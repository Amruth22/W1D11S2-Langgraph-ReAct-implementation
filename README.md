# Research Assistant Agent with LangGraph & Gemini 2.0 Flash 
A sophisticated research assistant that combines **LangGraph** orchestration with **Gemini 2.0 Flash** for fast, cost-effective research with built-in safety guardrails and self-improvement capabilities.

## Architecture Overview

**LangGraph** orchestrates a stateful graph with nodes for reasoning, acting, and safety validation. **Gemini 2.0 Flash** serves as the LLM for fast, cost-effective inference. The agent follows ReAct pattern with planning layer and reflexion for self-improvement.

### Core Components

- **State Management**: `TypedDict` with research_query, plan, sources, draft, safety_checks
- **Graph Nodes**: `plan_node` → `search_node` → `validate_node` → `synthesize_node` → `safety_node`
- **LLM Integration**: `ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.1)`
- **Tools**: `TavilySearchTool` for web search, `StructuredOutputParser` for formatted responses
- **Safety Guardrails**: URL whitelist validation, content filtering, rate limiting
- **Conditional Edges**: Routes based on safety validation (safe→continue, unsafe→escalate, retry→reflexion)
- **Checkpointing**: `MemorySaver` for state persistence, enables interruption/resumption
- **Reflexion Loop**: Failed attempts trigger self-critique node that updates plan before retry

## Quick Start

### Installation

```bash
# Clone the CLI-only version
git clone -b cli-only https://github.com/Amruth22/W1D11S2-Langgraph-ReAct-implementation.git
cd W1D11S2-Langgraph-ReAct-implementation

# Install dependencies
pip install -r requirements.txt

# API keys are already configured in .env file
# For your own setup: cp .env.example .env and edit with your keys
```

### Environment Setup

The API keys are already configured in the `.env` file:

```env
GEMINI_API_KEY=AIzaSyCeQeHPZYUl2iZVMfNCs1hC3FeO23pkRag
TAVILY_API_KEY=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
```

For your own setup, copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### Configuration Validation

Test your configuration:

```bash
# Check if API keys are properly loaded
python -m src.main --config

# Test with a simple query
python -m src.main "What is artificial intelligence?"
```

### Basic Usage

```python
import asyncio
from src.graph import research_query

async def main():
    result = await research_query("What are the latest developments in quantum computing?")
    print(result['draft'])

asyncio.run(main())
```

### Command Line Interface

```bash
# Basic research
python -m src.main "What are the latest developments in AI?"

# With checkpointing
python -m src.main "Climate change impacts" --thread-id my_research_1

# Resume from checkpoint
python -m src.main --resume --thread-id my_research_1

# Show execution history
python -m src.main --history --thread-id my_research_1

# Show configuration
python -m src.main --config

# Run examples
python -m src.main --examples
```

## Workflow Architecture

```mermaid
graph TD
    A[Start] --> B[Plan Node]
    B --> C{Planning Success?}
    C -->|Yes| D[Search Node]
    C -->|No| R[Reflexion Node]
    
    D --> E{Sources Found?}
    E -->|Yes| F[Validate Node]
    E -->|No| R
    
    F --> G{Sources Safe?}
    G -->|Yes| H[Synthesize Node]
    G -->|No| R
    
    H --> I{Synthesis Success?}
    I -->|Yes| J[Safety Node]
    I -->|No| R
    
    J --> K{Final Safety Check?}
    K -->|Safe| L[End - Success]
    K -->|Unsafe| R
    
    R --> M{Retry Available?}
    M -->|Yes| B
    M -->|No| N[End - Max Retries]
```

## Core Features

### 1. ReAct Pattern Implementation

- **Reasoning**: Planning and synthesis nodes analyze and plan research
- **Acting**: Search node executes queries and gathers information
- **Observation**: Validation nodes assess results and safety

### 2. Safety Guardrails

```python
# URL Validation
trusted_domains = {
    "wikipedia.org", "arxiv.org", "pubmed.ncbi.nlm.nih.gov",
    "scholar.google.com", "ieee.org", "nature.com", "science.org",
    "nvidia.com", "techpowerup.com", "reddit.com"
}

# Content Moderation
blocked_keywords = ["violence", "hate", "harassment", "illegal", "harmful"]

# Rate Limiting
rate_limiter = TokenBucket(capacity=60, refill_rate=1.0)
```

### 3. Reflexion & Self-Improvement

When failures occur, the agent:
1. Analyzes what went wrong
2. Identifies specific issues
3. Suggests improvements
4. Revises the research plan
5. Retries with updated approach (max 3 attempts)

### 4. State Persistence

```python
# Checkpointing enables resumption
workflow = ResearchWorkflow()
result = await workflow.run_research(query, thread_id="my_research")

# Resume later
resumed_result = await workflow.resume_from_checkpoint("my_research")
```

### 5. Automatic Report Saving

```python
# Reports are automatically saved to ./reports/ directory
# Filename format: YYYYMMDD_HHMMSS_[thread_id_]query.md

# Example saved file: 20241218_143022_ai_research_What_are_the_latest_developments_in_AI.md
```

## Project Structure

```
W1D11S2-Langgraph-ReAct-implementation/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── state.py             # State definitions (TypedDict)
│   ├── safety.py            # Safety validation components
│   ├── tools.py             # Tavily & Gemini integrations
│   ├── nodes.py             # LangGraph nodes implementation
│   ├── graph.py             # Workflow orchestration
│   └── main.py              # CLI application
├── examples/
│   └── basic_usage.py       # Usage examples
├── tests/
│   └── test_basic.py        # Basic tests
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Advanced Usage

### Custom Workflow Configuration

```python
from src.graph import ResearchWorkflow
from src.config import Config

# Customize configuration
Config.MAX_RETRIES = 5
Config.TEMPERATURE = 0.2
Config.MAX_SEARCH_RESULTS = 15

# Create workflow with custom settings
workflow = ResearchWorkflow()
result = await workflow.run_research("Your query here")
```

### Batch Research Processing

```python
import asyncio
from src.graph import research_query

async def batch_research(queries):
    tasks = []
    for i, query in enumerate(queries):
        task = research_query(query, thread_id=f"batch_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

# Usage
queries = [
    "Latest AI developments",
    "Climate change solutions", 
    "Quantum computing breakthroughs"
]

results = await batch_research(queries)
```

## Testing

```bash
# Run basic tests
python tests/test_basic.py

# Run with pytest (if installed)
pytest tests/

# Run examples
python examples/basic_usage.py
```

## Performance & Optimization

### Token Efficiency
- **Differential Editing**: Uses structured parsing to minimize token usage
- **Selective Content**: Only processes relevant search results
- **Caching**: Checkpointing reduces redundant processing

### Rate Limiting
- **Token Bucket**: Prevents API rate limit violations
- **Adaptive Delays**: Automatically handles rate limit responses
- **Concurrent Safety**: Thread-safe rate limiting implementation

## Security Features

### Content Safety
- **Multi-layer Validation**: URL, content, and output validation
- **Keyword Filtering**: Blocks harmful content patterns
- **Confidence Scoring**: Assesses safety confidence levels

### Data Privacy
- **No Persistent Storage**: Research data not permanently stored (except reports)
- **API Key Security**: Secure handling of authentication
- **Audit Logging**: Tracks safety violations and errors

## API Version Available

For a full-featured version with FastAPI, authentication, and audit logging, check out the `main` branch:

```bash
git checkout main
```

The API version includes:
- REST API endpoints
- User authentication
- Audit logging
- Background research execution
- Web interface

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Check configuration
   python -m src.main --config
   ```

2. **Rate Limiting**
   ```python
   # Adjust rate limits in config.py
   RATE_LIMIT_REQUESTS_PER_MINUTE = 30  # Reduce if needed
   ```

3. **Memory Issues**
   ```python
   # Reduce search results
   MAX_SEARCH_RESULTS = 5
   MAX_OUTPUT_TOKENS = 500
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **LangGraph** for workflow orchestration
- **Google Gemini** for fast LLM inference
- **Tavily** for reliable web search
- **ReAct Pattern** research for the architectural foundation

---

**Built using LangGraph & Gemini 2.0 Flash - CLI Version**
