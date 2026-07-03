"""Commande /ping — vérifie la latence du bot, exemple Container + Separator."""

import time

import discord
from discord import app_commands, ui
from discord.ext import commands


class PingView(ui.LayoutView):
    """LayoutView = obligatoire pour utiliser les Components V2."""

    def __init__(self, ws_ping_ms: int, roundtrip_ms: int):
        super().__init__()

        container = ui.Container()
        container.add_item(ui.TextDisplay("## 🏓 Pong !"))
        container.add_item(ui.Separator())
        container.add_item(
            ui.TextDisplay(
                f"**Latence API (WebSocket) :** `{ws_ping_ms}ms`\n"
                f"**Temps d'aller-retour :** `{roundtrip_ms}ms`"
            )
        )
        self.add_item(container)


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Vérifie la latence du bot")
    @app_commands.checks.cooldown(1, 5.0)  # 1 utilisation / 5s par utilisateur
    async def ping(self, interaction: discord.Interaction) -> None:
        start = time.monotonic()

        # Réponse différée pour mesurer un aller-retour réel et éviter tout timeout
        await interaction.response.defer(ephemeral=True)

        roundtrip_ms = round((time.monotonic() - start) * 1000)
        ws_ping_ms = round(self.bot.latency * 1000)

        await interaction.followup.send(view=PingView(ws_ping_ms, roundtrip_ms))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))
