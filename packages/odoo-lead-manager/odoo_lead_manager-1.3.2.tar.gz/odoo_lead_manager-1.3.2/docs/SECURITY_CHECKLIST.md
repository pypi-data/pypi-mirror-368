# Security Checklist for PyPI Package

## 🚨 CRITICAL: Sensitive Files Exclusion

This document ensures that sensitive files and credentials are never accidentally included in the PyPI package.

## ✅ Files Successfully Excluded

The following sensitive files are now properly excluded from the package:

### Environment and Credential Files
- `.env` - Contains sensitive environment variables
- `.orienv` - Contains Odoo server credentials and passwords
- `*claude_desktop*` - Claude desktop configuration files
- `*config.json` - Configuration files that may contain sensitive data

### Temporary and Development Files
- `id.txt`, `ids` - Temporary ID files
- `e`, `s.txt`, `res`, `smen` - Temporary files
- `tags`, `tmp.txt` - Temporary files
- `todo*` - Todo files
- `oldfiles.txt`, `people.list` - Development files

## 🔧 Configuration Files Updated

### MANIFEST.in
Updated to exclude sensitive files:
```ini
# Exclude sensitive files and credentials
global-exclude .env
global-exclude .orienv
global-exclude *claude_desktop*
global-exclude *config.json
global-exclude id.txt
global-exclude ids
global-exclude e
global-exclude s.txt
global-exclude res
global-exclude smen
global-exclude tags
global-exclude tmp.txt
global-exclude todo*
global-exclude oldfiles.txt
global-exclude people.list
```

### .gitignore
Updated to prevent sensitive files from being committed to version control.

## 🛡️ Security Best Practices

### Before Every Build
1. **Check for sensitive files**: `find . -name "*.env*" -o -name "*config.json" -o -name ".orienv"`
2. **Verify exclusions**: `tar -tzf dist/*.tar.gz | grep -E "(\.env|\.orienv|claude_desktop|config\.json)"`
3. **Review package contents**: `tar -tzf dist/*.tar.gz | head -20`

### Before Every Commit
1. **Check git status**: `git status`
2. **Verify .gitignore**: Ensure sensitive files are not tracked
3. **Review staged files**: `git diff --cached`

### Before Every PyPI Upload
1. **Rebuild package**: `python -m build`
2. **Verify exclusions**: Check that sensitive files are not included
3. **Test installation**: `pip install dist/*.whl --force-reinstall`

## 🚨 Security Issues Found and Fixed

### Previously Included Sensitive Files
- `.orienv` - **CRITICAL**: Contained Odoo server credentials and passwords
- `claude_desktop_config.json` - Configuration files
- `claude_desktop_http_config.json` - Configuration files

### Action Taken
1. ✅ Updated MANIFEST.in to exclude all sensitive files
2. ✅ Updated .gitignore to prevent version control commits
3. ✅ Rebuilt package to verify exclusions
4. ✅ Verified sensitive files are no longer included

## 📋 Pre-Publication Checklist

Before publishing any new version to PyPI:

- [ ] Check for new sensitive files: `find . -name "*.env*" -o -name "*config.json" -o -name ".orienv"`
- [ ] Verify MANIFEST.in exclusions are up to date
- [ ] Rebuild package: `python -m build`
- [ ] Check package contents: `tar -tzf dist/*.tar.gz | grep -E "(\.env|\.orienv|claude_desktop|config\.json)"`
- [ ] Test installation: `pip install dist/*.whl --force-reinstall`
- [ ] Verify CLI works: `odlm --help`

## 🔍 Monitoring Commands

### Check for Sensitive Files
```bash
# Find all potential sensitive files
find . -name "*.env*" -o -name "*config.json" -o -name ".orienv" -o -name "*credential*" -o -name "*password*"

# Check what's in the built package
tar -tzf dist/*.tar.gz | grep -E "(\.env|\.orienv|claude_desktop|config\.json|credential|password)"
```

### Verify Git Status
```bash
# Check if sensitive files are tracked
git status --ignored

# Check what would be committed
git diff --cached
```

## ⚠️ Important Notes

1. **Never commit sensitive files** to version control
2. **Always verify exclusions** before building
3. **Test the package** before publishing
4. **Keep this checklist updated** when adding new files
5. **Rotate credentials** if they were ever exposed

## 🆘 Emergency Response

If sensitive files are accidentally published:

1. **Immediately revoke exposed credentials**
2. **Contact PyPI support** to request package removal
3. **Update all passwords and API keys**
4. **Review access logs** for unauthorized access
5. **Document the incident** and update security procedures

---

**Remember: Security is everyone's responsibility. Always verify before publishing!** 