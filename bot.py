# Based on code by Ali Tobah
# and by Dr. Abel Sanchez's Discord bot tutorial
# Extended: IT Support Bot with conversation memory

from dotenv import load_dotenv
from groq import Groq
from collections import defaultdict
import discord
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY)

conversation_history = defaultdict(list)
MAX_HISTORY = 6

def call_groq(user_id: str, question: str) -> str:
    history = conversation_history[user_id]
    history.append({"role": "user", "content": question})

    messages = [
        {
            "role": "system",
            "content": (
                "You are an internal IT support specialist for a company of 300 employees. "
                "Help with VPN issues, password resets, IAM queries, and security policies. "
                "Be concise — reply in 3-5 bullet points maximum. "
                "If the issue requires human intervention, say so explicitly."
            )
        }
    ] + history

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    response = completion.choices[0].message.content
    history.append({"role": "assistant", "content": response})

    if len(history) > MAX_HISTORY * 2:
        conversation_history[user_id] = history[-(MAX_HISTORY * 2):]

    print(f"[{user_id}] {question[:50]}...")
    return response

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)

    if message.content.startswith("$hello"):
        await message.channel.send("Good day! Type $question followed by your IT issue.")

    elif message.content.startswith("$reset"):
        conversation_history[user_id] = []
        await message.channel.send(
            "Session reset. Previous context cleared. How can I help you?"
        )

    elif message.content.startswith("$question"):
        message_content = message.content.split("$question", 1)[1].strip()

        if not message_content:
            await message.channel.send(
                "Please type your IT issue after $question"
            )
            return

        response = call_groq(user_id, message_content)
        await message.channel.send(response)

client.run(DISCORD_TOKEN)