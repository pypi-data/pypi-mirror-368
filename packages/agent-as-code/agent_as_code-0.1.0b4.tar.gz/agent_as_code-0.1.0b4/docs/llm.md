## LLM Integration (Beta)

This guide explains how to use the `agent llm` namespace to configure providers, list models, run quick chats, and prepare for managed fine‑tuning.

### Quick Start

```bash
# See supported providers
agent llm providers list

# Auto-config (reads env vars if present) and sets sensible defaults
agent llm configure auto

# Or use the interactive wizard (stores keys in ~/.agent/llm.json)
agent llm configure wizard

# Or set keys non-interactively (CI-friendly)
agent llm configure set-key --provider openai --api-key $OPENAI_API_KEY
agent llm configure set-key --provider anthropic --api-key $ANTHROPIC_API_KEY
agent llm configure set-key --provider google --api-key ${GOOGLE_API_KEY:-$GEMINI_API_KEY}

# List models
agent llm models list --provider openai

# Set a default
agent llm configure set-default --provider openai --model gpt-4o-mini

# Quick chat (uses configured defaults if provider/model omitted)
agent llm chat --message "Hello!"
```

### Concepts

- **Single namespace**: All commands under `agent llm` for simplicity.
- **Top providers**: OpenAI, Anthropic, Google (Gemini) for coding tasks.
- **Credentials**: Stored in `~/.agent/llm.json`. You can also use environment variables. `configure auto` reads them automatically.
- **Agentfile**: You can reference provider and model in your Agentfile via `MODEL` and `ENV` while the CLI keeps secrets out of source control.

### Commands

- `agent llm providers list`
  - Output example:
    ```
    Available LLM providers:
      - anthropic
      - google
      - openai
    ```

- `agent llm providers list` (json-friendly one-liner)
  ```bash
  agent llm providers list | sed '1d' | awk '{print $2}'
  # anthropic
  # google
  # openai
  ```

- `agent llm models list --provider <name> [--capabilities chat,tools,vision]`
  - Output example:
    ```
    Models for provider 'openai':
      - gpt-4o-mini (ctx=128000, caps=[chat,tools,vision])
      - gpt-4o (ctx=128000, caps=[chat,tools,vision])
      - o3-mini (ctx=200000, caps=[chat,tools,reasoning])
    ```

  - With capability filter:
    ```bash
    agent llm models list --provider openai --capabilities chat,vision
    # Models for provider 'openai':
    #   - gpt-4o-mini (ctx=128000, caps=[chat,tools,vision])
    #   - gpt-4o (ctx=128000, caps=[chat,tools,vision])
    ```

- `agent llm configure auto`
  - Reads OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY/GEMINI_API_KEY
  - Persists keys and sets a default provider/model if not set

- `agent llm configure auto`
  - Reads OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY/GEMINI_API_KEY
  - Persists keys and sets a default provider/model if not set
  - Example:
    ```bash
    export GOOGLE_API_KEY=... # or GEMINI_API_KEY
    agent llm configure auto
    # Configured API keys for: google
    # Default set to google:gemini-1.5-flash
    ```

- `agent llm configure wizard`
  - Guides you to enter API keys and pick a default model.
  - Example session (user presses Enter to skip):
    ```
    LLM Configuration Wizard
    -------------------------
    We'll help you set API keys and pick a default model. Press Enter to skip any step.

    Supported providers:
      - anthropic
      - google
      - openai
    Enter API key for anthropic (or leave blank to skip):
    Enter API key for google (or leave blank to skip):
    Enter API key for openai (or leave blank to skip):
    Choose default provider (openai/anthropic/google): google
      1. gemini-1.5-pro (caps=chat,tools,vision)
      2. gemini-1.5-flash (caps=chat,tools,vision)
    Pick a model number: 2
    Default set to google:gemini-1.5-flash
    ```

- `agent llm configure set-key --provider <name> --api-key <key>`
  - Saves an API key to `~/.agent/llm.json`.
  - Example:
    ```bash
    agent llm configure set-key --provider openai --api-key $OPENAI_API_KEY
    # Saved API key for openai
    ```

- `agent llm configure set-default --provider <name> --model <model>`
  - Sets the default provider and model in `~/.agent/llm.json`.
  - Example:
    ```bash
    agent llm configure set-default --provider openai --model gpt-4o-mini
    # Default LLM set to openai:gpt-4o-mini
    ```

- `agent llm chat [--provider <name>] [--model <model>] --message <text> [--temperature 0.2]`
  - Sends a one-shot message and prints the response text. If provider/model are omitted, the configured defaults are used.
  - Google example (with defaults):
    ```bash
    agent llm chat --message "write a python code to see what is the date and time now"
    # Several ways exist to get the current date and time in Python...
    ```
  - OpenAI example:
    ```bash
    agent llm chat --provider openai --model gpt-4o-mini --message "Suggest 3 test cases for a sum(a,b) function"
    # 1) sum(2,3) -> 5
    # 2) sum(-1,1) -> 0
    # 3) sum(0,0) -> 0
    ```
  - Anthropic example:
    ```bash
    agent llm chat --provider anthropic --model claude-3-5-haiku --message "Summarize: def add(a,b): return a+b"
    # A concise function that returns the sum of two inputs a and b.
    ```

- `agent llm doctor`
  - Prints default provider/model and whether API keys are present for major providers.
  - Example:
    ```
    LLM Doctor
    ----------
    Default: google:gemini-1.5-flash
    openai: key: yes
    anthropic: key: no
    google: key: yes
    ```

- `agent llm generate-agentfile --description <text> [--output <file>]`
  - Generates a complete Agentfile from natural language description using LLM.
  - Example:
    ```bash
    agent llm generate-agentfile --description "A code review agent for Python projects" --output Agentfile
    ```

- `agent llm suggest-template --description <text>`
  - Gets intelligent template recommendation based on agent requirements.
  - Example:
    ```bash
    agent llm suggest-template --description "Real-time data processing agent with streaming"
    ```

- `agent llm generate-tests --description <text> [--test-type <type>]`
  - Generates comprehensive test cases for an agent using LLM.
  - Example:
    ```bash
    agent llm generate-tests --description "Sentiment analysis agent" --test-type comprehensive
    ```

- `agent llm optimize-agent --agent-path <path> --optimization-goal <goal>`
  - Analyzes and optimizes existing agent using LLM analysis.
  - Example:
    ```bash
    agent llm optimize-agent --agent-path ./my-agent --optimization-goal "performance"
    ```

### Fine-tuning (Managed, Beta)

The CLI surfaces placeholders for managed fine‑tuning workflows:

- `agent llm tune create --provider <name> --base-model <model> --dataset <path>`
- `agent llm tune status --provider <name> --job-id <id>`
- `agent llm tune promote --provider <name> --job-id <id>`

Detailed, provider-specific instructions will land soon. Prepare datasets in the vendor's standard format (e.g., OpenAI JSONL messages).

### LLM-Enhanced Agent Creation

The LLM integration goes beyond basic chat - it can help you create and optimize agents using AI:

#### Generate Agentfile from Natural Language

```bash
# Create an Agentfile by describing what you want
agent llm generate-agentfile --description "I need a sentiment analysis agent that can process social media posts and generate weekly reports" --output Agentfile

# This uses LLM to:
# - Analyze your requirements
# - Choose appropriate capabilities
# - Select optimal model configuration
# - Generate complete Agentfile
```

#### Get Intelligent Template Recommendations

```bash
# Let LLM suggest the best template for your needs
agent llm suggest-template --description "I need an agent for real-time data processing with streaming capabilities"

# LLM analyzes and recommends:
# - Best template (python-agent, node-agent, etc.)
# - Reasoning for the choice
# - Suggested capabilities
# - Key dependencies
```

#### Generate Comprehensive Test Cases

```bash
# Create test suites using LLM
agent llm generate-tests --description "A code review agent that analyzes Python code and suggests improvements" --test-type comprehensive

# Generates:
# - Unit test cases with input/output expectations
# - Integration test scenarios
# - Edge case handling tests
# - Error condition tests
# - Performance test scenarios
```

#### AI-Powered Agent Optimization

```bash
# Analyze and optimize existing agents
agent llm optimize-agent --agent-path ./my-agent --optimization-goal "performance"

# LLM analyzes your Agentfile and suggests:
# - Model selection improvements
# - Capability optimizations
# - Resource allocation changes
# - Cost optimizations
# - Security enhancements
```

### Examples

```bash
# OpenAI quick chat
agent llm chat --provider openai --model gpt-4o-mini --message "Write a Python function that reverses a string."

# Anthropic chat
agent llm chat --provider anthropic --model claude-3-5-haiku --message "Summarize this code block: def add(a,b): return a+b"

# Gemini chat
agent llm chat --provider google --model gemini-1.5-pro --message "Generate 3 unit tests for a Fibonacci function in Python."
```

### Top 5 LLM CLI Use Cases

1. Rapid model setup from environment
   ```bash
   export GOOGLE_API_KEY=... && agent llm configure auto && agent llm doctor
   ```

2. Pick the right model for a task
   ```bash
   agent llm models list --provider openai --capabilities chat,tools
   ```

3. One-shot prompt experiments (defaults)
   ```bash
   agent llm chat --message "Give 3 naming ideas for a code refactoring tool"
   ```

4. CI-friendly key management
   ```bash
   agent llm configure set-key --provider anthropic --api-key $ANTHROPIC_API_KEY
   agent llm configure set-default --provider anthropic --model claude-3-5-haiku
   ```

5. Project bootstrap and validation
   ```bash
   agent init my-agent && cd my-agent
   agent llm providers list && agent llm doctor
   ```

### Complete LLM-Enhanced Agent Creation Workflow

Here's how to use the LLM commands to create agents more intelligently:

#### 1. Get Template Recommendations
```bash
# Let LLM suggest the best starting point
agent llm suggest-template --description "I need an agent that can analyze customer feedback from multiple channels and generate actionable insights"
```

#### 2. Generate Agentfile from Requirements
```bash
# Create Agentfile using natural language
agent llm generate-agentfile --description "Customer feedback analysis agent with sentiment detection, topic modeling, and report generation capabilities" --output Agentfile
```

#### 3. Initialize Agent Project
```bash
# Create the project structure
agent init customer-feedback-agent --template python-agent
cd customer-feedback-agent
```

#### 4. Generate Test Suite
```bash
# Create comprehensive tests using LLM
agent llm generate-tests --description "Customer feedback analysis agent" --test-type comprehensive
```

#### 5. Build and Test
```bash
# Build the agent
agent build -t customer-feedback-agent:latest .

# Test functionality
agent test customer-feedback-agent:latest
```

#### 6. Optimize Based on Usage
```bash
# After some usage, optimize for performance
agent llm optimize-agent --agent-path . --optimization-goal "performance"
```

This workflow demonstrates how LLM integration makes agent creation more intelligent and user-friendly, reducing the need for deep technical knowledge while maintaining the power and flexibility of the framework.

### 5 More Advanced Use Cases for Agentic Workflows

1. Multi-provider fallback script (simple router)
   ```bash
   prompt="Summarize last release notes in 3 bullets"
   agent llm chat --provider openai --model gpt-4o-mini --message "$prompt" || \
   agent llm chat --provider anthropic --model claude-3-5-haiku --message "$prompt" || \
   agent llm chat --provider google --model gemini-1.5-flash --message "$prompt"
   ```

2. Capability-driven selection with default promotion
   ```bash
   chosen=$(agent llm models list --provider google --capabilities chat,tools | awk '/^-/{print $2; exit}')
   if [ -n "$chosen" ]; then
     agent llm configure set-default --provider google --model "$chosen"
   fi
   agent llm chat --message "Draft a README outline for a Python microservice"
   ```

3. Structured outputs guardrail (retry until JSON)
   ```bash
   prompt='Return a JSON object with keys: title, priority, items (list of strings)'
   for i in 1 2 3; do
     out=$(agent llm chat --message "$prompt") && echo "$out" | python -c 'import sys,json;json.loads(sys.stdin.read());print("ok")' && break
     echo "Retry $i due to invalid JSON..."
   done
   ```

4. Batch task generation for agents (seed test suites)
   ```bash
   cat > tasks.txt << 'EOF'
   Create 5 end-to-end tests for a login flow
   Propose 3 strategies to cache API responses
   Design a prompt template for robust JSON extraction
   EOF

   while IFS= read -r task; do
     echo "==> $task"
     agent llm chat --message "$task"
     echo
   done < tasks.txt
   ```

5. Pre-flight checks in CI before agent build
   ```bash
   agent llm doctor | tee llm_doctor.txt
   if grep -q "key: no" llm_doctor.txt; then
     echo "Missing LLM keys; aborting build" >&2; exit 1
   fi
   agent llm models list --provider openai --capabilities chat | grep -q "- gpt-4o-mini" || {
     echo "Expected model not available; aborting" >&2; exit 1; }
   ```

### Troubleshooting

- Missing API key
  - Error: `... API key not configured ...`
  - Fix: Run `agent llm configure wizard` or `agent llm configure set-key ...`.

- Missing packages
  - The CLI bundles OpenAI, Anthropic, and Google SDKs by default. If your environment is missing these, reinstall: `pip install -e agent-as-code`.

### Best Practices

- Store secrets outside of source control (in `~/.agent/llm.json` or env vars).
- Use `--capabilities` filter to find models with tool-calling or vision.
- Start with small, cost-effective models for dev; promote larger models for prod.


