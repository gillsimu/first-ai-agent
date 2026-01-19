import tiktoken
from utils.logger import log_debug

# Choose tokenizer based on model
ENCODER = tiktoken.encoding_for_model("gpt-4o-mini")

def count_tokens(messages):
    """
    Count tokens for a list of messages (role + content)
    """
    total_tokens = 0
    for m in messages:
        total_tokens += len(ENCODER.encode(m["role"]))  # Role token
        content = m.get("content") or ""
        total_tokens += len(ENCODER.encode(content))  # Content token
    log_debug(f"Total tokens in conversation: {total_tokens}")
    return total_tokens
