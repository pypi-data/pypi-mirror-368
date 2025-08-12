# PyPI Publication Guide for Odoo Lead Manager

This guide will walk you through the process of publishing the Odoo Lead Manager package to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI
4. **Python Tools**: Ensure you have the latest versions of build tools

## Step 1: Install Required Tools

```bash
# Install/upgrade build tools
pip install --upgrade build twine setuptools wheel

# Verify installations
python -m build --version
twine --version
```

## Step 2: Prepare Your Package

### Update Package Information

Before publishing, make sure to update the following files with your actual information:

1. **setup.py**: Update author, email, and URLs
2. **pyproject.toml**: Update project metadata
3. **README.md**: Ensure it's comprehensive and well-formatted
4. **LICENSE**: Verify the license is appropriate

### Check Package Structure

Run the build script to verify everything is ready:

```bash
python build_package.py
```

This will:
- Clean build artifacts
- Check package structure
- Build the package
- Validate the built package
- Run tests

## Step 3: Test on TestPyPI First

It's recommended to test your package on TestPyPI before publishing to the main PyPI.

### Configure TestPyPI

Create a `~/.pypirc` file (or update existing):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### Upload to TestPyPI

```bash
# Build the package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ odoo-lead-manager
```

## Step 4: Publish to PyPI

Once you've tested on TestPyPI and everything works correctly:

```bash
# Upload to PyPI
twine upload dist/*

# Verify the upload
pip install odoo-lead-manager
```

## Step 5: Verify Publication

After uploading, verify your package:

1. **Check PyPI**: Visit https://pypi.org/project/odoo-lead-manager/
2. **Test Installation**: `pip install odoo-lead-manager`
3. **Test CLI**: `odlm --help`

## Step 6: Update Documentation

After successful publication:

1. Update your README.md with installation instructions
2. Add PyPI badge to your repository
3. Update any documentation that references installation

## Common Issues and Solutions

### Package Name Already Taken

If the package name `odoo-lead-manager` is already taken, you'll need to choose a different name:

1. Update `setup.py` and `pyproject.toml` with a new name
2. Consider names like:
   - `odoo-lead-distributor`
   - `odoo-crm-lead-manager`
   - `odoo-lead-automation`

### Version Conflicts

When updating the package:

1. Increment the version number in `setup.py` and `pyproject.toml`
2. Update the version in `src/odoo_lead_manager/__init__.py`
3. Use semantic versioning (e.g., 1.3.1 → 1.3.2 for bug fixes)

### Build Errors

If you encounter build errors:

1. Check that all required files exist
2. Verify the package structure is correct
3. Ensure all dependencies are properly specified
4. Run `python -m build --verbose` for detailed error messages

### Upload Errors

Common upload issues:

1. **Authentication**: Verify your API tokens are correct
2. **Package Name**: Ensure the package name is unique
3. **Version**: Don't upload the same version twice
4. **File Size**: Ensure files aren't too large

## Best Practices

### Before Publishing

1. **Test Thoroughly**: Run all tests and verify functionality
2. **Check Dependencies**: Ensure all dependencies are correctly specified
3. **Documentation**: Make sure README.md is comprehensive
4. **License**: Include a proper license file
5. **Metadata**: Verify all package metadata is correct

### After Publishing

1. **Monitor**: Check for any issues reported by users
2. **Update**: Keep the package updated with bug fixes and features
3. **Documentation**: Maintain up-to-date documentation
4. **Support**: Provide support for users

## Automation

Consider setting up automated publishing using GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and publish
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m build
        twine upload dist/*
```

## Security Considerations

1. **API Tokens**: Never commit API tokens to version control
2. **Environment Variables**: Use environment variables for sensitive data
3. **Package Verification**: Always verify packages before installation
4. **Dependencies**: Regularly update dependencies for security patches

## Support

If you encounter issues during the publication process:

1. Check the [PyPI documentation](https://packaging.python.org/tutorials/packaging-projects/)
2. Review the [Twine documentation](https://twine.readthedocs.io/)
3. Search for similar issues on Stack Overflow
4. Contact PyPI support if needed

## Next Steps

After successful publication:

1. **Promote**: Share your package on relevant forums and communities
2. **Monitor**: Track downloads and user feedback
3. **Maintain**: Keep the package updated and well-maintained
4. **Expand**: Consider adding more features and improvements 