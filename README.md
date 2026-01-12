# First AI Agent

A beginner-friendly AI agent in Python that can think, remember, and respond using OpenAI GPT models.

## Features
- Chat with GPT-4o-mini
- Stores conversation memory
- Modular structure to add tools and plugins

## Project Structure

## Setup

1. Clone the repo:

```bash
git clone <your-repo-url>
cd first-ai-agent
```

2. Create and activate virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

3. Upgrade pip and install dependencies:
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

4. Add your OpenAI API key in .env:
```bash
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

5. Run the agent:
```bash
python main.py
```
