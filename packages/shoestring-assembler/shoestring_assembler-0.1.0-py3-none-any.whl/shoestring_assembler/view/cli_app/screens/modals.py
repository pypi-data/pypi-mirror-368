from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class ConfirmModal(ModalScreen):
    CSS_PATH = "modals.tcss"

    """Screen to confirm something"""
    def __init__(self, *args, prompt="Continue?", **kwargs):
        super().__init__(*args, classes="modal_screen", **kwargs)
        self.prompt = prompt

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.prompt, id="prompt"),
            Button("Yes", variant="success", id="yes"),
            Button("No", variant="error", id="no"),
            classes="modal_dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

class FatalErrorModal(ModalScreen):
    CSS_PATH = "modals.tcss"
    def __init__(self, *args, error_message="FATAL Error", **kwargs):
        super().__init__(*args, classes="modal_screen", **kwargs)
        self.error_message = error_message

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.error_message, id="prompt"),
            Button("Exit", variant="error", id="exit"),
            classes="modal_dialog",
        )

    @on(Button.Pressed, "#exit") 
    def handle_exit(self) -> None:
        self.app.exit()

