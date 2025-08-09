from __future__ import annotations

from typing import TypeVar, overload

from openai import BadRequestError, resources
from openai._types import NOT_GIVEN, NotGiven
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
    completion_create_params,
)
from openai.types.shared.reasoning_effort import ReasoningEffort
from pydantic import BaseModel

from typegpt_light.exceptions import LLMModelRefusal, LLMOutputTruncated

from ...prompt_definition.prompt_template import PromptTemplate
from ...utils.internal_types import _UseDefault, _UseDefaultType
from ..base_chat_completion import BaseChatCompletions
from ..exceptions import AzureContentFilterException
from ..views import AzureChatModel, OpenAIChatModel, UnsafeModel

# Prompt = TypeVar("Prompt", bound=PromptTemplate)
_Output = TypeVar("_Output", bound=BaseModel)


class AsyncTypeChatCompletion(resources.chat.AsyncCompletions, BaseChatCompletions):
    async def generate_completion(
        self,
        model: OpenAIChatModel | UnsafeModel | AzureChatModel,
        messages: list[ChatCompletionMessageParam],
        frequency_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: list[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: dict[str, int] | None | NotGiven = NOT_GIVEN,  # [-100, 100]
        max_tokens: int | NotGiven = 1000,
        n: int | None | NotGiven = NOT_GIVEN,
        presence_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        store: bool | None | NotGiven = NOT_GIVEN,
        seed: int | None | NotGiven = NOT_GIVEN,
        stop: str | list[str] | None | NotGiven = NOT_GIVEN,
        temperature: float | None | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: list[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_p: float | None | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        timeout: float | None | NotGiven = NOT_GIVEN,
    ) -> str:
        raw_model: OpenAIChatModel | str
        if isinstance(model, AzureChatModel):
            raw_model = model.deployment_id
            is_azure = True
        elif isinstance(model, UnsafeModel):
            raw_model = model.name
            is_azure = False
        else:
            raw_model = model
            is_azure = False

        try:
            result = await self.create(
                model=raw_model,
                messages=messages,
                frequency_penalty=frequency_penalty,
                function_call=function_call,
                functions=functions,
                logit_bias=logit_bias,
                max_tokens=max_tokens,
                n=n,
                presence_penalty=presence_penalty,
                response_format=response_format,
                store=store,
                seed=seed,
                stop=stop,
                stream=False,
                temperature=temperature,
                tool_choice=tool_choice,
                tools=tools,
                top_p=top_p,
                user=user,
                timeout=timeout,
            )

            if is_azure and result.choices[0].finish_reason == "content_filter":
                raise AzureContentFilterException(reason="completion")

            return result.choices[0].message.content or ""

        except BadRequestError as e:
            if is_azure and e.code == "content_filter":
                raise AzureContentFilterException(reason="prompt")
            elif (
                is_azure and "filtered due to the prompt triggering Azure OpenAI" in e.message
            ):  # temporary fix: OpenAI library doesn't correctly parse code into error object
                raise AzureContentFilterException(reason="prompt")
            else:
                raise e

    @overload
    async def generate_output(
        self,
        model: OpenAIChatModel | UnsafeModel | AzureChatModel,
        prompt: PromptTemplate,
        output_type: type[_Output],
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        max_completion_tokens: int | None | NotGiven = NOT_GIVEN,
        frequency_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        n: int | None | NotGiven = NOT_GIVEN,
        presence_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        temperature: float | NotGiven = NOT_GIVEN,
        seed: int | None | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        timeout: float | None | NotGiven = NOT_GIVEN,
        reasoning_effort: ReasoningEffort | NotGiven = NOT_GIVEN,
        retry_on_parse_error: int = 0,
    ) -> _Output: ...

    @overload
    async def generate_output(
        self,
        model: OpenAIChatModel | UnsafeModel | AzureChatModel,
        prompt: PromptTemplate,
        output_type: _UseDefaultType = _UseDefault,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        max_completion_tokens: int | None | NotGiven = NOT_GIVEN,
        frequency_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        n: int | None | NotGiven = NOT_GIVEN,
        presence_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        temperature: float | NotGiven = NOT_GIVEN,
        seed: int | None | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        timeout: float | None | NotGiven = NOT_GIVEN,
        reasoning_effort: ReasoningEffort | NotGiven = NOT_GIVEN,
        retry_on_parse_error: int = 0,
    ) -> BaseModel: ...

    async def generate_output(
        self,
        model: OpenAIChatModel | UnsafeModel | AzureChatModel,
        prompt: PromptTemplate,
        output_type: type[_Output] | _UseDefaultType = _UseDefault,
        max_tokens: int | None | NotGiven = NOT_GIVEN,
        max_completion_tokens: int | None | NotGiven = NOT_GIVEN,
        frequency_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        n: int | None | NotGiven = NOT_GIVEN,
        presence_penalty: float | None | NotGiven = NOT_GIVEN,  # [-2, 2]
        temperature: float | NotGiven = NOT_GIVEN,
        seed: int | None | NotGiven = NOT_GIVEN,
        top_p: float | NotGiven = NOT_GIVEN,
        timeout: float | None | NotGiven = NOT_GIVEN,
        reasoning_effort: ReasoningEffort | NotGiven = NOT_GIVEN,
        retry_on_parse_error: int = 0,
        store: bool | None | NotGiven = NOT_GIVEN,
    ) -> _Output | BaseModel:
        """
        Calls OpenAI Chat API, generates assistant response, and fits it into the output class

        :param model: model to use as `OpenAIChatModel` or `AzureChatModel`
        :param prompt: prompt, which is a subclass of `PromptTemplate`
        :param max_tokens: maximum number of tokens for non-reasoning models
        :param max_completion_tokens: maximum number of tokens for reasoning models
        :param output_type: output class used to parse the response, subclass of `BaseLLMResponse`. If not specified, the output defined in the prompt is used
        :param request_timeout: timeout for the request in seconds
        :param retry_on_parse_error: number of retries if the response cannot be parsed (i.e. any `LLMParseException`). If set to 0, it has no effect.
        :param config: additional OpenAI/Azure config if needed (e.g. no global api key)
        """

        raw_model: OpenAIChatModel | str
        if isinstance(model, AzureChatModel):
            raw_model = model.deployment_id
            is_azure = True
        elif isinstance(model, UnsafeModel):
            raw_model = model.name
            is_azure = False
        else:
            raw_model = model
            is_azure = False

        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": prompt.system_prompt()},
            self._generate_user_message(prompt.user_prompt()),
        ]

        if isinstance(output_type, _UseDefaultType):
            result = await self._client.beta.chat.completions.parse(
                model=raw_model,
                messages=messages,
                max_tokens=max_tokens,
                max_completion_tokens=max_completion_tokens,
                frequency_penalty=frequency_penalty,
                n=n,
                presence_penalty=presence_penalty,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                timeout=timeout,
                reasoning_effort=reasoning_effort,
                store=store,
                response_format=prompt.Output,
            )
        else:
            result = await self._client.beta.chat.completions.parse(
                model=raw_model,
                messages=messages,
                max_tokens=max_tokens,
                max_completion_tokens=max_completion_tokens,
                frequency_penalty=frequency_penalty,
                n=n,
                presence_penalty=presence_penalty,
                temperature=temperature,
                seed=seed,
                top_p=top_p,
                timeout=timeout,
                reasoning_effort=reasoning_effort,
                store=store,
                response_format=output_type,
            )

        if is_azure and result.choices[0].finish_reason == "content_filter":
            raise AzureContentFilterException(reason="completion")

        if result.choices[0].finish_reason == "length":
            raise LLMOutputTruncated(
                "Output length exceeds the limit",
                system_prompt=prompt.system_prompt(),
                user_prompt=prompt.user_prompt(),
                raw_completion=result.choices[0].message.content,
            )

        if result.choices[0].message.refusal:
            raise LLMModelRefusal(
                f"Model refused to generate the output: {result.choices[0].message.refusal}",
                system_prompt=prompt.system_prompt(),
                user_prompt=prompt.user_prompt(),
                raw_completion=result.choices[0].message.content,
            )

        parsed_output = result.choices[0].message.parsed

        return parsed_output  #  type: ignore
