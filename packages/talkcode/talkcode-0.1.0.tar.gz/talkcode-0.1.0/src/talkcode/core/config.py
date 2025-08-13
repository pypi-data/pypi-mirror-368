import toml
import os

CONFIG_PATH = os.path.expanduser("~/.talkcode/config.toml")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print("Config not found. Run `talkcode init` first.")
        raise FileNotFoundError(CONFIG_PATH)
    with open(CONFIG_PATH, "r") as f:
        return toml.load(f)

def init_config():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        f.write("""[azure_openai]
provider = "azure"  # Options: azure, openai, anthropic, gemini

# Azure OpenAI
endpoint = "https://your-resource-name.openai.azure.com/"
deployment = "your-deployment-model-name"
api_version = "2024-02-01-preview"
api_key = "your-azure-api-key"

# OpenAI
# deployment = "gpt-3.5-turbo"
# api_key = "your-openai-api-key"

# Anthropic
# model = "claude-3-opus-20240229"
# api_key = "your-anthropic-api-key"

# Gemini
# model = "gemini-pro"
# api_key = "your-gemini-api-key"
""")
    print(f"talkcode config initialized at {CONFIG_PATH}")

def get_ai_config():
    config = load_config()
    ai_config = config.get("azure_openai", {})
    validate_ai_config(ai_config)
    return ai_config

def validate_ai_config(config):
    provider = config.get("provider", "azure").lower()

    required_keys = {
        "azure": ["endpoint", "deployment", "api_version", "api_key"],
        "openai": ["deployment", "api_key"],
        "anthropic": ["model", "api_key"],
        "gemini": ["model", "api_key"]
    }

    if provider not in required_keys:
        raise ValueError(f"Unsupported provider: {provider}")

    missing = [key for key in required_keys[provider] if key not in config]
    if missing:
        raise ValueError(f"Missing {provider} config keys: {missing}")
