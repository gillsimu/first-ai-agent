from openai import OpenAI
from utils.logger import log_info, log_debug, log_error
from utils.token_monitor import count_tokens
from utils.system_stats_monitor import log_system_usage


MAX_TOKENS = 120_000  # Safety margin
class Agent:
    def __init__(self, client, memory):
        self.client = client
        self.memory = memory

    def ask(self, user_input):
        try:
            log_info(f"User: {user_input}")
            self.memory.add_message("user", user_input)

            # Count tokens
            count_tokens(self.memory.get_history())

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.memory.get_history()
            )

            reply = response.choices[0].message.content
            self.memory.add_message("assistant", reply)
            log_info(f"Agent: {reply}")

            log_system_usage()

            return reply
        except Exception as e:
            log_error(f"Error in Agent.ask: {e}")
            return "Oops! Something went wrong."
