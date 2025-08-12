<div align="center">

```
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║    ██████╗ ██╗      ██████╗ ██████╗  █████╗ ██╗   ║
    ║   ██╔════╝ ██║     ██╔═══██╗██╔══██╗██╔══██╗██║   ║
    ║   ██║  ███╗██║     ██║   ██║██████╔╝███████║██║   ║
    ║   ██║   ██║██║     ██║   ██║██╔══██╗██╔══██║██║   ║
    ║   ╚██████╔╝███████╗╚██████╔╝██████╔╝██║  ██║██║   ║
    ║    ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ║
    ║                                                   ║
    ║   ██████╗ ███████╗███╗   ██╗██╗███████╗           ║
    ║  ██╔════╝ ██╔════╝████╗  ██║██║██╔════╝           ║
    ║  ██║  ███╗█████╗  ██╔██╗ ██║██║█████╗             ║
    ║  ██║   ██║██╔══╝  ██║╚██╗██║██║██╔══╝             ║
    ║  ╚██████╔╝███████╗██║ ╚████║██║███████╗           ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝╚══════╝           ║
    ║                                                   ║
    ║        🌟 The Complete AI Agent Framework 🌟      ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
```

# **GlobalGenie**
### *The Complete AI Agent Framework*

Build intelligent, autonomous agents with memory, reasoning, and multi-modal capabilities

[![PyPI version](https://img.shields.io/pypi/v/globalgenie?color=1a365d&style=for-the-badge)](https://pypi.org/project/globalgenie/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-1a365d?style=for-the-badge)](https://www.python.org/downloads/)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-d69e2e?style=for-the-badge)](https://opensource.org/licenses/MPL-2.0)
[![Documentation](https://img.shields.io/badge/docs-globalgenie.com-1a365d?style=for-the-badge)](https://docs.globalgenie.com)

</div>

## What is GlobalGenie?

GlobalGenie is a comprehensive framework for building sophisticated AI agents that can think, remember, and act autonomously. Unlike simple chatbots, GlobalGenie agents are equipped with:

<div align="center">

| Feature | Description |
|---------|-------------|
| 🧠 **Advanced Reasoning** | Multi-step thinking and problem-solving capabilities |
| 💾 **Persistent Memory** | Long-term memory across conversations and sessions |
| 📚 **Knowledge Integration** | RAG capabilities with vector databases and document processing |
| 🛠️ **Tool Integration** | Seamless integration with APIs, databases, and external services |
| 👥 **Multi-Agent Collaboration** | Coordinate multiple agents for complex workflows |
| 🎯 **Goal-Oriented Behavior** | Autonomous task completion with planning and execution |

</div>

## Quick Start

### Installation

```bash
pip install globalgenie
```

### Your First Agent

Create an intelligent agent in just a few lines:

- **Model Agnostic**: GlobalGenie provides a unified interface to 23+ model providers, no lock-in.
- **Highly performant**: Agents instantiate in **~3μs** and use **~6.5Kib** memory on average.
- **Reasoning is a first class citizen**: Reasoning improves reliability and is a must-have for complex autonomous agents. GlobalGenie supports 3 approaches to reasoning: Reasoning Models, `ReasoningTools` or our custom `chain-of-thought` approach.
- **Natively Multi-Modal**: GlobalGenie Agents are natively multi-modal, they accept text, image, and audio as input and generate text, image, and audio as output.
- **Advanced Multi-Agent Architecture**: GlobalGenie provides an industry leading multi-agent architecture (**Agent Teams**) with reasoning, memory, and shared context.
- **Built-in Agentic Search**: Agents can search for information at runtime using 20+ vector databases. GlobalGenie provides state-of-the-art Agentic RAG, **fully async and highly performant.**
- **Built-in Memory & Session Storage**: Agents come with built-in `Storage` & `Memory` drivers that give your Agents long-term memory and session storage.
- **Structured Outputs**: GlobalGenie Agents can return fully-typed responses using model provided structured outputs or `json_mode`.
- **Pre-built FastAPI Routes**: After building your Agents, serve them using pre-built FastAPI routes. 0 to production in minutes.
- **Monitoring**: Monitor agent sessions and performance in real-time on [globalgenie.com](https://app.globalgenie.com).

## Installation

```shell
pip install -U globalgenie
```

## Example - Reasoning Agent

Let's build a Reasoning Agent to get a sense of GlobalGenie's capabilities.

Save this code to a file: `reasoning_agent.py`.

```python
from globalgenie.agent import Agent
from globalgenie.models.anthropic import Claude
from globalgenie.tools.reasoning import ReasoningTools
from globalgenie.tools.yfinance import YFinanceTools

agent = Agent(
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[
        ReasoningTools(add_instructions=True),
        YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True),
    ],
    instructions=[
        "Use tables to display data",
        "Only output the report, no other text",
    ],
    markdown=True,
)
agent.print_response(
    "Write a report on NVDA",
    stream=True,
    show_full_reasoning=True,
    stream_intermediate_steps=True,
)
```

Then create a virtual environment, install dependencies, export your `ANTHROPIC_API_KEY` and run the agent.

```shell
uv venv --python 3.12
source .venv/bin/activate

uv pip install globalgenie anthropic yfinance

export ANTHROPIC_API_KEY=sk-ant-api03-xxxx

python reasoning_agent.py
```

We can see the Agent is reasoning through the task, using the `ReasoningTools` and `YFinanceTools` to gather information. This is how the output looks like:



## Example - Multi Agent Teams



```python
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat
from globalgenie.tools.web import WebSearchTools

# Create an agent with web search capabilities
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    tools=[WebSearchTools()],
    instructions="You are a helpful research assistant. Always verify information with web searches."
)

# Start a conversation
response = agent.run("What are the latest developments in quantum computing?")
print(response.content)
```

### Agent with Memory and Knowledge

Build stateful agents that remember and learn:

```python
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat
from globalgenie.memory import SqliteMemory
from globalgenie.knowledge import PDFKnowledgeBase
from globalgenie.tools.calculator import CalculatorTools

# Create an agent with persistent memory and knowledge
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    memory=SqliteMemory(
        table_name="agent_memory",
        db_file="agent_sessions.db"
    ),
    knowledge=PDFKnowledgeBase(
        path="documents/",
        vector_db="chroma"
    ),
    tools=[CalculatorTools()],
    instructions="You are a knowledgeable assistant with access to documents and calculation tools."
)

# The agent remembers previous conversations
response = agent.run("Analyze the financial report from last quarter")
print(response.content)
```

## Core Features

### 🤖 Intelligent Agents
- **Multi-Model Support**: OpenAI, Anthropic, Google, Ollama, and 20+ providers
- **Reasoning Capabilities**: Chain-of-thought, tree-of-thought, and custom reasoning patterns
- **Autonomous Decision Making**: Goal-oriented behavior with planning and execution
- **Error Handling**: Robust error recovery and retry mechanisms

### 💾 Advanced Memory Systems
- **Conversation Memory**: Remember context across interactions
- **Semantic Memory**: Store and retrieve knowledge based on meaning
- **Episodic Memory**: Remember specific events and experiences
- **Memory Persistence**: SQLite, PostgreSQL, Redis, and cloud storage options

### 📚 Knowledge Integration
- **Document Processing**: PDF, Word, text, and web content ingestion
- **Vector Databases**: Chroma, Pinecone, Weaviate, and 15+ vector stores
- **RAG Capabilities**: Retrieval-augmented generation with advanced chunking
- **Knowledge Graphs**: Build and query structured knowledge representations

### 🛠️ Extensive Tool Ecosystem
- **Web Tools**: Search, scraping, and API integration
- **Database Tools**: SQL, NoSQL, and vector database operations
- **File Tools**: Read, write, and process various file formats
- **Communication Tools**: Email, Slack, Discord, and messaging platforms
- **Custom Tools**: Easy framework for building domain-specific tools

### 👥 Multi-Agent Systems
- **Agent Teams**: Coordinate multiple specialized agents
- **Workflow Orchestration**: Complex multi-step processes
- **Agent Communication**: Inter-agent messaging and collaboration
- **Role-Based Architecture**: Specialized agents for different tasks

## Architecture Overview

GlobalGenie follows a modular architecture that makes it easy to build and scale AI applications:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Agents      │    │     Models      │    │     Tools       │
│                 │    │                 │    │                 │
│ • Reasoning     │◄──►│ • OpenAI        │◄──►│ • Web Search    │
│ • Planning      │    │ • Anthropic     │    │ • Databases     │
│ • Execution     │    │ • Google        │    │ • APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Memory      │    │   Knowledge     │    │   Workflows     │
│                 │    │                 │    │                 │
│ • Conversations │    │ • Documents     │    │ • Multi-Agent   │
│ • Semantic      │    │ • Vector DBs    │    │ • Orchestration │
│ • Episodic      │    │ • RAG           │    │ • State Mgmt    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Use Cases

### 🏢 Business Applications
- **Customer Support**: Intelligent chatbots with knowledge base integration
- **Data Analysis**: Automated report generation and insights
- **Content Creation**: Blog posts, documentation, and marketing materials
- **Process Automation**: Workflow automation with decision-making capabilities

### 🔬 Research & Development
- **Literature Review**: Automated research paper analysis and summarization
- **Experiment Planning**: Design and optimize experimental procedures
- **Data Processing**: Large-scale data analysis and pattern recognition
- **Knowledge Discovery**: Extract insights from unstructured data

### 🎓 Education & Training
- **Personalized Tutoring**: Adaptive learning systems
- **Content Generation**: Educational materials and assessments
- **Student Assessment**: Automated grading and feedback
- **Curriculum Planning**: Intelligent course design and optimization

## Getting Started Guide

### 1. Installation and Setup

```bash
# Install GlobalGenie
pip install globalgenie

# Install optional dependencies for specific features
pip install globalgenie[web]      # Web search and scraping tools
pip install globalgenie[docs]     # Document processing capabilities
pip install globalgenie[vector]   # Vector database integrations
pip install globalgenie[all]      # All optional dependencies
```

### 2. Configuration

Create a configuration file or set environment variables:

```python
# config.py
import os
from globalgenie.config import GlobalGenieConfig

config = GlobalGenieConfig(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_model="gpt-4",
    memory_backend="sqlite",
    vector_store="chroma"
)
```

### 3. Build Your First Agent

```python
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat

# Simple conversational agent
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    instructions="You are a helpful assistant specialized in Python programming."
)

# Interactive conversation
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break
    
    response = agent.run(user_input)
    print(f"Agent: {response.content}")
```

### 4. Add Tools and Capabilities

```python
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat
from globalgenie.tools.web import WebSearchTools
from globalgenie.tools.calculator import CalculatorTools
from globalgenie.tools.python import PythonTools

# Multi-tool agent
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    tools=[
        WebSearchTools(),
        CalculatorTools(),
        PythonTools()
    ],
    instructions="""
    You are a versatile AI assistant with access to:
    - Web search for current information
    - Calculator for mathematical operations
    - Python execution for data analysis
    
    Always use the appropriate tool for each task.
    """
)

# The agent can now search the web, calculate, and run Python code
response = agent.run("Find the current stock price of Apple and calculate its P/E ratio")
```

### 5. Add Memory and Knowledge

```python
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat
from globalgenie.memory import SqliteMemory
from globalgenie.knowledge import WebKnowledgeBase
from globalgenie.tools.web import WebSearchTools

# Agent with persistent memory and knowledge
agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    memory=SqliteMemory(
        table_name="conversations",
        db_file="agent_memory.db"
    ),
    knowledge=WebKnowledgeBase(
        urls=[
            "https://docs.python.org/3/",
            "https://pandas.pydata.org/docs/"
        ]
    ),
    tools=[WebSearchTools()],
    instructions="You are a Python expert with access to official documentation."
)

# The agent remembers previous conversations and has access to documentation
response = agent.run("How do I handle missing data in pandas DataFrames?")
```

## Advanced Features

### Multi-Agent Workflows

```python
from globalgenie.team import AgentTeam
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat
from globalgenie.tools.web import WebSearchTools
from globalgenie.tools.python import PythonTools

# Create specialized agents
researcher = Agent(
    name="researcher",
    model=OpenAIChat(id="gpt-4"),
    tools=[WebSearchTools()],
    instructions="You are a research specialist. Gather comprehensive information on given topics."
)

analyst = Agent(
    name="analyst", 
    model=OpenAIChat(id="gpt-4"),
    tools=[PythonTools()],
    instructions="You are a data analyst. Process and analyze information to extract insights."
)

writer = Agent(
    name="writer",
    model=OpenAIChat(id="gpt-4"),
    instructions="You are a technical writer. Create clear, comprehensive reports."
)

# Create a team workflow
team = AgentTeam(
    agents=[researcher, analyst, writer],
    workflow="sequential"  # researcher -> analyst -> writer
)

# Execute complex multi-agent task
result = team.run("Create a comprehensive market analysis report for electric vehicles in 2024")
```

### Custom Tool Development

```python
from globalgenie.tools import Tool
from typing import Dict, Any
import requests

class WeatherTool(Tool):
    """Custom tool for weather information"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        super().__init__(
            name="get_weather",
            description="Get current weather information for a city"
        )
    
    def run(self, city: str) -> Dict[str, Any]:
        """Get weather data for a city"""
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }

# Use custom tool
from globalgenie.agent import Agent
from globalgenie.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4"),
    tools=[WeatherTool(api_key="your-api-key")],
    instructions="You are a weather assistant. Provide detailed weather information."
)

response = agent.run("What's the weather like in New York?")
```

## Model Support

GlobalGenie supports 25+ AI model providers:

### OpenAI
- GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- DALL-E 3 for image generation
- Whisper for speech recognition

### Anthropic
- Claude 3 (Opus, Sonnet, Haiku)
- Claude 2.1, Claude Instant

### Google
- Gemini Pro, Gemini Pro Vision
- PaLM 2, Codey

### Open Source
- Ollama (Llama 2, Mistral, CodeLlama)
- Hugging Face Transformers
- Together AI

### Cloud Providers
- AWS Bedrock (Claude, Llama, Titan)
- Azure OpenAI Service
- Google Vertex AI

## Documentation

- **📖 [Complete Documentation](https://docs.globalgenie.com)** - Comprehensive guides and API reference
- **🚀 [Quick Start Guide](https://docs.globalgenie.com/quickstart)** - Get up and running in minutes
- **💡 [Examples Gallery](https://docs.globalgenie.com/examples)** - Real-world use cases and implementations
- **🛠️ [API Reference](https://docs.globalgenie.com/api)** - Detailed API documentation
- **❓ [FAQ](https://docs.globalgenie.com/faq)** - Frequently asked questions

## Community & Support

- **💬 [Discord Community](https://discord.gg/globalgenie)** - Join our active community
- **📧 Email Support** - Direct support from our team
- **🐛 [Issue Tracker](https://github.com/globalgenie-agi/globalgenie/issues)** - Report bugs and request features
- **📝 [Blog](https://blog.globalgenie.com)** - Latest updates and tutorials

## Contributing

We welcome contributions! Please see our Contributing Guide for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/globalgenie-agi/globalgenie.git
cd globalgenie

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```

## License

GlobalGenie is released under the MIT License.

## Roadmap

- **Q1 2025**: Enhanced multi-modal capabilities
- **Q2 2025**: Advanced workflow orchestration
- **Q3 2025**: Enterprise security features
- **Q4 2025**: Distributed agent systems

---

<div align="center">
  <strong>Ready to build the future with AI agents?</strong>
  
  [Get Started](https://docs.globalgenie.com/quickstart) • [View Examples](https://docs.globalgenie.com/examples) • [Join Community](https://discord.gg/globalgenie)
</div>