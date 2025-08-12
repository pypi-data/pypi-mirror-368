# PyPI Authentication Setup Guide

This guide explains how to connect your local development environment to your existing PyPI account for package publication.

## 🔑 How PyPI Authentication Works

PyPI uses **API tokens** for authentication instead of username/password. This is more secure and allows for fine-grained permissions.

## 📋 Step-by-Step Setup

### Step 1: Access Your PyPI Account

1. **Go to PyPI**: Visit [https://pypi.org/](https://pypi.org/)
2. **Sign In**: Use your existing PyPI account credentials
3. **Navigate to Account Settings**: Click on your username → "Account settings"

### Step 2: Generate API Token for PyPI

1. **Go to API Tokens Section**:
   - In your account settings, find "API tokens" in the left sidebar
   - Click "Add API token"

2. **Configure the Token**:
   - **Token name**: Give it a descriptive name (e.g., "odoo-lead-manager-upload")
   - **Scope**: Select "Entire account (all projects)" or "Restrict to a project" if you want to limit access
   - **Project**: If restricting to a project, select "odoo-lead-manager" (or create it first)

3. **Create the Token**:
   - Click "Add token"
   - **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

### Step 3: Generate API Token for TestPyPI (Recommended)

1. **Go to TestPyPI**: Visit [https://test.pypi.org/](https://test.pypi.org/)
2. **Sign In**: Use your existing TestPyPI account (or create one)
3. **Follow the same steps** as above to generate a TestPyPI token

### Step 4: Configure Local Authentication

Create or update the `~/.pypirc` file in your home directory:

```bash
# On macOS/Linux
nano ~/.pypirc

# On Windows (PowerShell)
notepad $env:USERPROFILE\.pypirc
```

Add the following content:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-actual-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

**Important Notes**:
- Replace `pypi-your-actual-api-token-here` with your real PyPI token
- Replace `pypi-your-test-api-token-here` with your real TestPyPI token
- The `__token__` username is literal - don't change it
- The password should start with `pypi-` followed by your actual token

### Step 5: Secure Your Configuration

```bash
# Set proper permissions (macOS/Linux)
chmod 600 ~/.pypirc

# On Windows, ensure the file is not readable by others
```

## 🔍 Verifying Your Setup

### Test PyPI Connection

```bash
# Test PyPI authentication
twine check --repository pypi dist/*

# Test TestPyPI authentication  
twine check --repository testpypi dist/*
```

### Test Upload (Dry Run)

```bash
# Test upload to TestPyPI (recommended first)
twine upload --repository testpypi --dry-run dist/*

# If successful, test actual upload
twine upload --repository testpypi dist/*
```

## 🛠️ Alternative Authentication Methods

### Method 1: Environment Variables

Instead of using `~/.pypirc`, you can use environment variables:

```bash
# Set environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-actual-api-token-here

# For TestPyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-test-api-token-here
```

### Method 2: Command Line Arguments

You can pass credentials directly (not recommended for security):

```bash
twine upload --username __token__ --password pypi-your-token dist/*
```

## 🔧 Troubleshooting Authentication Issues

### Common Problems and Solutions

1. **"Invalid credentials" error**
   - Verify your API token is correct
   - Ensure the token starts with `pypi-`
   - Check that you're using `__token__` as the username

2. **"Token not found" error**
   - Regenerate your API token
   - Ensure you copied the entire token
   - Check that the token hasn't expired

3. **"Permission denied" error**
   - Verify your token has upload permissions
   - Check if the project exists (create it if needed)
   - Ensure you're not trying to upload to a restricted project

4. **"File permissions" error**
   - Set proper permissions: `chmod 600 ~/.pypirc`
   - Ensure the file is in your home directory

### Testing Your Configuration

```bash
# Test the configuration file
python -c "
import configparser
config = configparser.ConfigParser()
config.read('~/.pypirc')
print('PyPI configured:', 'pypi' in config.sections())
print('TestPyPI configured:', 'testpypi' in config.sections())
"
```

## 🔐 Security Best Practices

1. **Never commit tokens to version control**
   - Add `~/.pypirc` to your `.gitignore`
   - Use environment variables in CI/CD

2. **Use project-scoped tokens when possible**
   - Limit token access to specific projects
   - Rotate tokens regularly

3. **Store tokens securely**
   - Use a password manager
   - Don't share tokens in logs or error messages

4. **Monitor token usage**
   - Check PyPI account for token activity
   - Revoke unused tokens

## 📱 Using with Our Publication Script

Our `publish_to_pypi.sh` script will automatically use your `~/.pypirc` configuration:

```bash
# The script will use your configured credentials
./publish_to_pypi.sh
```

## 🚀 Next Steps

Once authentication is set up:

1. **Test with TestPyPI first**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Verify the upload**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ odoo-lead-manager
   ```

3. **Publish to PyPI**:
   ```bash
   twine upload dist/*
   ```

## 📞 Getting Help

If you encounter authentication issues:

1. **Check PyPI Status**: [https://status.python.org/](https://status.python.org/)
2. **PyPI Documentation**: [https://pypi.org/help/](https://pypi.org/help/)
3. **Twine Documentation**: [https://twine.readthedocs.io/](https://twine.readthedocs.io/)

---

**Your PyPI account is now ready to receive your package! 🎉** 