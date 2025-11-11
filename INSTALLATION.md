# Installation and Setup Guide

Complete guide for setting up the JAX-CTSM Translation Agents.

## System Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 500MB for installation + space for logs/output

## Prerequisites

1. **Python Installation**
   ```bash
   python3 --version  # Should be 3.9+
   ```

2. **Anthropic API Key**
   - Sign up at https://console.anthropic.com/
   - Create an API key
   - Keep it secure!

3. **Access to CTSM and jax-ctsm**
   - CTSM repository: `/burg-archive/home/mck2199/CTSM`
   - jax-ctsm repository: `/burg-archive/home/mck2199/jax-ctsm`

## Installation Steps

### Step 1: Navigate to Directory

```bash
cd /burg-archive/home/mck2199/jax-agents
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

### Step 3: Install Package

```bash
# Install in development mode
pip install -e .

# This will install:
# - anthropic (Claude API client)
# - python-dotenv (environment variables)
# - pyyaml (configuration)
# - pydantic (data validation)
# - rich (beautiful console output)
# - tenacity (retry logic)
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your favorite editor
```

In `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxx  # Your actual API key
LOG_LEVEL=INFO
```

### Step 5: Verify Installation

```bash
# Test import
python3 -c "from jax_agents import OrchestratorAgent; print('✓ Installation successful!')"

# Check version
python3 -c "import jax_agents; print(f'jax-agents version: {jax_agents.__version__}')"
```

## Configuration

### Default Configuration

The default `config.yaml` is already configured for typical use:

```yaml
llm:
  model: "claude-sonnet-4-20250514"  # Claude 4.5 Sonnet
  temperature: 0.0  # Deterministic
  max_tokens: 4000

paths:
  ctsm_root: "../CTSM"
  jax_ctsm_root: "../jax-ctsm"
  output_dir: "../jax-ctsm/src/jax_ctsm"
```

### Custom Configuration

To customize, edit `config.yaml`:

```bash
nano config.yaml
```

Common changes:
- **Paths**: Update if CTSM/jax-ctsm are in different locations
- **Temperature**: Increase (e.g., 0.1) for more creative translations
- **Max Tokens**: Increase for longer modules
- **Cost Limits**: Set budget constraints

## Verification

### Quick Test

Run the analysis example to verify everything works:

```bash
# This will analyze a Fortran module
# Cost: ~$0.05-0.10
python3 examples/analyze_module.py
```

Expected output:
```
📊 Analyzing Fortran module: CNPhenologyMod.F90
Running structural analysis...
🤖 Static Analysis is thinking...
✓ Analysis complete!
  - Found X subroutines
  - Found Y data types
  - Found Z module dependencies
```

### Run Full Example

```bash
# This will convert a module
# Cost: ~$0.30-1.00
python3 examples/convert_single_module.py
```

## Troubleshooting

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'jax_agents'`

**Solution**:
```bash
# Make sure you're in the right directory
cd /burg-archive/home/mck2199/jax-agents

# Reinstall
pip install -e .
```

### Issue: API Key Error

**Error**: `ValueError: ANTHROPIC_API_KEY not found in environment`

**Solution**:
```bash
# Check .env file exists
ls -la .env

# If not, create it
cp .env.example .env
nano .env  # Add your API key
```

### Issue: Import Errors

**Error**: `ImportError: cannot import name 'X'`

**Solution**:
```bash
# Update dependencies
pip install --upgrade anthropic python-dotenv pyyaml pydantic rich tenacity
```

### Issue: Permission Denied

**Error**: `PermissionError: [Errno 13] Permission denied: 'logs/'`

**Solution**:
```bash
# Create logs directory
mkdir -p logs
chmod 755 logs

# Create output directory
mkdir -p output
chmod 755 output
```

### Issue: High API Costs

**Warning**: Unexpected high costs

**Solution**:
1. Start with small modules
2. Set cost limits in config.yaml
3. Monitor token usage:
   ```python
   cost = agent.get_cost_estimate()
   print(f"Current: ${cost['total_cost_usd']:.4f}")
   ```

## Directory Structure After Installation

```
jax-agents/
├── .env                       # Your API key (DO NOT COMMIT!)
├── .gitignore                 # Git ignore file
├── config.yaml                # Configuration
├── pyproject.toml             # Package definition
├── README.md                  # Main documentation
├── QUICKSTART.md              # Quick start guide
├── ARCHITECTURE.md            # Architecture details
├── INSTALLATION.md            # This file
│
├── src/jax_agents/            # Source code
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── orchestrator.py        # Orchestrator agent
│   ├── static_analysis.py     # Static analysis agent
│   ├── translator.py          # Translator agent
│   ├── prompts/               # Prompt templates
│   └── utils/                 # Utilities
│
├── examples/                  # Example scripts
│   ├── convert_single_module.py
│   ├── analyze_module.py
│   ├── translate_with_context.py
│   └── batch_conversion.py
│
├── logs/                      # Log files (created on first run)
├── output/                    # Output files (created on first run)
└── venv/                      # Virtual environment (if created)
```

## First Steps After Installation

1. **Read the Quickstart**
   ```bash
   cat QUICKSTART.md
   ```

2. **Review an Example**
   ```bash
   cat examples/analyze_module.py
   ```

3. **Try Analysis Only** (low cost)
   ```bash
   python3 examples/analyze_module.py
   ```

4. **Try Full Conversion** (higher cost)
   ```bash
   python3 examples/convert_single_module.py
   ```

5. **Review Generated Code**
   ```bash
   ls -l output/
   cat output/*.py
   ```

## Development Setup

If you plan to modify the agents:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# This adds:
# - pytest (testing)
# - black (formatting)
# - ruff (linting)
# - mypy (type checking)
```

### Run Tests

```bash
pytest tests/ -v
```

### Format Code

```bash
black src/
```

### Lint Code

```bash
ruff check src/
```

## Updating

To update the package:

```bash
cd /burg-archive/home/mck2199/jax-agents
git pull  # If using git
pip install -e . --upgrade
```

## Uninstallation

To remove the package:

```bash
pip uninstall jax-agents

# Optionally remove virtual environment
rm -rf venv/

# Optionally remove generated files
rm -rf logs/ output/
```

## Getting Help

- **Documentation**: See `README.md` and `ARCHITECTURE.md`
- **Examples**: Check `examples/` directory
- **Logs**: Review `logs/` for detailed information
- **Issues**: Check API key, paths, and permissions

## Next Steps

After successful installation:

1. ✅ Review `QUICKSTART.md` for usage examples
2. ✅ Read `ARCHITECTURE.md` to understand the system
3. ✅ Try `examples/analyze_module.py` first
4. ✅ Convert a simple module
5. ✅ Review and validate the output
6. ✅ Iterate and improve

---

**Ready to convert CTSM to JAX! 🚀**

Installation Date: October 2025

