import discord
from discord import app_commands
import os
import requests
from dotenv import load_dotenv

# Load tokens from .env or Railway environment
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 🔐 Safety check
if not TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN is not set. Check Railway or .env file.")

# ✅ Allowed channel IDs (replace with yours)
ALLOWED_CHANNELS = [
    1461505623438004275  # Replace with your actual allowed channel IDs
]

# 🚀 Bot setup
class LuaBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")
        await self.tree.sync()
        print("✅ Slash commands synced.")


client = LuaBot()

# ----------------------------
# 💬 /lua Command (AI Lua gen)
# ----------------------------
@client.tree.command(name="lua", description="Generate Roblox Lua code using AI")
@app_commands.describe(prompt="What should the Lua code do?")
async def lua(interaction: discord.Interaction, prompt: str):
    if interaction.channel.id not in ALLOWED_CHANNELS:
        await interaction.response.send_message(
            "🚫 This command is not allowed in this channel.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    try:
        lua_code = call_openrouter(prompt)
        await interaction.followup.send(f"```lua\n{lua_code}\n```")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


# ----------------------------
# 🧹 /clear Command (admin-only)
# ----------------------------
@client.tree.command(name="clear", description="Clear messages in this channel (admin only)")
@app_commands.describe(amount="Number of messages to delete (max 100)")
async def clear(interaction: discord.Interaction, amount: int):
    if interaction.channel.id not in ALLOWED_CHANNELS:
        await interaction.response.send_message(
            "🚫 This command is not allowed in this channel.",
            ephemeral=True
        )
        return

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            "❌ You don’t have permission to manage messages.",
            ephemeral=True
        )
        return

    if amount < 1 or amount > 100:
        await interaction.response.send_message(
            "⚠️ Please choose a number between 1 and 100.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to delete messages: {e}", ephemeral=True)


# ----------------------------
# ℹ️ /info Command
# ----------------------------
@client.tree.command(name="info", description="Show what the bot does and limitations")
async def info(interaction: discord.Interaction):
    desc = (
        "**🤖 LuaBot** helps you write Roblox Lua scripts using AI!\n\n"
        "**Available Commands:**\n"
        "• `/lua` – Generate Lua code using natural language\n"
        "• `/clear` – Admin-only message cleanup (max 100)\n"
        "• `/info` – Show this message\n\n"
        "**⚠️ Limitations:**\n"
        "• AI output may require manual fixing\n"
        "• Command usage restricted to approved channels\n"
        "• Do not abuse API rate limits"
    )
    await interaction.response.send_message(desc, ephemeral=True)


# ----------------------------
# 🤖 OpenRouter AI Call
# ----------------------------
def call_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are an expert Roblox Lua developer. Help the user write clean, working Lua code."},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]


# ----------------------------
# 🔁 Start the Bot
# ----------------------------
client.run(TOKEN)
