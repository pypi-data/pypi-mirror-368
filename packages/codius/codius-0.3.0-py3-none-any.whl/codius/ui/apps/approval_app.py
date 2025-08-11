from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style


def show_approval_app() -> str:
    choices = [
        ("apply", "✅ Yes, apply the changes"),
        ("abort", "❌ No, abort and discard the changes"),
        ("change", "✏️ No, let me tell you how to revise the changes")
    ]
    index = [0]  # Mutable container to allow updates

    def get_menu_text():
        lines = []
        for i, (_, label) in enumerate(choices):
            prefix = "❯ " if i == index[0] else "  "
            style = "class:selected" if i == index[0] else ""
            lines.append((style, f"{prefix}{label}\n"))
        return FormattedText(lines)

    kb = KeyBindings()

    @kb.add("up")
    def _up(event):
        index[0] = (index[0] - 1) % len(choices)

    @kb.add("down")
    def _down(event):
        index[0] = (index[0] + 1) % len(choices)

    @kb.add("enter")
    def _enter(event):
        event.app.exit(result=choices[index[0]][0])

    @kb.add("escape")
    @kb.add("q")
    def _cancel(event):
        event.app.exit(result="abort")

    app = Application(
        layout=Layout(HSplit([Window(content=FormattedTextControl(get_menu_text), always_hide_cursor=True)])),
        key_bindings=kb,
        style=Style.from_dict({"selected": "bold fg:green"}),
        full_screen=False,
    )

    return app.run()
