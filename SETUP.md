# 🚀 Setup Guide - Research Assistant Agent with LangGraph & Gemini 2.0 Flash

This guide will help you set up and configure the Research Assistant Agent for optimal performance.

## 📋 Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or higher)
- **Git** for cloning the repository
- **API Keys** for Gemini and Tavily services

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Amruth22/W1D11S2-Langgraph-ReAct-implementation.git
cd W1D11S2-Langgraph-ReAct-implementation
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

#### Option A: Use Pre-configured Keys (Quick Start)
The repository includes a `.env` file with working API keys:

```bash
# API keys are already configured - you can start using immediately!
python -m src.main --config
```

#### Option B: Use Your Own API Keys (Recommended for Production)

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Get your API keys:**

   **Gemini API Key:**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key (starts with `AIza`)

   **Tavily API Key:**
   - Visit [Tavily](https://tavily.com/)
   - Sign up for an account
   - Get your API key from the dashboard (starts with `tvly-`)

3. **Edit the .env file:**
   ```bash
   # Edit .env with your favorite editor
   nano .env
   # or
   code .env
   ```

   Update the file with your keys:
   ```env
   GEMINI_API_KEY=your_actual_gemini_key_here
   TAVILY_API_KEY=your_actual_tavily_key_here
   ```

### 5. Validate Configuration

```bash
# Test configuration
python -m src.main --config

# Expected output:
# Current Configuration:
# model: gemini-2.0-flash-exp
# temperature: 0.1
# max_tokens: 1000
# ...
# config_valid: True
```

### 6. Test Installation

```bash
# Run a simple test query
python -m src.main "What is machine learning?"

# Expected: Research workflow should start and complete successfully
```

## 🎯 Configuration Options

### Environment Variables

You can customize the agent behavior by setting these environment variables in your `.env` file:

```env
# API Keys (Required)
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key

# LLM Configuration
TEMPERATURE=0.1                    # Controls randomness (0.0-1.0)
MAX_OUTPUT_TOKENS=1000            # Maximum tokens per response
MAX_RETRIES=3                     # Maximum retry attempts

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60 # API requests per minute
```

### Advanced Configuration

For advanced users, you can modify `src/config.py` to:

- Add more trusted domains
- Adjust safety keywords
- Modify search parameters
- Configure checkpointing behavior

## 🧪 Testing Your Setup

### Basic Functionality Test

```bash
# Test basic research
python -m src.main "What are the benefits of renewable energy?"
```

### Checkpointing Test

```bash
# Test with checkpointing
python -m src.main "Climate change impacts on agriculture" --thread-id test_1

# Resume from checkpoint (if interrupted)
python -m src.main --resume --thread-id test_1

# View execution history
python -m src.main --history --thread-id test_1
```

### Safety Features Test

```bash
# Test safety validation (should handle gracefully)
python -m src.main "controversial topic test"
```

### Batch Processing Test

```bash
# Run examples
python -m src.main --examples
```

## 🔍 Troubleshooting

### Common Issues

#### 1. **API Key Errors**

```bash
ERROR: GEMINI_API_KEY not found or invalid
```

**Solution:**
- Check that `.env` file exists in the project root
- Verify API key format (Gemini keys start with `AIza`)
- Ensure no extra spaces or quotes around the key

#### 2. **Import Errors**

```bash
ModuleNotFoundError: No module named 'langgraph'
```

**Solution:**
```bash
pip install -r requirements.txt
```

#### 3. **Rate Limiting**

```bash
429 Too Many Requests
```

**Solution:**
- Reduce `RATE_LIMIT_REQUESTS_PER_MINUTE` in `.env`
- Wait a few minutes before retrying
- Check your API quota limits

#### 4. **Permission Errors**

```bash
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix file permissions
chmod 644 .env
chmod -R 755 src/
```

#### 5. **Configuration Validation Fails**

```bash
config_valid: False
```

**Solution:**
```bash
# Check configuration details
python -c "from src.config import Config; print(f'Gemini: {bool(Config.GEMINI_API_KEY)}'); print(f'Tavily: {bool(Config.TAVILY_API_KEY)}')"
```

### Debug Mode

Enable verbose output for debugging:

```bash
# Add debug prints to see what's happening
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'Gemini Key Present: {bool(os.getenv(\"GEMINI_API_KEY\"))}')
print(f'Tavily Key Present: {bool(os.getenv(\"TAVILY_API_KEY\"))}')
"
```

## 🚀 Performance Optimization

### For Better Performance

1. **Use SSD storage** for checkpointing
2. **Increase rate limits** if you have higher API quotas
3. **Adjust temperature** for more focused responses (lower = more focused)
4. **Optimize search results** by reducing `MAX_SEARCH_RESULTS`

### For Cost Optimization

1. **Reduce `MAX_OUTPUT_TOKENS`** for shorter responses
2. **Lower `MAX_RETRIES`** to avoid excessive API calls
3. **Use checkpointing** to avoid re-running completed work
4. **Monitor API usage** through provider dashboards

## 📊 Monitoring & Maintenance

### Check API Usage

```bash
# Monitor your API usage through:
# - Google AI Studio: https://aistudio.google.com/
# - Tavily Dashboard: https://tavily.com/dashboard
```

### Regular Maintenance

```bash
# Update dependencies periodically
pip install --upgrade -r requirements.txt

# Clean up old checkpoints
rm -rf checkpoints/

# Clean up old reports
rm -rf reports/
```

## 🎯 Next Steps

Once your setup is working:

1. **Explore Examples**: Run `python -m src.main --examples`
2. **Read Documentation**: Check out the main README.md
3. **Customize Configuration**: Modify `src/config.py` for your needs
4. **Integrate**: Use the programmatic API in your own projects

## 🆘 Getting Help

If you encounter issues:

1. **Check this guide** for common solutions
2. **Review the logs** for specific error messages
3. **Test with simple queries** first
4. **Verify API keys** are valid and have sufficient quota
5. **Check network connectivity** for API access

## 🎉 Success!

If you see output like this, you're ready to go:

```
Starting research workflow for: 'What is machine learning?'
============================================================
Planning research for: What is machine learning?
Plan created: Comprehensive research approach...
Searching for information...
Found 8 sources
Validating 8 sources...
Validated sources: 6 safe sources
Synthesizing research from 6 sources...
Research synthesized (confidence: 0.87)
Final safety validation...
Research completed safely

Report saved to: reports/20241218_143022_What_is_machine_learning.md
```

**Congratulations! Your Research Assistant Agent is ready for use!** 🎉

---

*For advanced usage and API integration, see the main README.md file.*