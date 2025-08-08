import discord
from discord.ext import commands
import traceback

from utils import role_panel_function as Func

class NormalSelectEvent():
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    async def call(self, interaction: discord.Interaction):
        try:
            custom_id: str = interaction.data["custom_id"] #interaction.dataからcustom_idを取り出す
            if custom_id == "mp_role_panel_edit_select":
                value = interaction.data["values"][0]
                if interaction.user.id not in Func.select_role_panel:
                    await interaction.response.edit_message("役職パネルを選択してください。", view=None)
                    return
                message_id = Func.select_role_panel[interaction.user.id]
                message = await interaction.channel.fetch_message(message_id)
                if message == None:
                    await interaction.response.edit_message("役職パネルのメッセージが見つかりません。", view=None)
                    return
                embed = message.embeds[0]
                if embed == None:
                    await interaction.response.edit_message("役職パネルが見つかりません。", view=None)
                    return
                if embed.fields and embed.fields[1].value == value:
                    await interaction.response.edit_message(content="重複許可はすでに設定されています。", view=None)
                    return
                view: discord.ui.View = discord.ui.View()
                type_text: str = value
                component: discord.ui.View = message.components[0]
                await Func.fix_select_role_panel(interaction=interaction, message=message, type_text=type_text)
        except Exception:
            traceback.print_exc()