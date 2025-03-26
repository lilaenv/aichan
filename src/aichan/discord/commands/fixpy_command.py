from discord import (
    Interaction,
    TextStyle,
)
from discord.ui import Modal, TextInput

from src.aichan._cli import parse_args_and_setup_logging
from src.aichan.adapters.chat import ChatMessage
from src.aichan.ai.models.claude_model import ClaudeModelParams
from src.aichan.ai.services.anthropic_text import generate_anthropic_response
from src.aichan.config.env import (
    CLAUDE_DEFAULT_MAX_TOKENS,
    CLAUDE_DEFAULT_TEMPERATURE,
    CLAUDE_DEFAULT_TOP_P,
    FIXPY_MODEL,
)
from src.aichan.config.prompt import FIXPY_SYSTEM
from src.aichan.database.dao.access_dao import AccessDAO
from src.aichan.discord.client import BotClient
from src.aichan.utils.decorators import *
from src.aichan.utils.model_params_store import ModelParamsStore

access_dao = AccessDAO()
client = BotClient.get_instance()
logger = parse_args_and_setup_logging()
model_params = ModelParamsStore()


class CodeModal(Modal):
    """Modal for entering Python code to fix."""

    code_input: TextInput

    def __init__(self, temperature: float, top_p: float) -> None:
        """Initialize the code modal with AI parameters.

        Parameters
        ----------
        temperature : float
            The temperature parameter for Claude.
        top_p : float
            The top_p parameter for Claude.
        """
        super().__init__(title="Pythonコードの修正")

        self.code_input = TextInput(
            label="Python Code",
            style=TextStyle.long,
            placeholder="修正したいPythonコードを入力してください",
            required=True,
        )
        self.add_item(self.code_input)

        # AIパラメータを保存
        self.temperature = temperature
        self.top_p = top_p

    async def on_submit(self, interaction: Interaction) -> None:
        """Handle the submission of the modal.

        Parameters
        ----------
        interaction : Interaction
            The interaction object from Discord.
        """
        await interaction.response.defer(thinking=True)

        try:
            code = self.code_input.value

            # Claude AIに修正を依頼
            if FIXPY_MODEL is None:
                await interaction.followup.send(
                    "エラー: 利用可能なClaudeモデルがありません。管理者に連絡してください。",
                    ephemeral=True,
                )
                return

            params = ClaudeModelParams(
                model=FIXPY_MODEL,
                max_tokens=CLAUDE_DEFAULT_MAX_TOKENS,
                temperature=self.temperature,
                top_p=self.top_p,
            )

            message = [ChatMessage(role="user", content=code)]

            response_result = await generate_anthropic_response(
                system_prompt=FIXPY_SYSTEM,
                prompt=message,
                model_params=params,
            )

            # レスポンスを送信
            await interaction.followup.send(
                f"{response_result.result}",
                ephemeral=True,
            )

        except Exception as err:
            msg = f"Error processing fixpy request: {err!s}"
            logger.exception(msg)
            await interaction.followup.send(
                "コードの修正中にエラーが発生しました。",
                ephemeral=True,
            )


@client.tree.command(name="fixpy", description="Pythonコードのバグやエラーを検出して修正します")
# mypy(name-defined): defined in a wildcard import
@is_authorized_server()  # type: ignore # noqa: F405
# mypy(name-defined): defined in a wildcard import
@is_not_blocked_user()  # type: ignore # noqa: F405
async def fix_command(
    interaction: Interaction,
    temperature: float = CLAUDE_DEFAULT_TEMPERATURE,
    top_p: float = CLAUDE_DEFAULT_TOP_P,
) -> None:
    """Handle the /fixpy slash command.

    Parameters
    ----------
    interaction : Interaction
        The interaction instance.
    temperature : float, optional
        The temperature parameter for Claude, by default CLAUDE_DEFAULT_TEMPERATURE.
    top_p : float, optional
        The top-p parameter for Claude, by default CLAUDE_DEFAULT_TOP_P.
    """
    try:
        user = interaction.user
        logger.info("%s executed 'fixpy' command", user)

        if temperature < 0.0 or temperature > 1.0:
            await interaction.response.send_message(
                "**temperature**は 0.0 から1.0 の間で設定してください",
                ephemeral=True,
            )
            return
        if top_p < 0.0 or top_p > 1.0:
            await interaction.response.send_message(
                "**top_p**は 0.0 から１.0 の間で設定してください",
                ephemeral=True,
            )
            return

        # 利用可能なモデルがない場合はエラーを返す
        if FIXPY_MODEL is None:
            await interaction.response.send_message(
                "利用可能なモデルがありません。管理者に連絡してください。",
                ephemeral=True,
            )
            return

        # Show the modal to input code
        modal = CodeModal(temperature=temperature, top_p=top_p)
        await interaction.response.send_modal(modal)

    except Exception as err:
        msg = f"Error showing fixpy modal: {err!s}"
        logger.exception(msg)
        await interaction.response.send_message(
            "コマンドの実行中にエラーが発生しました。",
            ephemeral=True,
        )
