# Setup Instructions

## PyPI Token Setup

To deploy the TMT package to PyPI, you need API tokens:

### 1. Create PyPI Account
- Go to https://pypi.org/account/register/
- Create an account and verify your email

### 2. Generate API Token
- Go to https://pypi.org/manage/account/
- Scroll to "API tokens" section
- Click "Add API token"
- Name: `tmt-deployment`
- Scope: "Entire account" (or specific to this project once created)
- Copy the generated token (starts with `pypi-`)

### 3. Update .env File
Replace the example tokens in `.env`:
```bash
PYPI_USERNAME=__token__
PYPI_PASSWORD=pypi-YOUR_ACTUAL_TOKEN_HERE
PYPI_API_TOKEN=pypi-YOUR_ACTUAL_TOKEN_HERE
```

### 4. Test PyPI (Optional)
For testing deployments:
- Go to https://test.pypi.org/account/register/
- Create account and generate token
- Update TEST_PYPI_* variables in .env

## Required Tools
Install these tools before running deployment:
```bash
pip install twine build
```

## Security Notes
- Never commit the actual .env file with real tokens
- Keep .env.example for reference
- Use environment-specific tokens for production vs testing