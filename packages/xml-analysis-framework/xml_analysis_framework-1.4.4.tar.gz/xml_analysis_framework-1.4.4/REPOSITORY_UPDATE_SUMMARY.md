# Repository Information Update Summary

## Changes Made for v1.2.0

### 🔗 **GitHub Repository URLs Updated**
All references changed from:
- `https://github.com/wjackson/xml-analysis-framework`

To:
- `https://github.com/redhat-ai-americas/xml-analysis-framework`

### 📧 **Contact Information Updated**
Author email changed from:
- `wjackson@example.com`

To:
- `wjackson@redhat.com`

### 📁 **Files Updated**

#### **setup.py**
- ✅ `url` field
- ✅ `author_email` field  
- ✅ `project_urls` section (Bug Reports, Source, Documentation)

#### **pyproject.toml**
- ✅ `authors` email field
- ✅ `[project.urls]` section (Homepage, Repository, Issues, Documentation)

#### **README.md**
- ✅ Installation section git clone command
- ✅ Fixed smart chunking example with analysis format conversion

#### **CONTRIBUTING.md**
- ✅ Development setup git clone command

#### **Version Files**
- ✅ setup.py version → 1.2.0
- ✅ src/__init__.py version → 1.2.0

#### **CHANGELOG.md**
- ✅ Added v1.2.0 entry documenting all changes

### 🎯 **PyPI Package Links**
When v1.2.0 is published, PyPI will show:
- **Homepage**: https://github.com/redhat-ai-americas/xml-analysis-framework
- **Repository**: https://github.com/redhat-ai-americas/xml-analysis-framework  
- **Issues**: https://github.com/redhat-ai-americas/xml-analysis-framework/issues
- **Documentation**: https://github.com/redhat-ai-americas/xml-analysis-framework/blob/main/README.md

### ✅ **Verification**
All references have been updated consistently across the project. The PKG-INFO file will be automatically regenerated during the next build process with the correct information.

### 📦 **Next Steps**
To update PyPI with these changes:
1. Commit and push changes to Git
2. Build the package: `python -m build`
3. Upload to PyPI: `twine upload dist/*`

The new v1.2.0 package will have all the correct Red Hat AI Americas repository links and contact information.