from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
# Make sure the environment variable is set
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Use OpenAI client WITHOUT arguments
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"Hello!"}]
)

print(response.choices[0].message.content)
breakpoint()