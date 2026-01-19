from dotenv import load_dotenv
import os
import sys
from openai import OpenAI
from memory.memory import Memory
from agents.orchestrator import OrchestratorAgent
import logging
# Suppress console printing for httpx/urllib3
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Load environment
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# Initialize OpenAI client
client = OpenAI()

# Initialize memory & orchestrator
memory = Memory(client=client, token_limit=25)
agent = OrchestratorAgent(client=client, memory=memory, model="gpt-4o-mini")

print("AI Agent is ready! Type 'exit' to quit.")

if "--demo" in sys.argv:
    demo_inputs = [
        "1+1",
        "Capital of France?",
        "2+2",
    ]
    for user_input in demo_inputs:
        print(f"You: {user_input}")
        reply = agent.ask(user_input)
        print("Agent:", reply)
else:
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        reply = agent.ask(user_input)
        print("Agent:", reply)
