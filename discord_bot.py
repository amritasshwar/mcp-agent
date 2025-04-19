import os
import discord
import asyncio
import concurrent.futures
from dotenv import load_dotenv
from agent_runner import run_agent

# === Load env ===
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# === Setup Bot ===
intents = discord.Intents.default()
intents.message_content = True  # Required for message reading
bot = discord.Client(intents=intents)

executor = concurrent.futures.ThreadPoolExecutor()

@bot.event
async def on_ready():
    print(f"🚀 Influenxers is online as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore messages from other bots
    if message.author.bot:
        return

    # Check if bot was mentioned
    if bot.user in message.mentions:
        # Remove bot mention from message
        content = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if not content:
            await message.channel.send("👋 Hi! Send me a task after mentioning me, like:\n`@Influenxers Ingest product for michelechungugc using Notion...`")
            return

        await message.channel.send("🧠 Influenxers is processing your task. This may take up to 30 minutes ⏳...")

        # Run the agent without blocking the event loop
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(executor, run_agent, content)
            await message.channel.send(f"✅ Done!\n```\n{response[:1900]}\n```")
        except Exception as e:
            await message.channel.send(f"❌ Something went wrong:\n```\n{str(e)}\n```")

# === Run Bot ===
bot.run(DISCORD_TOKEN)
