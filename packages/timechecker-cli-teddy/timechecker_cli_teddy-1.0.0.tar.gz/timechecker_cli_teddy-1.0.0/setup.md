# Setup Guide

## Required Tokens and API Keys

### PyPI Account Setup

1. **Create PyPI Account**
   - Go to https://pypi.org/account/register/
   - Create an account with your email

2. **Create API Token**
   - Go to https://pypi.org/manage/account/#api-tokens
   - Click "Add API token"
   - Name: `timechecker-deploy`
   - Scope: `Entire account` (or specific to timechecker project after first upload)
   - Copy the generated token (starts with `pypi-`)

3. **Create TestPyPI Account (Optional)**
   - Go to https://test.pypi.org/account/register/
   - Create account for testing deployments
   - Generate API token at https://test.pypi.org/manage/account/#api-tokens

### Environment Setup

1. **Copy Environment File**
   ```bash
   cp .env.example .env
   ```

2. **Update .env File**
   - Replace `PYPI_TOKEN` with your actual PyPI token
   - Replace `TESTPYPI_TOKEN` with your TestPyPI token (if using)
   - Keep `PYPI_USERNAME=__token__` as is

### Required Tools

- Python 3.7+
- pip
- twine (installed by cook.sh)
- build (installed by cook.sh)

No additional API keys or external services required for core functionality.