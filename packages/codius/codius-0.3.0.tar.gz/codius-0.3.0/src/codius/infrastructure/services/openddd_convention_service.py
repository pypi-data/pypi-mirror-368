import re
from pathlib import Path

from codius.infrastructure.services.tree_sitter_service import TreeSitterService


class OpenDddConventionService:

    def __init__(self, tree_sitter_service: TreeSitterService):
        self.tree_sitter_service = tree_sitter_service

    def get_source_root(self) -> str:
        return "src/"

    def get_tests_path(self) -> str:
        return "src/Tests"

    def get_interchange_path(self) -> str:
        return "src/Interchange"

    def get_layer_path(self, layer: str) -> str:
        return f"src/{layer}"

    def get_namespace_base(self, project_dir: Path) -> str:
        return project_dir.resolve().name

    def get_aggregate_structure(self) -> str:
        return "Domain/{AggregateName}/{AggregateName}.cs"

    def get_aggregate_path(self, name: str) -> str:
        return f"src/Domain/{name}/{name}.cs"

    def get_namespace_for(self, layer: str, name: str, base: str) -> str:
        return f"{base}.{layer}.{name}"

    def format_class_code(self, code: str) -> str:
        source = self._strip_bom_if_present(code)
        source = self._normalize_line_endings(source)

        tree = self.tree_sitter_service.parse_code(source)
        root = tree.root_node

        # Find the class declaration and its members
        class_node = self._find_class_node(root)
        members = self._collect_class_members(class_node)

        # Compute base indent level for formatting
        class_indent_spaces = self._get_class_indent(class_node, source)

        # Apply individual formatting plan
        source = self._enforce_member_spacing(source, members)

        # Re-parse after modifying spacing to get fresh offsets
        tree = self.tree_sitter_service.parse_code(source)
        root = tree.root_node
        class_node = self._find_class_node(root)
        members = self._collect_class_members(class_node)

        source = self._reindent_members(source, members, class_indent_spaces)
        source = self._enforce_line_breaks_between_sections(source, members)
        source = self._trim_empty_lines(source, class_node, members)
        source = self._final_cleanup(source)

        return source

    def _strip_bom_if_present(self, code: str) -> str:
        return code.lstrip('\ufeff')

    def _normalize_line_endings(self, code: str) -> str:
        return code.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"

    def _find_class_node(self, root) -> object:
        def walk(node):
            if node.type == "class_declaration":
                return node
            for child in node.children:
                result = walk(child)
                if result:
                    return result
            return None

        return walk(root)

    def _collect_class_members(self, class_node) -> list:
        members = []

        def walk(node):
            if node.type in ("field_declaration", "property_declaration",
                             "method_declaration", "constructor_declaration"):
                members.append(node)
            for child in node.children:
                walk(child)

        walk(class_node)
        members.sort(key=lambda n: n.start_byte)
        return members

    def _get_class_indent(self, class_node, source: str) -> int:
        line_start = source.rfind("\n", 0, class_node.start_byte) + 1
        return class_node.start_byte - line_start

    def _enforce_member_spacing(self, source: str, members: list) -> str:
        chunks = []
        last_end = 0

        for member in members:
            pre = source[last_end:member.start_byte]
            pre = re.sub(r'\n{3,}', '\n\n', pre)
            chunks.append(pre.rstrip() + "\n\n")

            chunks.append(source[member.start_byte:member.end_byte].rstrip())
            last_end = member.end_byte

        remainder = source[last_end:]
        remainder = re.sub(r'\n{3,}', '\n\n', remainder)
        chunks.append(remainder)

        return ''.join(chunks)

    def _enforce_line_breaks_between_sections(self, source: str, members: list) -> str:
        # TODO: Add logic to detect switch from properties to methods and insert 2 blank lines between sections
        return source

    def _reindent_members(self, source: str, members: list, class_indent: int) -> str:
        out = []
        last_end = 0
        for member in members:
            out.append(source[last_end:member.start_byte])
            block = source[member.start_byte:member.end_byte]
            reindented = self._reindent_block(block, class_indent)
            out.append(reindented)
            last_end = member.end_byte
        out.append(source[last_end:])
        return ''.join(out)

    def _trim_empty_lines(self, source: str, class_node, members: list) -> str:
        lines = source.splitlines()
        start_line = class_node.start_point[0]
        end_line = class_node.end_point[0]

        # Remove blank lines before class declaration
        while start_line > 0 and lines[start_line - 1].strip() == "":
            lines.pop(start_line - 1)
            start_line -= 1
            end_line -= 1

        # Remove blank lines immediately after opening brace {
        for i in range(start_line, end_line):
            if lines[i].strip() == "{":
                next_line = i + 1
                while next_line < len(lines) and lines[next_line].strip() == "":
                    lines.pop(next_line)
                    end_line -= 1
                break

        # Remove blank lines before closing brace }
        for i in range(end_line, start_line, -1):
            if lines[i].strip() == "}":
                prev_line = i - 1
                while prev_line > start_line and lines[prev_line].strip() == "":
                    lines.pop(prev_line)
                    prev_line -= 1
                    end_line -= 1
                break

        # Remove blank lines after class closing brace
        for i in range(end_line, len(lines), 1):
            if lines[i].strip() == "}":
                next_line = i + 1
                while next_line < len(lines) and lines[next_line].strip() == "":
                    lines.pop(next_line)
                break

        return "\n".join(lines) + "\n"

    def _reindent_block(self, code: str, class_indent: int) -> str:
        lines = code.splitlines()

        member_indent_str = " " * (class_indent + 4)
        block_indent_str = " " * (class_indent + 8)

        result = []
        inside_block = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                result.append("")
            elif stripped == "{":
                result.append(member_indent_str + "{")
                inside_block = True
            elif stripped == "}":
                result.append(member_indent_str + "}")
                inside_block = False
            elif inside_block:
                result.append(block_indent_str + stripped)
            else:
                result.append(member_indent_str + stripped)

        return "\n".join(result)

    def _final_cleanup(self, source: str) -> str:
        source = re.sub(r'[ \t]+\n', '\n', source)  # Strip trailing whitespace
        source = re.sub(r'\n{3,}', '\n\n', source)  # Collapse multiple blank lines

        # Ensure exactly one blank line between using directives and namespace
        source = re.sub(
            r'((?:using [^\n]+;\n)+)\s*(namespace\b)',
            r'\1\n\2',
            source,
            flags=re.MULTILINE
        )

        return source.rstrip() + "\n"  # Ensure exactly one newline at EOF
