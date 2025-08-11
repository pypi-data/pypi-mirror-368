import logging

from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from codius.infrastructure.services.openddd_convention_service import OpenDddConventionService
from codius.infrastructure.services.tree_sitter_service import TreeSitterService

logger = logging.getLogger(__name__)


class CodeGeneratorService:
    def __init__(self, convention_service: OpenDddConventionService, tree_sitter_service: TreeSitterService):
        self.convention_service = convention_service
        self.tree_sitter_service = tree_sitter_service
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
            autoescape=select_autoescape(disabled_extensions=("cs",)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def create_file(self, file_plan: dict, output_dir: Path, project_root: Path) -> Optional[dict]:
        template_name = file_plan.get("template")
        context = file_plan.get("context", {})
        relative_path = Path(file_plan["path"])

        try:
            template = self.jinja_env.get_template(f"{template_name}.cs.j2")
            rendered = template.render(**context)
            formatted = self.convention_service.format_class_code(rendered)

            file_path = output_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(formatted.strip(), encoding="utf-8")

            logger.debug("Generated file from template: %s", file_path)

            return {
                "path": str(relative_path),
                "content": formatted.strip()
            }

        except Exception as e:
            logger.error("Failed to generate file from template '%s': %s", template_name, e)
            raise

    def modify_file(
        self,
        path: str,
        steps: list[dict],
        output_dir: Path,
        project_root: Path,
        created_files_map: dict[str, str]
    ) -> Optional[dict]:
        relative_path = Path(path)
        relative_path_str = str(relative_path)

        if relative_path_str in created_files_map:
            current_code = created_files_map[relative_path_str]
        else:
            try:
                current_code = (project_root / relative_path).read_text(encoding="utf-8")
            except FileNotFoundError:
                logger.warning("Target file for modification not found: %s", path)
                raise

        for step in steps:
            context = step["context"]
            modification = step["modification"]

            if modification == "add_method":
                code = self._render_method_template(context)
                current_code = self._inject_method_ast_based(current_code, code,
                                                             context.get("placement"))
            elif modification == "add_property":
                code = self._render_property_template(context)
                current_code = self._inject_property_ast_based(current_code, code)
            else:
                raise Exception(f"Unsupported modification type: {modification}")

        file_path = output_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        formatted_code = self.convention_service.format_class_code(current_code)
        file_path.write_text(formatted_code.strip(), encoding="utf-8")

        return {
            "path": str(relative_path),
            "content": formatted_code.strip()
        }

    def _render_method_template(self, context: dict) -> str:
        method = context["method"]
        if "body" in method and method["body"].strip():
            params = ", ".join(f"{p['type']} {p['name']}" for p in method.get("parameters", []))
            returns = method.get("returns", "void")
            name = method["name"]
            body = method["body"].strip()
            return f"""public {returns} {name}({params})
{{
    {body}
}}"""
        template = self.jinja_env.get_template("domain/model/aggregate/aggregate_method.cs.j2")
        return template.render(**context)

    def _render_property_template(self, context: dict) -> str:
        prop = context["property"]
        type_ = prop["type"]
        name = prop["name"]
        default = prop.get("default")
        if default is not None:
            return f"public {type_} {name} {{ get; set; }} = {default};"
        else:
            return f"public {type_} {name} {{ get; set; }}"

    def _inject_method_ast_based(self, source_code: str, method_code: str, placement: Optional[dict]) -> str:
        tree = self.tree_sitter_service.parse_code(source_code)
        reference = placement.get("reference") if placement else None
        insert_pos = None

        def find_insertion_point(node):
            nonlocal insert_pos
            if node.type == "class_declaration":
                body_node = next((child for child in node.children if child.type == "declaration_list"), None)
                if not body_node:
                    return False

                reference_found = False
                last_method = None

                for child in body_node.children:
                    if child.type == "method_declaration":
                        name = self._extract_method_name(source_code, child)
                        if name == reference:
                            insert_pos = child.end_byte
                            reference_found = True
                            break
                        last_method = child

                if not reference_found:
                    insert_pos = last_method.end_byte if last_method else body_node.start_byte + 1
                return True

            for child in node.children:
                if find_insertion_point(child):
                    return True
            return False

        found = find_insertion_point(tree.root_node)
        if not found or insert_pos is None:
            logger.warning("Could not locate class or reference method. Appending at end of file.")
            return source_code + "\n\n" + method_code

        before = source_code[:insert_pos].rstrip()
        after = source_code[insert_pos:].lstrip()
        return before + "\n\n" + self._indent_block(method_code.strip()) + "\n    " + after

    def _inject_property_ast_based(self, source_code: str, property_code: str) -> str:
        tree = self.tree_sitter_service.parse_code(source_code)
        insert_pos = None
        class_indent = "    "

        def find_class_body(node):
            nonlocal insert_pos, class_indent
            if node.type == "class_declaration":
                line_start = source_code.rfind("\n", 0, node.start_byte) + 1
                class_indent = " " * (node.start_byte - line_start)

                body_node = next((c for c in node.children if c.type == "declaration_list"), None)
                if not body_node:
                    return False

                insert_pos = body_node.start_byte + 1
                return True

            for child in node.children:
                if find_class_body(child):
                    return True
            return False

        found = find_class_body(tree.root_node)
        if not found or insert_pos is None:
            logger.warning("Class declaration not found. Appending at end.")
            return source_code + "\n\n" + property_code

        before = source_code[:insert_pos].rstrip()
        after = source_code[insert_pos:].lstrip()
        indented = self._indent_block(property_code.strip(), spaces=len(class_indent.expandtabs()))
        return before + "\n" + class_indent + indented + "\n\n    " + after

    def _extract_method_name(self, source: str, node) -> str:
        for child in node.children:
            if child.type == "identifier":
                return source[child.start_byte:child.end_byte]
        return ""

    def _indent_block(self, code: str, spaces: int = 8) -> str:
        return "\n".join(" " * spaces + line if line.strip() else "" for line in code.splitlines())
