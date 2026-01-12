from dotenv import load_dotenv
import os
from openai import OpenAI
from agent.memory import Memory
from agent.agent import Agent
import logging
# Suppress console printing for httpx/urllib3
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Load environment
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI()

# Initialize memory & agent
memory = Memory(client=client, token_limit=25)
agent = Agent(client, memory)

print("AI Agent is ready! Type 'exit' to quit.")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    reply = agent.ask(user_input)
    print("Agent:", reply)
