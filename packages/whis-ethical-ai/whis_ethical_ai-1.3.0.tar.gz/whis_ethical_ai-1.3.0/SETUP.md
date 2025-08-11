# Development Environment Setup Guide

This guide provides step-by-step instructions for setting up a development environment for the Ethical AI Validator project on Linux-based systems (including GitHub Codespaces and Ubuntu).

## Prerequisites

Before starting, ensure you have the following installed:
- **Git** (for version control)
- **Python 3.8 or higher** (recommended: Python 3.11)
- **pip** (Python package installer)

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/whis-19/ethical-ai.git

# Navigate to the project directory
cd ethical-ai
```

## Step 2: Verify Python Installation

Ensure you have Python 3.8 or higher installed:

```bash
# Check Python version
python3 --version

# If Python 3 is not available, install it
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# On CentOS/RHEL:
sudo yum install python3 python3-pip

# On macOS (using Homebrew):
brew install python3
```

## Step 3: Create and Activate Virtual Environment

Creating a virtual environment isolates project dependencies:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
# .venv\Scripts\activate

# Verify activation (you should see (.venv) in your prompt)
which python
```

## Step 4: Install Dependencies

Install all required packages:

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e .[dev]

# Verify installation
pip list
```

## Step 5: Configure Git

Set up Git for the project:

```bash
# Configure Git user (if not already set)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Verify remote repository
git remote -v

# Create and switch to a development branch
git checkout -b develop
```

## Step 6: Set Up Testing Environment

Configure pytest for testing:

```bash
# Verify pytest installation
pytest --version

# Run initial test suite
pytest

# Run tests with coverage
pytest --cov=ethical_ai_validator --cov-report=html

# Check coverage percentage
pytest --cov=ethical_ai_validator --cov-report=term-missing
```

## Step 7: Configure Code Quality Tools

Set up linting and formatting tools:

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files

# Format code with Black
black .

# Check code with Flake8
flake8 .

# Type checking with MyPy
mypy src/ethical_ai_validator/
```

## Step 8: VS Code Configuration

### Install Recommended Extensions

1. Open VS Code in the project directory:
   ```bash
   code .
   ```

2. Install the following extensions:
   - **Python** (ms-python.python)
   - **Pylance** (ms-python.vscode-pylance)
   - **Python Test Explorer** (littlefoxteam.vscode-python-test-adapter)
   - **Python Docstring Generator** (njpwerner.autodocstring)
   - **autoDocstring** (njpwerner.autodocstring)

### Configure VS Code Settings

The project includes a `.vscode/settings.json` file with optimal settings for:
- Python interpreter path
- Linting with Flake8
- Formatting with Black
- Pytest integration
- Type checking with MyPy

## Step 9: Verify Setup

Run the following commands to verify your setup:

```bash
# Check Python version
python --version

# Verify virtual environment
which python

# Check installed packages
pip list

# Run tests
pytest --version
pytest -v

# Check code coverage
pytest --cov=ethical_ai_validator --cov-report=term

# Verify Git configuration
git status
git remote -v
```

## Step 10: Development Workflow

### Daily Development Routine

1. **Start your day:**
   ```bash
   cd ethical-ai
   source .venv/bin/activate
   git pull origin main
   ```

2. **Before making changes:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **During development:**
   ```bash
   # Run tests frequently
   pytest

   # Format code
   black .

   # Check linting
   flake8 .

   # Type checking
   mypy src/ethical_ai_validator/
   ```

4. **Before committing:**
   ```bash
   # Run all quality checks
   pre-commit run --all-files

   # Run full test suite
   pytest --cov=ethical_ai_validator --cov-report=html
   ```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Python version not found
```bash
# Solution: Install Python 3.8+
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip
```

#### Issue: Virtual environment not activating
```bash
# Solution: Check if venv is created properly
python3 -m venv .venv --clear
source .venv/bin/activate
```

#### Issue: Package installation fails
```bash
# Solution: Upgrade pip and try again
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Issue: Pytest not found
```bash
# Solution: Install pytest explicitly
pip install pytest pytest-cov pytest-mock
```

#### Issue: VS Code not recognizing Python interpreter
1. Open Command Palette (Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose the interpreter from `.venv/bin/python`

#### Issue: Git authentication fails
```bash
# Solution: Set up SSH keys or use HTTPS
git remote set-url origin https://github.com/whis-19/ethical-ai.git
```

## Environment Variables

Create a `.env` file for local development:

```bash
# Create .env file
touch .env

# Add environment variables
echo "DEBUG=True" >> .env
echo "LOG_LEVEL=INFO" >> .env
echo "TEST_MODE=True" >> .env
```

## GitHub Codespaces Setup

If using GitHub Codespaces:

1. **Open in Codespace:**
   - Navigate to the repository on GitHub
   - Click the green "Code" button
   - Select "Codespaces" tab
   - Click "Create codespace on main"

2. **Automatic Setup:**
   - The `.devcontainer/devcontainer.json` file will automatically configure the environment
   - Dependencies will be installed automatically
   - VS Code extensions will be installed

3. **Manual Setup (if needed):**
   ```bash
   # Follow steps 3-9 from above
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

## Performance Optimization

### For Large Projects

1. **Use pip cache:**
   ```bash
   pip install --cache-dir ~/.cache/pip -r requirements.txt
   ```

2. **Parallel testing:**
   ```bash
   pip install pytest-xdist
   pytest -n auto
   ```

3. **Optimize MyPy:**
   ```bash
   # Create mypy cache
   mypy --install-types src/ethical_ai_validator/
   ```

## Security Considerations

1. **Never commit sensitive data:**
   - API keys
   - Database credentials
   - Personal information

2. **Use environment variables:**
   ```bash
   # In .env file (not committed)
   API_KEY=your_api_key_here
   DATABASE_URL=your_database_url_here
   ```

3. **Regular security updates:**
   ```bash
   # Update dependencies regularly
   pip list --outdated
   pip install --upgrade package_name
   ```

## Next Steps

After completing the setup:

1. **Read the documentation:**
   - [README.md](README.md)
   - [Contributing Guide](CONTRIBUTING.md)

2. **Explore the codebase:**
   - Review the project structure
   - Understand the main modules
   - Read existing tests

3. **Start contributing:**
   - Pick an issue from the GitHub Issues
   - Create a feature branch
   - Write tests for your changes
   - Submit a pull request

## Support

If you encounter issues during setup:

1. **Check the troubleshooting section above**
2. **Search existing issues on GitHub**
3. **Create a new issue with detailed information**
4. **Join the project discussions**

## Additional Resources

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linting](https://flake8.pycqa.org/)
- [MyPy Type Checking](https://mypy.readthedocs.io/)
- [Pre-commit Hooks](https://pre-commit.com/) 