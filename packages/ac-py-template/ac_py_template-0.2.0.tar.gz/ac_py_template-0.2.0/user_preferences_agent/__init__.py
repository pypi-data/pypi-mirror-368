# user_preferences_agent/__init__.py
import asyncio
import logging
import pathlib
import re
import textwrap
import typing

import agents
import jinja2
import openai
import pydantic
import rich.console
import rich.panel
import rich.text
import universal_message as um
from google_language_support import LanguageCodes
from openai.types import ChatModel
from openai_usage import Usage
from rich_color_support import RichColorRotator

from user_preferences_agent._currency import CurrencyCode
from user_preferences_agent._timezone import TimezoneCode

__version__ = pathlib.Path(__file__).parent.joinpath("VERSION").read_text().strip()

logger = logging.getLogger(__name__)
console = rich.console.Console()
color_rotator = RichColorRotator()

DEFAULT_MODEL = "gpt-4.1-nano"

SUPPORTED_MODEL_TYPES: typing.TypeAlias = (
    agents.OpenAIChatCompletionsModel | agents.OpenAIResponsesModel | ChatModel | str
)


class UserPreferences(pydantic.BaseModel):
    """Represents all user-configurable preferences."""

    # --- General & Localization Settings ---
    language: LanguageCodes | None = pydantic.Field(
        default=None,
        description="The language the user prefers to use for the interface and responses.",  # noqa: E501
    )

    timezone: TimezoneCode | None = pydantic.Field(
        default=None,
        description="The timezone the user is currently in for accurate time-sensitive information.",  # noqa: E501
    )

    currency: CurrencyCode | None = pydantic.Field(
        default=None,
        description="The currency ISO 4217 code the user prefers for financial information.",  # noqa: E501
    )

    country: str | None = pydantic.Field(
        default=None,
        description="The country the user is located in, for regional context.",  # noqa: E501
    )

    city: str | None = pydantic.Field(
        default=None,
        description="The city the user is located in, for more specific local context.",  # noqa: E501
    )

    # --- AI Memory & Core Instructions ---
    rules_and_memories: typing.List[str] = pydantic.Field(
        default_factory=list,
        description="A list of standing rules, facts, and memories for the AI to follow.",  # noqa: E501
    )

    def merge(self, other: "UserPreferences") -> typing.Self:
        self.language = other.language or self.language
        self.timezone = other.timezone or self.timezone
        self.currency = other.currency or self.currency
        self.country = other.country or self.country
        self.city = other.city or self.city
        self.rules_and_memories.extend(other.rules_and_memories)
        return self

    def pretty_print(self, console: rich.console.Console = console) -> None:
        console.print(
            rich.panel.Panel(
                self.model_dump_json(indent=4),
                title="User Preferences",
            )
        )


class UserPreferencesAgent:
    instructions_analyze_language_j2: str = textwrap.dedent(
        """
        ## Role Instructions

        You are a User Experience Analyst.
        You will be given a chat history between a user and a customer service agent.
        Your task is to analyze the chat history and identify the user's preferred language.
        The user's preferred language must be one of the reference languages.
        Output the preferred language in the format [Language Name](#language_code).
        The reference ISO 639-1 language codes are: {{ language_codes }}.

        ## Examples

        ### Example 1

        user:
        Hello, I'm John Doe.

        assistant:
        Hello, John Doe. How can I help you today?

        user:
        I'm looking for a new phone.

        assistant:
        Sure, I can help you with that.

        analysis:
        language: [English](#en)  # done

        ### Example 2

        user:
        I want to know the weather in Tokyo.

        assistant:
        The weather in Tokyo is sunny.

        user:
        Could you speak in Japanese?

        assistant:
        OK, I will speak in Japanese next time.

        analysis:
        language: [Japanese](#ja)  # done

        ## Input Chat History

        {{ messages_instructions }}

        analysis:
        language:
        """  # noqa: E501
    ).strip()

    instructions_rules_and_memories_j2: str = textwrap.dedent(
        """
        ## Role Instructions

        You are a User Experience Analyst.
        You will be given a chat history between a user and a customer service agent.
        Your task is to read a chat history and extract specific rules, facts, or memories stated by the USER only.
        Focus only on what the user says, ignore assistant responses when extracting rules.

        ## Abstractive Proposition Segmentation (APS)

        Each extracted rule or memory MUST follow Abstractive Proposition Segmentation (APS) principles.
        APS is an analysis technique that breaks down text information into component parts.
        This means each rule should be a single, atomic proposition that captures one specific piece of information.

        ## Output Format Rules

        - Each extracted piece of information MUST be on a new line.
        - Each line MUST begin with the prefix `rule: `.
        - Extract the information as a concise statement following APS principles.
        - Each rule should contain only one atomic proposition or fact.
        - If you find NO rules, facts, or memories, you MUST output exactly `rule: None`.
        - Do NOT include conversational filler, greetings, or your own explanations.
        - Only extract information from USER messages, not assistant responses.

        ## Examples

        ### Example 1

        user:
        My name is Alex.

        assistant:
        Nice to meet you, Alex.

        user:
        And my favorite color is blue.

        analysis:
        rule: The user's name is Alex.
        rule: The user's favorite color is blue.
        [DONE]

        ### Example 2

        user:
        Please always respond in Spanish.

        assistant:
        Entendido. Responderé en español a partir de ahora.

        analysis:
        rule: The user wants responses in Spanish.
        [DONE]

        ### Example 3

        user:
        Can you tell me the weather?

        assistant:
        Of course. Where do you live?

        user:
        I'm in London.

        analysis:
        rule: The user is in London.
        [DONE]

        ### Example 4

        user:
        Hello!

        assistant:
        Hi there! How can I help?

        analysis:
        rule: None
        [DONE]

        ## Input Chat History

        {{ messages_instructions }}

        analysis:
        """  # noqa: E501
    ).strip()

    async def analyze_language(
        self,
        messages: list[um.SUPPORTED_MESSAGE_TYPES] | list[um.Message],
        *,
        model: typing.Optional[SUPPORTED_MODEL_TYPES] = None,
        tracing_disabled: bool = True,
        verbose: bool = False,
        console: rich.console.Console = console,
        color_rotator: RichColorRotator = color_rotator,
        width: int = 80,
        **kwargs,
    ) -> "UserPreferencesResult":
        msgs = [um.Message.from_any(msg) for msg in messages]
        chat_model = self._to_chat_model(model)

        agent_instructions_template = jinja2.Template(
            self.instructions_analyze_language_j2
        )
        user_input = agent_instructions_template.render(
            language_codes=", ".join(lang.value for lang in LanguageCodes),
            messages_instructions=um.messages_to_instructions(msgs),
        )

        if verbose:
            __rich_panel = rich.panel.Panel(
                rich.text.Text(user_input),
                title="LLM INSTRUCTIONS",
                border_style=color_rotator.pick(),
                width=width,
            )
            console.print(__rich_panel)

        agent = agents.Agent(
            name="user-preferences-agent-analyze-language",
            model=chat_model,
            model_settings=agents.ModelSettings(temperature=0.0),
        )
        result = await agents.Runner.run(
            agent,
            user_input,
            run_config=agents.RunConfig(tracing_disabled=tracing_disabled),
        )
        usage = Usage.from_openai(result.context_wrapper.usage)
        usage.model = chat_model.model
        usage.cost = usage.estimate_cost(usage.model)

        if verbose:
            __rich_panel = rich.panel.Panel(
                rich.text.Text(str(result.final_output)),
                title="LLM OUTPUT",
                border_style=color_rotator.pick(),
                width=width,
            )
            console.print(__rich_panel)
            __rich_panel = rich.panel.Panel(
                rich.text.Text(usage.model_dump_json(indent=4)),
                title="LLM USAGE",
                border_style=color_rotator.pick(),
                width=width,
            )
            console.print(__rich_panel)

        return UserPreferencesResult(
            input_messages=msgs,
            user_preferences=self._parse_user_preferences_language(
                str(result.final_output)
            ),
            usages=[usage],
        )

    async def analyze_rules_and_memories(
        self,
        messages: list[um.SUPPORTED_MESSAGE_TYPES] | list[um.Message],
        *,
        model: typing.Optional[SUPPORTED_MODEL_TYPES] = None,
        tracing_disabled: bool = True,
        verbose: bool = False,
        console: rich.console.Console = console,
        color_rotator: RichColorRotator = color_rotator,
        width: int = 80,
        **kwargs,
    ) -> "UserPreferencesResult":
        msgs = [um.Message.from_any(msg) for msg in messages]
        chat_model = self._to_chat_model(model)

        agent_instructions_template = jinja2.Template(
            self.instructions_rules_and_memories_j2
        )
        user_input = agent_instructions_template.render(
            messages_instructions=um.messages_to_instructions(msgs),
        )

        if verbose:
            __rich_panel = rich.panel.Panel(
                rich.text.Text(user_input),
                title="LLM INSTRUCTIONS",
                border_style=color_rotator.pick(),
                width=width,
            )
            console.print(__rich_panel)

        agent = agents.Agent(
            name="user-preferences-agent-rules-and-memories",
            model=chat_model,
            model_settings=agents.ModelSettings(temperature=0.0),
        )
        result = await agents.Runner.run(
            agent,
            user_input,
            run_config=agents.RunConfig(tracing_disabled=tracing_disabled),
        )
        usage = Usage.from_openai(result.context_wrapper.usage)
        usage.model = chat_model.model
        usage.cost = usage.estimate_cost(usage.model)

        if verbose:
            __rich_panel = rich.panel.Panel(
                rich.text.Text(str(result.final_output)),
                title="LLM OUTPUT",
                border_style=color_rotator.pick(),
                width=width,
            )
            console.print(__rich_panel)
            __rich_panel = rich.panel.Panel(
                rich.text.Text(usage.model_dump_json(indent=4)),
                title="LLM USAGE",
                border_style=color_rotator.pick(),
                width=width,
            )
            console.print(__rich_panel)

        return UserPreferencesResult(
            input_messages=msgs,
            user_preferences=self._parse_user_preferences_rules_and_memories(
                str(result.final_output)
            ),
            usages=[usage],
        )

    async def run(
        self,
        messages: list[um.SUPPORTED_MESSAGE_TYPES] | list[um.Message],
        *,
        model: typing.Optional[SUPPORTED_MODEL_TYPES] = None,
        tracing_disabled: bool = True,
        verbose: bool = False,
        console: rich.console.Console = console,
        color_rotator: RichColorRotator = color_rotator,
        width: int = 80,
        **kwargs,
    ) -> "UserPreferencesResult":
        msgs = [um.Message.from_any(msg) for msg in messages]
        chat_model = self._to_chat_model(model)

        results = await asyncio.gather(
            self.analyze_language(
                msgs,
                model=chat_model,
                tracing_disabled=tracing_disabled,
                verbose=verbose,
                console=console,
                color_rotator=color_rotator,
                width=width,
                **kwargs,
            ),
            self.analyze_rules_and_memories(
                msgs,
                model=chat_model,
                tracing_disabled=tracing_disabled,
                verbose=verbose,
                console=console,
                color_rotator=color_rotator,
                width=width,
                **kwargs,
            ),
        )

        # Merge the results into a single UserPreferences object
        usages = []
        user_preferences = UserPreferences()
        for result in results:
            user_preferences = user_preferences.merge(result.user_preferences)
            usages.extend(result.usages)

        return UserPreferencesResult(
            input_messages=msgs,
            user_preferences=user_preferences,
            usages=usages,
        )

    def _parse_user_preferences_language(
        self,
        text: str,
    ) -> UserPreferences:
        pattern = re.compile(
            r"\[([^\]]+)\]\s*\(\s*#\s*([^)]+?)\s*\)", flags=re.IGNORECASE
        )
        for m in pattern.finditer(text):
            lang_expr = m.group(1)
            lang_code_str = m.group(2)
            break
        else:
            logger.error(f"No language expression found in the text: {text}")
            lang_expr = None
            lang_code_str = None

        if lang_code_str is not None:
            try:
                language = LanguageCodes.from_might_common_name(lang_code_str)
            except ValueError:
                logger.error(f"Invalid language expression: {lang_code_str}")
                language = None

        if language is None and lang_expr is not None:
            logger.info(f"Trying to parse language expression: {lang_expr}")
            try:
                language = LanguageCodes.from_might_common_name(lang_expr)
            except ValueError:
                logger.error(f"Failed to parse language expression: {lang_expr}")
                language = None

        return UserPreferences(language=language)

    def _parse_user_preferences_rules_and_memories(
        self,
        text: str,
    ) -> UserPreferences:
        pattern = re.compile(r"^rule:\s*(.+)", re.MULTILINE | re.IGNORECASE)
        matches = pattern.findall(text)

        if len(matches) == 1 and matches[0].strip().lower() in ("none", "null"):
            return UserPreferences(rules_and_memories=[])

        rules_and_memories = [match.strip() for match in matches]
        return UserPreferences(rules_and_memories=rules_and_memories)

    def _to_chat_model(
        self,
        model: (
            agents.OpenAIChatCompletionsModel
            | agents.OpenAIResponsesModel
            | ChatModel
            | str
            | None
        ) = None,
    ) -> agents.OpenAIChatCompletionsModel | agents.OpenAIResponsesModel:
        model = DEFAULT_MODEL if model is None else model

        if isinstance(model, str):
            openai_client = openai.AsyncOpenAI()
            return agents.OpenAIResponsesModel(
                model=model,
                openai_client=openai_client,
            )

        else:
            return model


class UserPreferencesResult(pydantic.BaseModel):
    input_messages: typing.List[um.Message]
    user_preferences: UserPreferences
    usages: typing.List[Usage] = pydantic.Field(default_factory=list)
