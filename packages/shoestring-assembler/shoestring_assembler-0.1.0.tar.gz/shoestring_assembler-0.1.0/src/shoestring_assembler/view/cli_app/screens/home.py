from textual import on
from textual.screen import Screen
from textual.widgets import Button, Markdown, Header, Collapsible, Static, Label, Footer
from textual.containers import Container, HorizontalGroup, VerticalScroll, Middle
from shoestring_assembler.model.installed import InstalledSolutionsModel
from shoestring_assembler.model.solution import SolutionModel
from shoestring_assembler.interface.signals import Action,ActionSignal
from textual.message import Message

INSTRUCTIONS = """
## Welcome to the Shoestring Assembler
"""

class SolutionAction(Message):
    """Action selected message."""
    def __init__(self, signal: ActionSignal) -> None:
        self.signal = signal
        super().__init__()

class Home(Screen):
    CSS_PATH = "home.tcss"
    SUB_TITLE = "Select an Action"

    def __init__(self, installed_solutions: list[SolutionModel]) -> None:
        super().__init__()
        self.solution_list = installed_solutions

    def compose(self):
        yield Header()
        yield Markdown(INSTRUCTIONS)
        with HorizontalGroup(id="download_bar"):
            with Middle():
                yield Label("Add a new Solution:")
            yield Button("Download", id="download")
            yield Button("Find", id="find",tooltip="Find a solution that is already installed")
        with VerticalScroll(can_focus=False):
            for solution in self.solution_list:
                with Collapsible(
                    title=(
                        solution.solution_details.name
                        if solution.solution_details
                        else "Unknown"
                    )
                ):
                    yield SolutionEntry(solution, classes = "solution_action_dropdown")
        yield Footer()

    @on(Button.Pressed, "#find")
    def select_download(self):
        self.dismiss(ActionSignal(Action.DOWNLOAD))

    @on(Button.Pressed, "#filesystem")
    def select_find(self):
        self.dismiss(ActionSignal(Action.FIND))

    @on(SolutionAction)
    def handle_solution_action(self,action:SolutionAction):
        self.dismiss(action.signal)


class SolutionEntry(Container):
    def __init__(self, solution:SolutionModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.solution = solution

    def compose(self):
        yield Label(f"version {self.solution.solution_details.version if self.solution.solution_details else '<unknown>'}")
        with HorizontalGroup():
            yield Button("Assemble", id="assemble")
            yield Button("Check for updates", id="update")
            yield Button("Reconfigure", id="reconfigure")
        with HorizontalGroup():
            yield Button("Build", id="build")
            yield Button("Setup", id="setup")
        with HorizontalGroup():
            yield Button("Start", id="start")
            yield Button("Restart", id="restart")
            yield Button("Stop", id="stop")

    @on(Button.Pressed)
    def handle_button_press(self,message:Button.Pressed):
        button_id = message.button.id
        match button_id:
            case "assemble":
                action = Action.ASSEMBLE
            case "update":
                action = Action.UPDATE
            case "reconfigure":
                action = Action.RECONFIGURE
            case "build":
                action = Action.BUILD
            case "setup":
                action = Action.SETUP
            case "start":
                action = Action.START
            case "restart":
                action = Action.RESTART
            case "stop":
                action = Action.STOP

        self.post_message(SolutionAction(ActionSignal(action,self.solution)))
