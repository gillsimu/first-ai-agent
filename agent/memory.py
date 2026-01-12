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
        total_tokens = 0
        for msg in self.chat_history:
            content = msg.get("content") or ""
            total_tokens += len(self.enc.encode(content))

            # Count tool arguments if present
            if msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    args_str = str(call.function.arguments)
                    total_tokens += len(self.enc.encode(args_str))
        return total_tokens
    
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
            # Build content safely for summarization
            content_to_summarize = []
            for m in pruned_messages:
                role = m.get("role", "unknown")
                content = m.get("content") or ""
                # If tool_calls exist, convert them to string
                if m.get("tool_calls"):
                    tool_info = " | ".join(
                        f"{call.function.name}({call.function.arguments})" 
                        for call in m["tool_calls"]
                    )
                    content += f" | ToolCalls: {tool_info}"
                content_to_summarize.append(f"{role}: {content}")

            summary_prompt = "Summarize the following conversation briefly, preserving context:\n" + "\n".join(content_to_summarize)

            if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": summary_prompt}],
                        temperature=0.5
                    )
                    summary_text = response.choices[0].message.content
                    log_debug(f"[X] Generated summary of pruned messages: {summary_text}")
                    self.summary = f"\n{summary_text}"

                    # Keep summary as a system message at the start
                    self.chat_history.insert(0, {"role": "system", "content": self.summary})
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
