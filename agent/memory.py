import tiktoken
from utils.logger import log_debug, log_info
from openai import OpenAI

class Memory:
    def __init__(self, model="gpt-4o-mini", token_limit=3000, client=None):
        """
        model: the GPT model you are using
        token_limit: max total tokens to keep in memory before pruning
        client: OpenAI client instance (required for summarization)
        """
        self.chat_history = []
        self.model = model
        self.enc = tiktoken.encoding_for_model(model)
        self.token_limit = token_limit
        self.client = client
        self.summary = ""  # Holds summary of pruned messages

    def add_message(self, role, content):
        """Add a message and prune memory if token limit exceeded"""
        self.chat_history.append({"role": role, "content": content})
        log_debug(f"Memory updated. Total messages: {len(self.chat_history)}")
        
        # Check token usage and prune if needed
        self.prune_memory()
    
    def token_count(self):
        """Count total tokens in memory including summary"""
        tokens = sum(len(self.enc.encode(msg["content"])) for msg in self.chat_history)
        if self.summary:
            tokens += len(self.enc.encode(self.summary))
        return tokens
    
    def prune_memory(self):
        """Prune or summarize oldest messages until under token limit"""
        if not self.chat_history:
            return
        
        memory_pruned = False
        target_tokens = int(self.token_limit * 0.75)
        pruned_messages = []

        # Remove oldest messages until under target
        while self.token_count() > target_tokens and self.chat_history:
            removed = self.chat_history.pop(0)
            log_debug(f"[X] Message pruned: {removed}")
            pruned_messages.append(removed)
            memory_pruned = True

        if memory_pruned and pruned_messages:
            if self.client:
                # Summarize pruned messages
                content_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in pruned_messages])
                summary_prompt = f"Summarize the following conversation briefly, preserving context:\n{content_to_summarize}"
                
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": summary_prompt}],
                        temperature=0.5  # how random or creative the model’s responses are Range: 0.0 to 2.0 (usually 0–1.5) Lower values → more deterministic (safe, repetitive, precise) Higher values → more random/creative (varied, exploratory, sometimes unpredictable)
                    )
                    summary_text = response.choices[0].message.content
                    log_debug(f"[X] Generated summary ofr pruned messages: {summary_text}")
                    self.summary += f"\n{summary_text}"

                    # Keep summary as a system message in history
                    self.chat_history.insert(0, {"role": "system", "content": self.summary})  # system messages are usually read first by the model by inserting the summary at the start, GPT sees the pruned context first
                except Exception as e:
                    log_info(f"[!] Failed to summarize pruned messages: {e}")
            else:
                log_debug("[!] OpenAI client not provided. Pruned messages are dropped.")

            log_debug(f"[X] Memory pruned. Current token count: {self.token_count()}, Total messages: {len(self.chat_history)}")
    
    def get_history(self):
        return self.chat_history

    def memory_size(self):
        """Approximate size of memory (number of messages or characters)."""
        total_chars = sum(len(m["content"]) for m in self.chat_history)
        return len(self.chat_history), total_chars
