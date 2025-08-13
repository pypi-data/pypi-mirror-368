
## Talkcode

**Talk to your legacy Python codebase using AI and static analysis.**  
`talkcode` helps developers explore, understand, and query large codebases using natural language and intelligent indexing.


## 🚀 What Is It?

`talkcode` is a command-line tool that combines static analysis with AI to make legacy Python codebases more accessible. Whether you're onboarding a new team member or reverse-engineering a complex system, `talkcode` lets you ask questions like:

- “Where is `process_order()` used?”
- “What does `UserManager` depend on?”
- “Show me all functions that modify global state.”

---

## 🔍 Features

- 📦 Static analysis of Python codebases  
- 🔍 Function and class indexing  
- 🔁 Call flow tracing  
- 🔑 Keyword-based code search  
- 🤖 Optional AI integration for natural language Q&A  
- 🖥️ Terminal UI powered by [`textual`]

---

## 📦 Installation

```bash
pip install talkcode
```

---

## 🛠️ Usage

```bash
talkcode init
talkcode index --path /path/to/codebase
talkcode chat --ai
talkcode ui --ai
```

---

## 🤖 AI Integration

Enable AI-powered answers with:

```bash
talkcode chat --ai
```

### Supported Providers

- ✅ Azure OpenAI

### Coming Soon

- 🔜 Google Gemini  
- 🔜 Anthropic Claude

To configure Azure OpenAI, create a config file at:

```toml
# ~/.talkcode/config.toml

[azure]
provider = "azure"
endpoint = "https://your-resource-name.openai.azure.com/"
deployment = "your-model-deployment-name"
api_version = "2023-07-01-preview"
api_key = "your-azure-openai-api-key"
```

---

## 🖥️ Textual UI

Launch the interactive terminal UI:

```bash
talkcode ui
```

Enable AI in the UI:

```bash
talkcode ui --ai
```


## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).  
You are free to use, modify, and distribute this software with proper attribution.

---

## 💬 Example Responses

Here are anonymized examples of the kinds of insights `talkcode` can generate:

### 🔗 Dependencies

```text
This module depends on:
  - A secrets manager client for secure credential access
  - A GPT-based AI interface for natural language processing
```

### 📡 Downstream Consumers

```text
This component is invoked by:
  - A markdown conversion utility that formats analysis results
  - An evaluation module that scores AI-generated outputs
```

### 🧠 AI-Powered Answers

```text
Q: What does the authentication handler rely on?
A: It depends on a token validator, a configuration loader, and a secrets manager.

Q: Which modules call the data transformation pipeline?
A: The pipeline is triggered by the ingestion service and the reporting engine.
```
