# Based on code by Ali Tobah
# and by Dr. Abel Sanchez's Discord bot tutorial
from dotenv import load_dotenv
from groq import Groq
import discord
import os

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def call_groq(question):
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful university professor. Answer clearly and concisely."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    response = completion.choices[0].message.content
    print(response)
    return response

# Discord setup
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

    if message.content.startswith("$hello"):
        await message.channel.send("Good day!")

    elif message.content.startswith("$question"):
        message_content = message.content.split("$question", 1)[1].strip()

        if not message_content:
            await message.channel.send("Please type a question after $question")
            return

        response = call_groq(message_content)
        await message.channel.send(response)

client.run(DISCORD_TOKEN)