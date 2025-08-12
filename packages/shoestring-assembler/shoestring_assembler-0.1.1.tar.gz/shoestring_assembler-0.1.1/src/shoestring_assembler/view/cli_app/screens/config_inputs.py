from textual import on
from textual.screen import Screen
from textual.widgets import (
    Button,
    Markdown,
    Header,
    OptionList,
    Input,
    Label,
    TabbedContent,
    TabPane,
    Footer,
    Select
)
from textual.containers import (
    Container,
    HorizontalGroup,
    VerticalScroll,
    Middle,
    VerticalGroup,
)
from shoestring_assembler.model.solution import SolutionModel
from shoestring_assembler.model.base_module import BaseModule
from shoestring_assembler.interface.signals import Action, ActionSignal, BackSignal
from shoestring_assembler.model.user_config import UserConfig
from textual.message import Message
from textual.events import Blur,DescendantBlur
from shoestring_assembler.display import Display
from shoestring_assembler.interface.events.audit import Audit

from textual.reactive import reactive

INSTRUCTIONS = """
## Configure the solution
* Configure the solution by filling in the questions in each tab below
* Click continue when you're finished
"""


class SolutionAction(Message):
    """Action selected message."""

    def __init__(self, signal: ActionSignal) -> None:
        self.signal = signal
        super().__init__()


class ConfigInputs(Screen):
    CSS_PATH = "config.tcss"
    SUB_TITLE = "Configure Solution"
    AUTO_FOCUS = ""

    def __init__(self, solution_model: SolutionModel) -> None:
        super().__init__()
        self.solution_model = solution_model

    def compose(self):
        yield Header()
        with HorizontalGroup():
            yield Markdown(INSTRUCTIONS, id="instructions")
            with Container(id="button_container"):
                yield Button("Back to Menu", id="back")
                yield Button("Continue", variant="success", id="continue")
        with TabbedContent():
            for service_module in self.solution_model.service_modules:
                with TabPane(id=service_module.name, title=service_module.name):
                    yield ServiceModuleEntry(
                        service_module,
                        classes="module_entry",
                        can_focus = False
                    )
        yield Footer()

    @on(Button.Pressed, "#continue")
    def select_download(self):
        self.dismiss("continue")

    @on(Button.Pressed, "#back")
    def select_find(self):
        self.dismiss(BackSignal)


class ServiceModuleEntry(VerticalScroll):
    refresh_flag = reactive(bool, recompose=True)

    def __init__(self, service_module: BaseModule, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_module = service_module
        self.last_changed = None

    def compose(self):
        name = self.service_module.name
        user_config = self.service_module.user_config
        status = user_config.status

        if status == UserConfig.Status.WARN_FUTURE:
            # TODO
            # Display.print_warning(
            #     f"Current user config version is {user_config.version} which is newer than the template version of {user_config.template.version}.\n"
            #     + f"[red]This might be ok! [/red] - but it should be checked!\n"
            #     + f"You can find the current user config files at [purple]./{user_config.rel_path}[/purple] and the template files at [purple]./{user_config.template.rel_path}[/purple]"
            # )
            pass

        self.border_title = f"\[{status}]"
        if status == UserConfig.Status.NO_TEMPLATE:
            yield Label("No user config for this service module")
            return

        user_config.requires_configuration = True
        prompt_list = user_config.template.prompts

        if prompt_list is None:
            yield Label("No user config prompts for this service module")
            return

        Display.print_debug(f"COMPOSE")
        prompt_list = [*prompt_list]
        while len(prompt_list) > 0:
            prompt = prompt_list.pop(0)
            Display.print_debug(f">> {prompt}")
            Display.print_debug(f"<> {prompt_list}")
            Display.print_debug(f"!! {user_config.answers}")
            key = prompt.get("key")
            answer_key = prompt.get("answer_key", key)

            if "option" in prompt:
                options = prompt["option"]
                default_index = user_config.prompt_defaults.get(answer_key)
                answer_index = user_config.answers.get(answer_key)
                real_index = (
                    answer_index - 1
                    if answer_index
                    else default_index - 1 if default_index else 0
                )

                yield OptionPrompt(
                    answer_key=answer_key,
                    prompt=prompt["text"],
                    choices=[option["prompt"] for option in options],
                    selected=real_index,
                )

                if real_index is not None:
                    if "target" in options[real_index]:
                        target_prompts = options[real_index]["target"]
                        prompt_list = [*target_prompts, *prompt_list]
                    elif "value" in options[real_index]:
                        selected_value = options[real_index]["value"]
                        user_config.context[key] = selected_value
            elif "value" in prompt:
                user_config.context[key] = prompt.get("value")
            else:
                default_value = user_config.prompt_defaults.get(answer_key)
                answer_value = user_config.answers.get(answer_key)
                real_value = (
                    answer_value
                    if answer_value
                    else default_value if default_value else None
                )

                yield TextPrompt(
                    answer_key=answer_key,
                    prompt=prompt["text"],
                    value=real_value,
                )

                if real_value is not None:
                    user_config.context[key] = real_value

    def fix_focus(self):
        if self.last_changed:
            should_have_focus = self.query_one(f"#{self.last_changed}")
            should_have_focus.focus()

    @on(Button.Pressed, "#assemble")
    def select_download(self, message):
        self.post_message(SolutionAction(ActionSignal(Action.ASSEMBLE, self.solution)))

    # @on(OptionList.OptionSelected)
    # def handle_option_select(self, message: OptionList.OptionSelected):
    #     answer_key = message.option_list.id
    #     value = message.option_index + 1
    #     self.service_module.user_config.answers[answer_key] = value

    #     Audit.submit("select_option", Audit.Type.Expected, key=answer_key, value=value)
    #     self.last_changed = answer_key
    #     self.refresh_flag = not self.refresh_flag
    #     self.call_after_refresh(self.fix_focus)

    @on(Select.Changed)
    def handle_option_select(self, message: Select.Changed):
        answer_key = message.select.id
        value = message.value + 1
        if value != self.service_module.user_config.answers.get(answer_key):
            self.service_module.user_config.answers[answer_key] = value

            Audit.submit("select_option", Audit.Type.Expected, key=answer_key, value=value)
            self.last_changed = answer_key
            self.refresh_flag = not self.refresh_flag
            self.call_after_refresh(self.fix_focus)

    @on(Input.Blurred)
    def handle_text_input(self, message: Input.Changed):
        answer_key = message.input.id
        value = message.value
        self.service_module.user_config.answers[answer_key] = value

        Audit.submit("text_input", Audit.Type.Expected, key=answer_key, value=value)
        self.last_changed = answer_key


# class OptionPrompt(VerticalGroup):

#     refresh_flag = reactive(bool, recompose=True)

#     def __init__(
#         self,
#         *children,
#         prompt="",
#         choices=[],
#         selected=None,
#         answer_key=None,
#         name=None,
#         id=None,
#         classes=None,
#         disabled=False,
#         markup=True,
#     ):
#         super().__init__(
#             *children,
#             name=name,
#             id=id,
#             classes=classes,
#             disabled=disabled,
#             markup=markup,
#         )
#         self.prompt = prompt
#         self.choices = choices
#         self.selected = selected
#         self.answer_key = answer_key

#     def compose(self):
#         yield Label(self.prompt)
#         list = OptionList(*self.choices, id=self.answer_key)
#         if self.selected:
#             list.highlighted = self.selected
#         yield list

#     @on(DescendantBlur)
#     def handle_focus_loss(self,widget):
#         self.refresh_flag = not self.refresh_flag


class OptionPrompt(VerticalGroup):

    refresh_flag = reactive(bool, recompose=True)

    def __init__(
        self,
        *children,
        prompt="",
        choices=[],
        selected=None,
        answer_key=None,
        name=None,
        id=None,
        classes=None,
        disabled=False,
        markup=True,
    ):
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )
        self.prompt = prompt
        self.choices = choices
        self.selected = selected
        self.answer_key = answer_key

    def compose(self):
        yield Label(self.prompt)
        list = Select([(choice,index) for index,choice in enumerate(self.choices)], id=self.answer_key, value=self.selected)
        # if self.selected:
        #     list.highlighted = self.selected
        yield list

    # @on(DescendantBlur)
    # def handle_focus_loss(self, widget):
    #     self.refresh_flag = not self.refresh_flag


class TextPrompt(VerticalGroup):

    def __init__(
        self,
        *children,
        prompt="",
        value=None,
        answer_key=None,
        name=None,
        id=None,
        classes=None,
        disabled=False,
        markup=True,
    ):
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
            markup=markup,
        )
        self.prompt = prompt
        self.value = value
        self.answer_key = answer_key

    def compose(self):
        yield Label(self.prompt)
        yield Input(value=self.value, id=self.answer_key)
