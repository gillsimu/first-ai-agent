from openai import OpenAI
from utils.logger import log_debug, log_error
import json

# Hold shared OpenAI client
# Own its own memory
# Define how agents talk to the LLM
# Be extended by CalculatorAgent, SearchAgent, Orchestrator
class BaseAgent:
    def __init__(
        self,
        name: str,
        client: OpenAI,
        memory,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        tools: list | None = None
    ):
        self.name = name
        self.client = client
        self.memory = memory
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools or []

    def _tool_schemas(self):
        """
        Return tool descriptors without executors for the LLM API.
        """
        return [{k: v for k, v in tool.items() if k != "executor"} for tool in self.tools]

    def call_llm(self, use_tools: bool = True):
        """
        Call the LLM with current memory and tools.
        Returns the assistant message.
        """
        try:
            tools = self._tool_schemas() if self.tools and use_tools else None
            tool_choice = "required" if tools else None
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.memory.get_history()
                ],
                tools=tools,
                tool_choice=tool_choice
            )

            return response.choices[0].message

        except Exception as e:
            log_error(f"[{self.name}] LLM call failed: {e}")
            raise

    def handle_tool_calls(self, message):
        """
        Execute requested tools and update memory.
        Returns tool outputs.
        """
        tool_outputs = []
        # Tools should be descriptors, not functions
        # The LLM should see a description of a tool, not the Python function itself.
        # The LLM only understands: Text, JSON schemas, Names, Descriptions. IT DOES NOT UNDERSTAND: Call Python functions, execute code, import modules.
        # The LLM needs descriptor (A contract between the LLM and your system. “If you want X, ask for Y in this exact shape.”): {
        #   "name": "calculator",
        #   "description": "Use this tool to perform math",
        #   "parameters": {
        #     "expression": { "type": "string" }
        #   }
        # }
        # It answers: What is the tool called? When should I use it? What arguments does it take?
        # The LLM: Decides whether to use the tool -> Emits a JSON tool call
        # Your code: Executes the real function -> Returns results
        # Security: Never execute raw code from the LLM. Always use predefined functions mapped to tool names. 
        # Deterministic: The same tool call should always produce the same result.
        # Testability: You can mock tool functions in tests.
        # Replacability: You can swap out tool implementations without changing the LLM logic.
        # Descriptors describe intent. Functions execute reality.
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            raw_args = tool_call.function.arguments

            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except Exception:
                args = {}

            tool = next((t for t in self.tools if t["function"]["name"] == tool_name), None)

            if not tool:
                output = f"Unknown tool: {tool_name}"
            else:
                output = tool["executor"](**args)

            # Store tool response
            self.memory.chat_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": output
            })

            tool_outputs.append(output)

        return tool_outputs
