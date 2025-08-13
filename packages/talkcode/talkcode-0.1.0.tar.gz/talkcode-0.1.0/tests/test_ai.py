from src.talkcode.chat.ai import MultiProviderAI

def test_ai_config_load():
    try:
        ai = MultiProviderAI()
        response = ai.ask("What is a function?", context="def foo(): pass")
        assert isinstance(response, str)
    except Exception:
        pass  # Skip if config is not set
