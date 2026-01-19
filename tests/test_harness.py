import json
import unittest

from agents.orchestrator import OrchestratorAgent


class MemoryStub:
    def __init__(self):
        self.chat_history = []

    def add_message(self, role, content):
        self.chat_history.append({"role": role, "content": content})

    def get_history(self):
        return self.chat_history


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, tool_id, function):
        self.id = tool_id
        self.function = function


class FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls or []


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, message):
        self.choices = [FakeChoice(message)]


class FakeChatCompletions:
    def __init__(self, parent):
        self.parent = parent

    def create(self, model, messages, tools=None, tool_choice=None, **_kwargs):
        if tools and tool_choice == "required":
            user_text = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_text = msg.get("content") or ""
                    break

            if any(ch.isdigit() for ch in user_text) or any(op in user_text for op in "+-*/"):
                name = "calculator"
                args = {"expression": user_text}
            else:
                name = "search"
                args = {"query": user_text}

            self.parent.last_tool_name = name
            tool_call = FakeToolCall("tool_1", FakeFunction(name, json.dumps(args)))
            return FakeResponse(FakeMessage(content=None, tool_calls=[tool_call]))

        # Summarization call or no-tools response
        user_prompt = messages[-1]["content"] if messages else ""
        lines = [line.strip() for line in user_prompt.splitlines()]
        items = [line[2:] for line in lines if line.startswith("- ")]
        summary = items[0] if items else ""
        return FakeResponse(FakeMessage(content=summary, tool_calls=[]))


class FakeClient:
    def __init__(self):
        self.last_tool_name = None
        self.chat = type("Chat", (), {})()
        self.chat.completions = FakeChatCompletions(self)


class OrchestratorHarnessTests(unittest.TestCase):
    # This test harness is a fully offline, deterministic stand-in for the real LLM.
    # It verifies that the orchestrator routes math questions to the calculator tool,
    # routes factual questions to the search tool, and returns the tool output as the
    # final response. The FakeClient simulates tool selection and summarization so the
    # tests can run without network calls or API keys.
    def setUp(self):
        self.client = FakeClient()
        self.memory = MemoryStub()
        self.agent = OrchestratorAgent(client=self.client, memory=self.memory)

    def test_calculator_path(self):
        reply = self.agent.ask("1+1")
        self.assertEqual(self.client.last_tool_name, "calculator")
        self.assertEqual(reply, "Result: 2")

    def test_search_path(self):
        reply = self.agent.ask("Capital of France?")
        self.assertEqual(self.client.last_tool_name, "search")
        self.assertEqual(reply, "Bathinda is the capital of France.")


if __name__ == "__main__":
    unittest.main()
