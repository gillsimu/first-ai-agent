from openai import OpenAI
from utils.logger import log_info, log_debug, log_error
from utils.token_monitor import count_tokens
from utils.system_stats_monitor import log_system_usage
from tools.calculator.calculator import calculator_tool
from tools.calculator.schema import calculator_schema
from tools.search.search import search_tool
from tools.search.schema import search_schema
import json

MAX_TOKENS = 120_000  # Safety margin

class Agent:
    def __init__(self, client: OpenAI, memory, model="gpt-4o-mini"):
        self.client = client
        self.memory = memory
        self.model = model

        self.system_prompt = (
            "You are an AI agent. "
            "If a user asks for a mathematical calculation, "
            "you MUST use the calculator tool. "
            "Do NOT perform math yourself."
            "If a user asks for factual information, you MUST use the search tool. "
            "Do NOT answer using your own knowledge."
        )

    def ask(self, user_input: str) -> str:
        try:
            # --- Step 0: Log and add user message to memory ---
            log_info(f"User: {user_input}")
            self.memory.add_message("user", user_input)

            # --- Step 1: Ask GPT if it wants to use a tool ---
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.memory.get_history()
                ],
                tools=[calculator_schema, search_schema],
                tool_choice="auto"
            )

            message = response.choices[0].message

            # --- Step 2: Tool execution if GPT requested ---
            if message.tool_calls:
                # Save assistant tool call to memory
                self.memory.chat_history.append({
                    "role": "assistant",
                    "tool_calls": message.tool_calls,
                    "content": None
                })

                # Handle each tool call
                for tool_call in message.tool_calls:
                    log_debug(f"🛠 Tool called: {tool_call.function.name}")
                    tool_name = tool_call.function.name
                    raw_args = tool_call.function.arguments

                    # Parse arguments safely
                    try:
                        if isinstance(raw_args, str):
                            tool_args = json.loads(raw_args)
                        else:
                            tool_args = raw_args or {}
                    except Exception as e:
                        log_error(f"Failed to parse tool arguments: {e}")
                        tool_args = {}

                    print(f"🛠 Tool called: {tool_name} with args {tool_args}")

                    # Execute tool
                    if tool_name == "calculator":
                        expression = tool_args.get("expression", "")
                        tool_result = calculator_tool.func(expression)
                    elif tool_name == "search":
                        query = tool_args.get("query", "")
                        tool_result = search_tool.func(query)
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                    # Save tool result to memory
                    self.memory.chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })

                # --- Step 3: Send updated memory to GPT for final answer ---
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *self.memory.get_history()
                    ]
                )

                final_message = second_response.choices[0].message
                reply = final_message.content
            else:
                print(f"🛠 LLM did not request a tool.")
                # No tool requested, just use GPT response
                reply = message.content

            # --- Step 4: Store assistant reply and log ---
            self.memory.add_message("assistant", reply)
            log_info(f"Agent: {reply}")

            # --- Step 5: Monitoring ---
            count_tokens(self.memory.get_history())
            log_system_usage()

            return reply

        except Exception as e:
            log_error(f"Error in Agent.ask: {e}")
            return "Oops! Something went wrong."
