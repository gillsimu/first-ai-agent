import json

from agents.base_agent import BaseAgent
from agents.calculator_agent import CalculatorAgent, calculator_descriptor
from agents.search_agent import SearchAgent, search_schema
from utils.logger import log_info, log_error


class OrchestratorAgent(BaseAgent):
    def __init__(
        self,
        client,
        memory,
        model: str = "gpt-4o-mini",
        search_api_key: str = "",
        search_provider: str = "serpapi",
    ):
        self.calculator = CalculatorAgent()
        self.search = SearchAgent(api_key=search_api_key, provider=search_provider)

        tools = [
            {**calculator_descriptor, "executor": self._run_calculator},
            {**search_schema, "executor": self._run_search},
        ]

        system_prompt = (
            "You are an orchestrator agent. "
            "Route math to the calculator tool and factual questions to the search tool. "
            "Always use tools when applicable and do not answer from memory."
        )

        super().__init__(
            name="orchestrator",
            client=client,
            memory=memory,
            system_prompt=system_prompt,
            model=model,
            tools=tools,
        )

    def _run_calculator(self, expression: str) -> str:
        return self.calculator.run(expression)

    def _run_search(self, query: str) -> str:
        result = self.search.run(query)
        return json.dumps(result)

    def ask(self, user_input: str) -> str:
        try:
            log_info(f"User: {user_input}")
            self.memory.add_message("user", user_input)

            message = self.call_llm()

            reply = ""
            if message.tool_calls:
                self.memory.chat_history.append(
                    {"role": "assistant", "tool_calls": message.tool_calls, "content": None}
                )
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    try:
                        tool_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args or {}
                    except Exception:
                        tool_args = {}
                    print(f"🛠 Tool called: {tool_name} with args {tool_args}")
                    log_info(f"🛠 Tool called: {tool_name} with args {tool_args}")
                tool_outputs = self.handle_tool_calls(message)
                for output in tool_outputs:
                    log_info(f"🛠 Tool output: {output}")
                reply = self._summarize_tool_outputs(tool_outputs)
            else:
                message = self.call_llm(use_tools=False)
                reply = message.content or ""
            self.memory.add_message("assistant", reply)
            log_info(f"Agent: {reply}")
            return reply
        except Exception as e:
            log_error(f"[orchestrator] Error in ask: {e}")
            return "Oops! Something went wrong."

    def _summarize_tool_outputs(self, outputs: list[str]) -> str:
        formatted = [self._format_tool_output(o) for o in outputs]
        if not formatted:
            return ""

        prompt = (
            "Summarize the tool results below in one concise response. "
            "Use only the provided tool results. Do not add external knowledge.\n\n"
            + "\n".join(f"- {item}" for item in formatted)
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You summarize tool outputs only."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            log_error(f"[orchestrator] Summarization failed: {e}")
            if len(formatted) == 1:
                return formatted[0]
            return "; ".join(formatted)

    def _format_tool_output(self, output: str) -> str:
        try:
            data = json.loads(output)
            if isinstance(data, dict):
                if "result" in data:
                    return str(data["result"])
                if "error" in data:
                    return str(data["error"])
        except Exception:
            pass
        return str(output)
