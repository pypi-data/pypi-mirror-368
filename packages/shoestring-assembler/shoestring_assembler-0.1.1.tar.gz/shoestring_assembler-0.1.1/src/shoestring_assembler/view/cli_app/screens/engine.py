from textual.app import ComposeResult
from textual.widgets import Footer, RichLog, Button, ProgressBar, Label
from textual.containers import (
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
    Center,
    Middle,
    Container
)
from textual import on
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel

import asyncio

from shoestring_assembler.display import Display
from rich.rule import Rule

from shoestring_assembler.interface.events.audit import Audit, AuditEvent
from shoestring_assembler.interface.events.progress import ProgressEvent, SectionEvent

from shoestring_assembler.interface.events.updates import Update
from textual.message import Message
from textual.binding import Binding


from shoestring_assembler.view.plain_cli.audit_events import audit_event_to_string


class CanContinue(Message):
    def __init__(self, future: asyncio.Future):
        super().__init__()
        self.future = future


class EngineScreen(Screen):
    CSS_PATH = "engine.tcss"

    BINDINGS = {
        Binding(
            key="l",
            action="toggle_show_log",
            description="Show/Hide detailed logs",
            key_display="l",
        ),
    }

    def action_toggle_show_log(self):
        self.query_one(LogSection).toggle_show()

    def __init__(self, update_receiver, name=None, id=None, classes=None):
        super().__init__(name, id, classes)
        self.update_receiver = update_receiver
        self.continue_future = None

    def compose(self) -> ComposeResult:
        with Container(id="main_wrapper"):
            yield StageLog()
            yield LogSection()
        yield ContinueButtonWrapper()
        yield Footer()

    def _on_mount(self, event):
        self.run_worker(self.update_listener())

    def trigger_audit_msg(self, audit_event: AuditEvent):
        self.write_audit_msg(audit_event)

    def write_audit_msg(self, audit_event):
        content = audit_event_to_string(audit_event)
        match audit_event.type:
            case Audit.Type.Expected:
                Display.print_log(content)
            case Audit.Type.Unexpected:
                Display.print_error(content)
            case Audit.Type.Log:
                Display.print_debug(content)

    def notify_fn(self, msg: Update.Event):
        stage_log: StageLog = self.query_one(StageLog)
        match (msg.type):
            case Update.Type.STAGE:
                stage_log.add_update(msg)
                Display.print_top_header(msg.content)

            case Update.Type.STEP:
                stage_log.add_update(msg)
                Display.print_header(msg.content)

            case Update.Type.INFO:
                Display.print_log(msg.content, log_level=msg.lod)

            case Update.Type.WARNING:
                Display.print_warning(msg.content)

            case Update.Type.ERROR:
                Display.print_error(msg.content)

            case Update.Type.SUCCESS:
                stage_log.add_update(msg)
                Display.print_complete(msg.content)

            case Update.Type.DEBUG:
                Display.print_debug(msg.content)

            case Update.Type.ATTENTION:
                Display.print_notification(msg.content)

            case _:
                Display.print_log(msg)

    def create_progress_section(self, msg: SectionEvent):
        stage_log: StageLog = self.query_one(StageLog)
        stage_log.handle_progress_section(msg)

    def diplay_progress_update(self, progress_event):
        stage_log: StageLog = self.query_one(StageLog)
        stage_log.handle_progress_update(progress_event)

    async def update_listener(self):
        while True:
            msg = await self.update_receiver.recv()
            match msg:
                case AuditEvent():
                    self.trigger_audit_msg(msg)
                case ProgressEvent():
                    self.diplay_progress_update(msg)
                case Update.Event():
                    self.notify_fn(msg)
                case SectionEvent():
                    self.create_progress_section(msg)
                case _:
                    raise Exception(msg)

    @on(CanContinue)
    def handle_can_contiue(self, msg: CanContinue):
        wrapper: ContinueButtonWrapper = self.query_one(ContinueButtonWrapper)
        wrapper.ready_to_continue = True
        self.continue_future = msg.future

    @on(Button.Pressed, "#continue")
    def handle_continue(self):
        self.continue_future.set_result("continue")
        wrapper: ContinueButtonWrapper = self.query_one(ContinueButtonWrapper)
        wrapper.ready_to_continue = False


class RichLogConsoleWrapper:
    def __init__(self, rich_log):
        self.rich_log = rich_log

    def print(self, msg):
        self.rich_log.write(msg)

    def rule(self, *args, **kwargs):
        rule = Rule(*args, **kwargs)
        self.print(rule)


class ContinueButtonWrapper(HorizontalGroup):
    ready_to_continue = reactive(False, recompose=True)

    def compose(self):
        yield Button("Continue", variant="success", id="continue", disabled=not self.ready_to_continue)


class StageLog(Container):
    contents = reactive({}, recompose=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_counter = 0

    def compose(self):
        yield Label("Progress:", id="progress_label")
        with VerticalScroll() as scroll:
            for key, entry in self.contents.items():
                match entry:
                    case ProgressEvent():
                        with HorizontalGroup(classes="progress_group"):
                            yield Label(entry.label)
                            bar = ProgressBar(
                                id=entry.key, total=entry.total, show_eta=False
                            )
                            bar.progress = entry.value
                            yield bar
                    case Update.Event():
                        match entry.type:
                            case Update.Type.STAGE:
                                yield Label(
                                    f"{entry.content}", classes="stage_header"
                                )
                            case Update.Type.STEP:
                                yield Label(
                                    f"- {entry.content}", classes="step_header"
                                )
                            case Update.Type.SUCCESS:
                                yield Label(
                                    Text.from_markup(
                                        f":white_check_mark:  {entry.content}",
                                        style="green",
                                    )
                                )

        # self.call_after_refresh(self.set_progress)
        scroll.scroll_end()

    def handle_progress_section(self, msg: SectionEvent):
        pass

    def set_progress(self):
        for bar_id, entry in self.contents.items():
            if not isinstance(entry, ProgressEvent):
                continue
            try:
                bar: ProgressBar = self.query_one(f"#{bar_id}")
                bar.progress = entry.value
            except:
                pass

    def handle_progress_update(self, event: ProgressEvent):
        self.contents[event.key] = event
        self.mutate_reactive(StageLog.contents)

    def add_update(self, event):
        self.contents[f"{self.id_counter}"] = event
        self.id_counter += 1
        self.mutate_reactive(StageLog.contents)


class LogSection(VerticalGroup):
    shown = reactive(False, recompose=False)

    def compose(self):
        yield Label(
            "Detailed Log:",
            id="detailed_log_label",
            classes="shown" if self.shown else "hidden",
        )
        log = RichLog(wrap=True, classes="shown" if self.shown else "hidden")
        yield log
        wrapped_console = RichLogConsoleWrapper(log)
        Display.alt_console = wrapped_console

    @on(Button.Pressed, "#do_show")
    def toggle_show(self):
        self.shown = not self.shown

        label = self.query_one("#detailed_log_label")
        label.classes = "shown" if self.shown else "hidden"

        log = self.query_one(RichLog)
        log.classes = "shown" if self.shown else "hidden"

        if self.shown:
            self.remove_class("no_border")
            self.add_class("border")
        else:
            self.remove_class("border")
            self.add_class("no_border")
