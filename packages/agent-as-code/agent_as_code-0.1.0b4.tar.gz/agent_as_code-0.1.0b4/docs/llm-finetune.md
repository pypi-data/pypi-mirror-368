## Managed Fine-tuning (Beta)

This document outlines the managed fine‑tuning flow. The CLI currently provides placeholders and will be expanded.

### Scope

- Managed fine‑tuning only for beta.
- Local LoRA/PEFT will be considered later.

### Datasets

- OpenAI: JSONL with messages format
- Anthropic: Messages format
- Google: Prompt/Response pairs

Validate your dataset before submitting to vendors.

### CLI Preview

```bash
# Create a fine-tune job
agent llm tune create --provider openai --base-model gpt-4o-mini --dataset ./data.jsonl

# Check job status
agent llm tune status --provider openai --job-id ft_abc123

# Promote when ready
agent llm tune promote --provider openai --job-id ft_abc123

# Diagnostics before/after fine-tuning
agent llm doctor

# Tip: you can set keys via auto-config
agent llm configure auto
```

### Status

The CLI will soon support job creation, polling, and promotion with safety checks and eval hooks.
For now, prepare datasets in the vendor’s format and use your vendor dashboard to monitor jobs.

