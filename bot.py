"""
Point d'entrée du bot.

Sécurité :
- Le token n'est JAMAIS écrit en dur, uniquement chargé depuis .env
- Intents limités au strict nécessaire (principe du moindre privilège)
- Toute erreur de commande est interceptée et loggée, sans jamais
  exposer de détails techniques à l'utilisateur final
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from utils.logger import get_logger

load_dotenv()
logger = get_logger()

# --- Validation stricte des variables d'environnement au démarrage ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

if not DISCORD_TOKEN:
    logger.error("Variable d'environnement manquante : DISCORD_TOKEN")
    logger.error("Copie .env.example vers .env et remplis les valeurs requises.")
    sys.exit(1)

# --- Principe du moindre privilège : uniquement les intents nécessaires ---
# N'active `message_content` ou `members` que si une commande en a
# réellement besoin (ce sont des intents "privilégiés" à activer aussi
# sur le Developer Portal).
intents = discord.Intents.default()
intents.message_content = False
intents.members = False


class SecureBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        # --- Chargement dynamique des cogs ---
        cogs_dir = Path(__file__).parent / "cogs"
        for file in sorted(cogs_dir.glob("*.py")):
            if file.stem.startswith("_"):
                continue
            extension = f"cogs.{file.stem}"
            try:
                await self.load_extension(extension)
                logger.info(f"Cog chargé : {extension}")
            except Exception:
                logger.error(f"Échec du chargement du cog {extension} :\n{traceback.format_exc()}")

        # --- Synchronisation des commandes slash ---
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(f"{len(synced)} commande(s) synchronisée(s) sur le serveur de test.")
        else:
            synced = await self.tree.sync()
            logger.info(f"{len(synced)} commande(s) synchronisée(s) globalement (jusqu'à 1h de propagation).")

    async def on_ready(self) -> None:
        logger.info(f"Connecté en tant que {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.listening, name="/ping")
        )


bot = SecureBot()


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    """
    Gestion globale des erreurs de commandes slash.
    On ne renvoie JAMAIS le détail technique à l'utilisateur (cela pourrait
    exposer des chemins de fichiers ou des infos internes) : on log côté
    serveur et on renvoie un message générique.
    """
    if isinstance(error, app_commands.CommandOnCooldown):
        message = f"⏳ Merci de patienter encore {error.retry_after:.1f}s avant de réutiliser cette commande."
    elif isinstance(error, app_commands.MissingPermissions):
        message = "⛔ Tu n'as pas la permission d'utiliser cette commande."
    elif isinstance(error, app_commands.NoPrivateMessage):
        message = "⛔ Cette commande doit être utilisée sur un serveur."
    else:
        logger.error(f"Erreur non gérée dans une commande : {error}", exc_info=error)
        message = "❌ Une erreur est survenue lors de l'exécution de cette commande."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


async def main() -> None:
    async with bot:
        try:
            await bot.start(DISCORD_TOKEN)
        except discord.LoginFailure:
            logger.error("Échec de connexion à Discord : token invalide. Vérifie ton .env.")
            sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Arrêt du bot demandé (Ctrl+C).")
