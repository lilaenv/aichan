from openai import (
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
    InternalServerError,
    OpenAI,
)

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.adapters.chat import ChatHistory, ChatMessage
from src.aichan.adapters.response import ResponseResult, ResponseStatus
from src.aichan.ai.models.gpt_model import GptModelParams

client = OpenAI()
logger = parse_args_and_setup_logging()


async def generate_openai_response(
    system_prompt: str,
    prompt: list[ChatMessage],
    model_params: GptModelParams,
) -> ResponseResult:
    """Generate a response from the GPT model.

    Parameters
    ----------
    system_prompt : str
        The system instruction.

    prompt : list[ChatMessage]
        A list of chat messages forming the conversation history.

    model_params : GptModelParams
        Configuration settings for the model, including parameters like
        max_tokens, temperature and top-p sampling.
    """
    try:
        convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
        full_prompt = [{"role": "developer", "content": system_prompt}, *convo]
        completion = client.chat.completions.create(
            # mypy(arg-type): expected loooooooooooooooooooooooong type
            messages=full_prompt,  # type: ignore
            # mypy(arg-type): expected ChatModel | str
            # but I specified it as app_commands.Choice[int] | str
            model=model_params.model,  # type: ignore
            max_tokens=model_params.max_tokens,
            temperature=model_params.temperature,
            top_p=model_params.top_p,
        )
        completion_result = completion.choices[0].message.content
        return ResponseResult(status=ResponseStatus.SUCCESS, result=completion_result)
    except (APIConnectionError, APITimeoutError, BadRequestError) as err:
        msg = f"Failed to genarate text: {err!s}"
        logger.exception(msg)
        return ResponseResult(status=ResponseStatus.OPENAI_ERROR, result=None)
    except InternalServerError as err:
        msg = f"InternalServerError has occurred: {err!s}"
        logger.exception(msg)
        return ResponseResult(status=ResponseStatus.OPENAI_ERROR, result=None)
    except Exception as err:
        msg = f"Unexpected error has occurred: {err!s}"
        logger.exception(msg)
        return ResponseResult(status=ResponseStatus.ERROR, result=None)
