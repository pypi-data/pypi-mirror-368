# CAlita: Adaptive LLM-based Iterative Task Automation

> Inspired by the paper "Alita: Generalist Agent Enabling Scalable Agentic Reasoning with Minimal Predefinition and Maximal Self-Evolution".

CAlita is an intelligent meta-agent system that automatically invents Python scripts as tools to solve complex tasks through an iterative CodeReAct (Code Reasoning and Acting) loop. The system can analyze natural language requirements, detect capability gaps, search for external resources, generate and register executable code, and manage isolated execution environments between tasks. CAlita refer to OpenAlita，rebuild with E2B sandbox and dynamic McpBox.

## 🚀 Key Features

- **Intelligent Task Analysis**: Uses LLM-powered brainstorming to analyze tasks and detect capability gaps
- **Dynamic Code Generation**: Automatically generates self-contained Python scripts based on task specifications
- **Sandbox Execution**: Use E2B sandbox execute script and code
- **External Resource Integration**: Searches and incorporates web resources when needed
- **Iterative Refinement**: Learns from execution failures and refines solutions automatically
- **MCP Registry**: Stores and reuses successful Model Context Protocols (MCPBox)
- **Comprehensive Benchmarking**: Supports evaluation on GAIA, MathVista, and PathVQA datasets

## 🏗️ Architecture

CAlita consists of several core components:

### Core Modules

- **MangerAgent**: Central orchestrates WebAgent, McpToolAgent, McpCreationAgent 
- **McpCreationAgentPro**: More Simple and Efficient McpCreationAgent
- **McpCreationAgent**: Central coordinator that orchestrates the entire pipeline
- **MCPBrainstorm**: Analyzes tasks and generates tool specifications using LLM
- **ResearchAgent**: Performs intelligent information retrieval using LangGraph and MCP tools
- **ScriptGenerator**: Generates executable Python scripts from specifications
- **CodeRunner**: Executes scripts in E2B Sandbox
- **MCPRegistry**: Persistent storage for successful Model Context Protocols Tool to McpBox
- **Benchmark**: Evaluation framework for multiple datasets


#### Detailed Process Flow:

1. **Task Analysis**: Analyze input task and detect capability gaps
2. **Resource Gathering**: Search external resources if gaps are detected
3. **Script Generation**: Generate self-contained Python script
4. **Execution**: Run script and capture output
5. **Registration**: Store successful scripts as reusable MCPs
6. **Iteration**: Refine based on feedback if execution fails

## 📋 Prerequisites

- Python 3.13+
- Required Python packages (see installation section)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd CAlita_repo
   ```

2. **Install dependencies**:
   ```bash
   uv sync --python 3.13
   ```

3. **Set up configuration**:
   - Copy `config.yaml.example` to `config.yaml` and update the API keys:
   ```yaml
   api:
     litellm_api_key: "your-actual-litellm-api-key-here"
     openai_api_key: "your-actual-openai-api-key-here"
     anthropic_api_key: "your-actual-anthropic-api-key-here"  # If using Anthropic models
   ```
4. **Config OS ENV**:
   ```bash
     export E2B_API_KEY=XX
     export E2B_ACCESS_TOKEN=XX
     export LITELLM_API_KEY=XX 
   ```

5. **Run Calita App**:
   ```bash
     uv run calita
   ```


6. **Run McpBox  Server**:
   ```bash
     uv run calita-mcpbox
   ```

## ⚙️ Configuration

The system is configured through `config.yaml`. Key configuration sections:

### Agent Configuration
```yaml
agent:
  primary_llm: "openai/qwen3-235b-a22b"                   # Primary LLM model
  coder_llm: "openai/qwen3-coder-480b-a35b-instruct"      # Coder model
  reason_llm: "openai/qwen3-235b-a22b-thinking-2507"      # Reason model
  script_gen_prompt_template: "templates/script_template.txt"
```


### API Configuration
```yaml
api:
  litellm_api_key: "<YOUR_LITELLM_API_KEY_HERE>"  # LITELLM OpenSource API key
  litellm_api_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"   # OpenSource API endpoint
  openai_api_key: "<YOUR_OPENAI_API_KEY_HERE>"  # OpenAI API key
  openai_api_url: "https://api.openai.com/v1"   # OpenAI API endpoint
  anthropic_api_key: "<YOUR_ANTHROPIC_API_KEY_HERE>"  # Anthropic API key
  anthropic_base_url: "https://api.anthropic.com"  # Anthropic API endpoint (optional)
```

### Benchmark Configuration
```yaml
benchmark:
  gaia:
    dataset_path: "data/gaia.json"
  mathvista:
    sample_size: 100
    dataset_path: "data/mathvista.json"
  pathvqa:
    sample_size: 100
    dataset_path: "data/pathvqa.json"
```

## 🚀 Usage

### Single Task Mode

Run CAlita on a single natural language task:

```bash
uv run calita
```

Then enter your task when prompted:
```
Enter a natural language query/task: Calculate the fibonacci sequence up to 100
```

### Benchmark Mode

Run evaluation on benchmark datasets:

```bash
uv run calita
```

This will evaluate the system on GAIA, MathVista, and PathVQA datasets and output metrics including pass@1 and pass@3 scores.

### Programmatic Usage

```python
from calita.manager_agent import ManagerAgent
from calita.utils.utils import get_global_config, setup_logging

# Load configuration
config = get_global_config("config.yaml")
setup_logging(config)
# Initialize the agent
manager = ManagerAgent(config)

# Process a task
result = manager.generate("Create a function to sort a list of numbers")
print(result)
```

## 📁 Project Structure

```
CAlita_repo/
├── calita/            # src, all code 
│   ├── manager_sub_agents # manager coodinate sub agents code
│   └── mcp_creation # mcp tool create and run code 
│   └── tools # pypi eg.. tools code
│   └── utils # utility code
├── examples/      # example code 
├── mcp_config/      # MCP Server config 
├── templates/            # Prompt templates 
│   ├── brain_storm_template.txt # analysis task
│   └── script_template.txt  # ScriptGenerator create mcp tool script
│   └── final_result_template.txt  # FinalResultAgent evaluate result and formate result
│   └── mcp_tool_fetch_template.txt   # McpToolAgent fetch mcp tools
│   └── task_plan_template.txt  # TaskPlanAgent plan task
├── data/                 # Dataset files (create this directory)
│   ├── gaia.json
│   ├── mathvista.json
│   └── pathvqa.json
└── logs/                 # Log files (auto-created)
    └── CAlita.log
```

## 📊 Evaluation Metrics

The system supports comprehensive evaluation with the following metrics:

- **Pass@1**: Success rate on first attempt
- **Pass@3**: Success rate within 3 attempts
- **Dataset-specific metrics**: 
  - GAIA: Breakdown by difficulty levels (Level 1, 2, 3)
  - MathVista: Mathematical reasoning accuracy
  - PathVQA: Medical image question answering accuracy

## 🔍 Logging

Logs are automatically generated in `logs/CAlita.log`. Configure logging level in `config.yaml`:

```yaml
logging:
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  log_file: "logs/CAlita.log"
```

## Inspiration and Credits
This project is inspired by the CAlita project by CharlesQ9 and the concepts presented in the research paper "CAlita: Generalist Agent Enabling Scalable Agentic Reasoning with Minimal Predefinition and Maximal Self-Evolution".

Original CAlita Project: CharlesQ9/CAlita on GitHub
Research Paper: CAlita: Generalist Agent Enabling Scalable Agentic Reasoning with Minimal Predefinition and Maximal Self-Evolution (arXiv:2505.20286)
Full credits to the authors and contributors of these works for the foundational architecture and ideas.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the LLM API
- The research community for benchmark datasets (GAIA, MathVista, PathVQA)
- Contributors and maintainers of the open-source libraries used

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the logs in `logs/CAlita.log` for debugging
- Ensure your OpenAI API key is properly configured

