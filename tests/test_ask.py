from types import SimpleNamespace

from app import ask as ask_module


def test_main_reuses_chat_for_follow_up_questions(monkeypatch, capsys):
    class FakeChat:
        def __init__(self):
            self.questions = []

        def send_message(self, question):
            self.questions.append(question)
            return SimpleNamespace(
                text=f"answer to {question}",
                usage_metadata=SimpleNamespace(
                    prompt_token_count=3,
                    candidates_token_count=4,
                ),
            )

    chat = FakeChat()

    class FakeClient:
        class chats:
            @staticmethod
            def create(model):
                return chat

    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: FakeClient())
    monkeypatch.setattr("sys.argv", ["app.ask", "first question"])
    questions = iter(["follow-up question", "/exit"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(questions))

    ask_module.main()

    assert chat.questions == ["first question", "follow-up question"]
    output = capsys.readouterr().out
    assert output.count("[トークン] 入力: 3, 出力: 4") == 2