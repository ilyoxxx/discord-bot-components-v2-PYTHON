"""Commande /serverinfo — infos du serveur, exemple Section + Thumbnail."""

import discord
from discord import app_commands, ui
from discord.ext import commands


class ServerInfoView(ui.LayoutView):
    def __init__(self, guild: discord.Guild, owner: discord.Member | None, requester: discord.User):
        super().__init__()

        info_text = ui.TextDisplay(
            f"## 📊 {guild.name}\n"
            f"**Membres :** {guild.member_count}\n"
            f"**Propriétaire :** {owner.mention if owner else 'Inconnu'}\n"
            f"**Créé le :** <t:{int(guild.created_at.timestamp())}:D>\n"
            f"**Salons :** {len(guild.channels)}\n"
            f"**Rôles :** {len(guild.roles)}\n"
            f"**Niveau de vérification :** {guild.verification_level}"
        )

        container = ui.Container()

        if guild.icon:
            section = ui.Section(info_text, accessory=ui.Thumbnail(guild.icon.url))
            container.add_item(section)
        else:
            container.add_item(info_text)

        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(f"-# Demandé par {requester}"))

        self.add_item(container)


class ServerInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="Affiche les informations du serveur")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0)
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        assert guild is not None  # garanti par @app_commands.guild_only()

        owner = guild.owner or (await guild.fetch_member(guild.owner_id) if guild.owner_id else None)

        view = ServerInfoView(guild, owner, interaction.user)
        await interaction.response.send_message(view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ServerInfo(bot))
