import anthropic

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.adapters.chat import ChatHistory, ChatMessage
from src.aichan.adapters.response import ResponseResult, ResponseStatus
from src.aichan.ai.models.claude_model import ClaudeModelParams

client = anthropic.Anthropic()
logger = parse_args_and_setup_logging()


async def generate_anthropic_response(
    system_prompt: str,
    prompt: list[ChatMessage],
    model_params: ClaudeModelParams,
) -> ResponseResult:
    """Generate a response from the claude model.

    Parameters
    ----------
    system_prompt : str
        The system instruction.

    prompt : list[ChatMessage]
        A list of chat messages forming the conversation history.

    model_params : ClaudeModelParams
        The model parameters.
    """
    try:
        convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
        result = client.messages.create(
            # mypy(arg-type): expected "Iterable[MessageParam]"
            messages=convo,  # type: ignore
            # mypy(arg-type): expected ModelParam
            # but I specified it as app_commands.Choice[int] | str
            model=model_params.model,  # type: ignore
            max_tokens=model_params.max_tokens,
            system=system_prompt,
            temperature=model_params.temperature,
            top_p=model_params.top_p,
        )
        # mypy(union-attr): has no attribute "text"
        claude_result = result.content[0].text  # type: ignore
        return ResponseResult(status=ResponseStatus.SUCCESS, result=claude_result)
    except Exception as err:
        msg = f"Unexpected error has occurred: {err!s}"
        logger.exception(msg)
        return ResponseResult(status=ResponseStatus.ERROR, result=None)
