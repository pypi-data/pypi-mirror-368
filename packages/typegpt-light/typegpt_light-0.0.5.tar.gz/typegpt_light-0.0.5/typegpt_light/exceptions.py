from typegpt_light.prompt_definition.prompt_template import UserPrompt


class LLMException(Exception):

    def __init__(
        self,
        message: str,
        system_prompt: str | None = None,
        user_prompt: UserPrompt | None = None,
        raw_completion: str | None = None,
    ):
        super().__init__(message)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.raw_completion = raw_completion


class LLMTokenLimitExceeded(LLMException): ...


class LLMModelRefusal(LLMException): ...


class LLMOutputTruncated(LLMException):
    """The output JSON couldn't be completed due to the output token limit"""

    ...
