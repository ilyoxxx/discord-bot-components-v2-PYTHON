# 🤖 Discord Bot — Components V2 (Python)

Un bot Discord moderne construit avec **discord.py ≥ 2.6** et les nouveaux **Components V2**, conçu selon des bonnes pratiques de sécurité strictes (gestion des secrets, permissions, anti-spam, gestion d'erreurs).

![Python](https://img.shields.io/badge/python-%3E%3D3.10-3776AB?logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-%E2%89%A52.6-5865F2?logo=discord&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-blue)

> ⚠️ **Note honnête** : aucun logiciel n'est "100% sécurisé". Ce projet applique un ensemble de bonnes pratiques reconnues (moindre privilège, secrets hors du code, validation, gestion d'erreurs) pour réduire au maximum la surface d'attaque — mais la sécurité reste un processus continu (mises à jour des dépendances, rotation du token, etc.), pas un état figé.

C'est l'équivalent Python du [bot Node.js / discord.js]([../discord-bot-v2](https://github.com/ilyoxxx/discord-bot-components-v2-JAVASCRIPT)) — même structure, mêmes fonctionnalités, mêmes principes de sécurité.

---

## ✨ Fonctionnalités

- Interface moderne avec **Components V2** (`ui.LayoutView`, `Container`, `Section`, `TextDisplay`, `Separator`, `Thumbnail`)
- Commandes slash : `/ping`, `/serverinfo`, `/security-status`
- Architecture en **cogs** chargés dynamiquement
- Cooldown anti-spam natif (`app_commands.checks.cooldown`)
- Gestion globale des erreurs (aucune trace technique exposée aux utilisateurs)
- Logger avec redaction automatique des tokens
- Vérification stricte des variables d'environnement au démarrage

## 🔒 Sécurité — ce qui est mis en place

| Mesure | Détail |
|---|---|
| Secrets hors du code | Token & IDs chargés via `.env` (jamais commités, voir `.gitignore`) |
| Moindre privilège | `message_content` et `members` désactivés par défaut |
| Anti-spam | Cooldown natif discord.py par commande |
| Contrôle d'accès | Vérification `OWNER_IDS` côté serveur pour les commandes sensibles |
| Gestion d'erreurs | Handler global `on_app_command_error`, aucune stack trace renvoyée à l'utilisateur |
| Logs sûrs | Les tokens sont automatiquement masqués (`[REDACTED_TOKEN]`) dans les logs |
| Pas de code arbitraire | Aucune commande `eval`/`exec` n'est exposée |
| Réponses privées | Les informations sensibles sont envoyées en `ephemeral` |

### Recommandations complémentaires (à faire toi-même)
- Active la **2FA** sur ton compte Discord Developer.
- Régénère immédiatement le token si tu penses qu'il a fuité (Developer Portal → Bot → Reset Token).
- Garde `discord.py` à jour (`pip list --outdated`) et utilise un environnement virtuel isolé.
- Héberge le bot sur une plateforme qui gère les variables d'environnement de façon sécurisée (Railway, Fly.io, VPS avec `.env` non exposé, etc.).
- Ne donne au bot que les **permissions Discord** strictement nécessaires lors de l'invitation.

---

## 📦 Prérequis

- [Python](https://www.python.org/) ≥ 3.10
- Un compte sur le [Discord Developer Portal](https://discord.com/developers/applications)

## 🚀 Installation

```bash
git clone https://github.com/ton-utilisateur/ton-repo.git
cd ton-repo

python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate

pip install -r requirements.txt
```

## ⚙️ Configuration

1. Copie le fichier d'exemple :

```bash
cp .env.example .env
```

2. Remplis `.env` :

```env
DISCORD_TOKEN=le_token_de_ton_bot
GUILD_ID=id_de_ton_serveur_de_test   # optionnel, pour une synchronisation instantanée
OWNER_IDS=ton_id_discord              # optionnel, pour les commandes admin
DEBUG=false
```

3. Sur le [Developer Portal](https://discord.com/developers/applications), section **Bot** :
   - Récupère ton token (bouton **Reset Token**)
   - Active uniquement les intents dont tu as réellement besoin

## 🔗 Inviter le bot sur ton serveur

Génère un lien d'invitation depuis l'onglet **OAuth2 → URL Generator** :
- Scopes : `bot`, `applications.commands`
- Permissions : uniquement celles requises par tes commandes (par défaut, aucune permission spéciale n'est nécessaire pour `/ping`, `/serverinfo`, `/security-status`)

## ▶️ Lancer le bot

```bash
python bot.py
```

Les commandes slash sont synchronisées automatiquement au démarrage (instantanément si `GUILD_ID` est défini, sinon jusqu'à 1h de propagation globale).

---

## 📁 Structure du projet

```
discord-bot-v2-python/
├── cogs/
│   ├── ping.py              # /ping — latence, exemple Container + Separator
│   ├── serverinfo.py        # /serverinfo — exemple Section + Thumbnail
│   └── security_status.py   # /security-status — commande protégée (owners uniquement)
├── utils/
│   ├── logger.py             # Logs avec redaction des secrets
│   └── permissions.py        # Vérification owners
├── bot.py                    # Point d'entrée
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE
```

## 🧩 Ajouter une nouvelle commande

Crée un fichier dans `cogs/`, par exemple `cogs/hello.py` :

```python
import discord
from discord import app_commands, ui
from discord.ext import commands


class HelloView(ui.LayoutView):
    def __init__(self):
        super().__init__()
        container = ui.Container()
        container.add_item(ui.TextDisplay("👋 Salut !"))
        self.add_item(container)


class Hello(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Dit bonjour")
    @app_commands.checks.cooldown(1, 3.0)
    async def hello(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=HelloView())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Hello(bot))
```

Le cog sera chargé automatiquement au prochain démarrage du bot.

---

## 🤝 Contribution

Les pull requests sont les bienvenues. Pour un changement majeur, ouvre d'abord une issue afin d'en discuter.

## 📄 Licence

Distribué sous licence [MIT](./LICENSE).
