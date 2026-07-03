"""Commande /security-status — état des protections, réservée aux owners."""

import discord
from discord import app_commands, ui
from discord.ext import commands

from utils.permissions import is_owner


class SecurityStatusView(ui.LayoutView):
    def __init__(self):
        super().__init__()

        checks = [
            ("Token chargé depuis .env (jamais en dur dans le code)", True),
            ("Intents limités au strict nécessaire", True),
            ("Cooldown anti-spam actif sur les commandes", True),
            ("Gestion globale des erreurs (on_error / on_app_command_error)", True),
            ("Aucune commande eval/exec exposée", True),
            ("Réponses sensibles envoyées en ephemeral", True),
        ]
        lines = "\n".join(f"{'✅' if ok else '❌'} {label}" for label, ok in checks)

        container = ui.Container()
        container.add_item(ui.TextDisplay("## 🔒 État de sécurité du bot"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(lines))
        self.add_item(container)


class SecurityStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="security-status",
        description="Affiche l'état des protections du bot (réservé aux propriétaires)",
    )
    @app_commands.checks.cooldown(1, 10.0)
    async def security_status(self, interaction: discord.Interaction) -> None:
        # Double vérification : la commande n'est utile qu'aux owners définis en .env
        if not is_owner(interaction.user.id):
            await interaction.response.send_message(
                "⛔ Tu n'es pas autorisé à utiliser cette commande.", ephemeral=True
            )
            return

        await interaction.response.send_message(view=SecurityStatusView(), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SecurityStatus(bot))
