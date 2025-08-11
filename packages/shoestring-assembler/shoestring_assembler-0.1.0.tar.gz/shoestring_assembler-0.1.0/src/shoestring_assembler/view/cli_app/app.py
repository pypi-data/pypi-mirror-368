from textual.app import App
from textual.binding import Binding
from shoestring_assembler.view.cli_app.screens.engine import CanContinue

import asyncio

from . import screens
from shoestring_assembler.interface.pipe import pipe

from shoestring_assembler.interface.state_machine import steps

from shoestring_assembler.interface.events.updates import FatalError
from shoestring_assembler.engine.engine import Engine


class SolutionAssemblerApp(App):
    BINDINGS = [
        Binding(
            "ctrl+q",
            "quit",
            "Quit",
            show=True,
            priority=True,
            key_display="ctrl+q",
        ),
        Binding(
            key="question_mark",
            action="toggle_help",
            description="Show/Hide help screen",
            key_display="?",
        ),
    ]
    ENABLE_COMMAND_PALETTE = False
    CSS_PATH = "layout.tcss"
    TITLE = "Shoestring Assembler"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui_pipe, engine_pipe = pipe.duplex()
        self.update_receiver, update_sender = pipe.simplex()
        self.engine = Engine(engine_pipe, update_sender)
        self.help_shown = False

    def on_mount(self):
        self.push_screen(screens.EngineScreen(self.update_receiver))
        self.engine_worker = self.run_worker(self.run_engine())
        self.monitor_worker = self.run_worker(self.monitor_engine())

    def action_toggle_help(self):
        if self.help_shown:
            self.action_hide_help_panel()
            self.help_shown = False
        else:
            self.action_show_help_panel()
            self.help_shown = True

    def screen_switcher(self, step: steps.UIStep, outcome_future: asyncio.Future):

        match (step):
            case steps.PresentCommands():
                screen = screens.Home(self.engine.installed_solutions.solutions)
            case steps.FindInstalledSolution():
                screen = screens.Find()
            case steps.ChooseSolution():
                screen = screens.SolutionPicker(step.provider_list)
            case steps.ChooseSolutionVersion():
                screen = screens.SolutionVersionPicker(step.version_list)
            case steps.ChooseDownloadLocation():
                screen = screens.DownloadLocation()
            case steps.PromptToAssemble():
                screen = screens.ConfirmModal(
                    prompt="Do you want to assemble the solution now?"
                )
            case steps.GetConfigurationInputs():
                screen = screens.ConfigInputs(self.engine.solution_model)
            case steps.PromptToBuild():
                screen = screens.ConfirmModal(
                    prompt="Do you want to build the solution now?"
                )
            case steps.PromptToStart():
                screen = screens.ConfirmModal(
                    prompt="Do you want to start the solution now?"
                )
            case steps.PauseStep():
                screen = None
                # send signal
                for screen in self.screen_stack:
                    screen.post_message(CanContinue(outcome_future))
            case steps.SelectUpdateVersion():
                screen = screens.UpdateVersionPicker(
                    self.engine.solution_model
                )
            case _:
                raise Exception(step)
                screen = None

        def get_result(result) -> None:
            """Called when screen is dismissed."""
            outcome_future.set_result(result)

        if screen:
            self.push_screen(screen, get_result)

    async def run_engine(self):
        await self.engine.run()

    async def monitor_engine(self):
        loop = asyncio.get_event_loop()
        try:
            outcome = None
            while True:
                next_ui_step = await self.engine.next(self.ui_pipe, outcome)
                # self.notify(str(type(next_ui_step)))

                outcome_future = loop.create_future()
                self.screen_switcher(next_ui_step, outcome_future)
                outcome = await outcome_future

        except FatalError as fatal_error:
            # display error modal and then quit
            self.push_screen(screens.FatalErrorModal(error_message=fatal_error.message))

        self.exit()
