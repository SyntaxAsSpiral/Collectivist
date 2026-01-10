---
id: collectivist-config
created: 2026-01-01T15:23:47.603-08:00
modified: 2026-01-01T21:52:08.221-08:00
status: example
---

# 💮 Collectivist Configuration

This is a Markdown-embedded configuration example. You can use this format in Obsidian vaults or any Markdown file.

## Configuration

```yaml
# LLM Configuration
llm_provider: lmstudio
llm_model: llama3.1-8b-instruct
# llm_api_key: your-api-key-here
# llm_base_url: https://custom-endpoint.com/v1
```

## Provider Examples

### Local Models (Recommended)

```yaml
# LMStudio (No API key needed)
llm_provider: lmstudio
llm_model: llama-3.1-8b-instruct-q4_0

# Ollama
llm_provider: ollama
llm_model: llama3.1:8b-instruct-q4_0
```

### Cloud Models

```yaml
# OpenAI
llm_provider: openai
llm_api_key: sk-your-openai-key
llm_model: gpt-4o-mini

# Anthropic
llm_provider: anthropic
llm_api_key: sk-ant-your-anthropic-key
llm_model: claude-3-haiku-20240307
```

## Notes

- Only the first ````yaml` code block is parsed
- Frontmatter and surrounding Markdown are ignored
- This format is perfect for Obsidian vault configuration
- Changes are version-controlled with your notes