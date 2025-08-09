import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../")


from typegpt_light.openai import AsyncTypeOpenAI, OpenAIChatModel, UnsafeModel


class TestOpenAIChatCompletion:

    def test_max_token_counter(self):
        # check if test covers all models (increase if new models are added)
        assert len(OpenAIChatModel.__args__) == 43  #  type: ignore

        client = AsyncTypeOpenAI(api_key="mock")

        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo") == 16384
        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo-0301") == 4096
        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo-0613") == 4096
        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo-1106") == 16384
        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo-0125") == 16384
        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo-16k") == 16384
        assert client.chat.completions.max_tokens_of_model("gpt-3.5-turbo-16k-0613") == 16384
        assert client.chat.completions.max_tokens_of_model("gpt-4") == 8192
        assert client.chat.completions.max_tokens_of_model("gpt-4-0314") == 8192
        assert client.chat.completions.max_tokens_of_model("gpt-4-0613") == 8192
        assert client.chat.completions.max_tokens_of_model("gpt-4-32k") == 32768
        assert client.chat.completions.max_tokens_of_model("gpt-4-32k-0314") == 32768
        assert client.chat.completions.max_tokens_of_model("gpt-4-32k-0613") == 32768
        assert client.chat.completions.max_tokens_of_model("gpt-4-turbo-preview") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4-1106-preview") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4-0125-preview") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4-vision-preview") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4-turbo") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4-turbo-2024-04-09") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4o") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4o-2024-05-13") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4o-2024-08-06") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4o-2024-11-20") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4o-mini") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4o-mini-2024-07-18") == 128_000
        assert client.chat.completions.max_tokens_of_model("o1") == 128_000
        assert client.chat.completions.max_tokens_of_model("o1-2024-12-17") == 128_000
        assert client.chat.completions.max_tokens_of_model("o1-mini") == 128_000
        assert client.chat.completions.max_tokens_of_model("o1-mini-2024-09-12") == 128_000
        assert client.chat.completions.max_tokens_of_model("gpt-4.1") == 1_047_576
        assert client.chat.completions.max_tokens_of_model("gpt-4.1-2025-04-14") == 1_047_576
        assert client.chat.completions.max_tokens_of_model("gpt-4.1-mini") == 1_047_576
        assert client.chat.completions.max_tokens_of_model("gpt-4.1-mini-2025-04-14") == 1_047_576
        assert client.chat.completions.max_tokens_of_model("gpt-4.1-nano") == 1_047_576
        assert client.chat.completions.max_tokens_of_model("gpt-4.1-nano-2025-04-14") == 1_047_576
        assert client.chat.completions.max_tokens_of_model("o3-mini") == 200_000
        assert client.chat.completions.max_tokens_of_model("o3-mini-2025-01-31") == 200_000
        assert client.chat.completions.max_tokens_of_model("gpt-5") == 400_000
        assert client.chat.completions.max_tokens_of_model("gpt-5-2025-08-07") == 400_000
        assert client.chat.completions.max_tokens_of_model("gpt-5-mini") == 400_000
        assert client.chat.completions.max_tokens_of_model("gpt-5-mini-2025-08-07") == 400_000
        assert client.chat.completions.max_tokens_of_model("gpt-5-nano") == 400_000
        assert client.chat.completions.max_tokens_of_model("gpt-5-nano-2025-08-07") == 400_000

        # "unsafe" models

        # all unknown models should return 128k
        assert client.chat.completions.max_tokens_of_model(UnsafeModel(name="some-random-model")) == 128_000

        # but known ones, should return the correct value
        assert client.chat.completions.max_tokens_of_model(UnsafeModel(name="o3-mini-2025-01-31")) == 200_000

    # -
