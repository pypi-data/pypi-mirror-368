# Docuver - Document Version Control Tool

A meta tool for version control of Office documents (docx, xlsx, odt, ods, odp, pptx). Since these files are essentially ZIP archives, Docuver extracts their contents into folders for proper version control with Git.

## Supported Formats

- Microsoft Office: `.docx`, `.xlsx`, `.pptx`
- LibreOffice/OpenOffice: `.odt`, `.ods`, `.odp`

## Installation

### Prerequisites
- Python 3.6 or higher
- No external dependencies (uses Python standard library only)

### Option 1: Install from PyPI (Recommended)
```bash
pip install docuver
```

### Verify Installation
```bash
docuver --help
```

## Quick Start

### 1. Initialize Your Project
```bash
# Navigate to your project directory
cd /path/to/your/project

# Initialize docuver (creates .docuver/ config and updates .gitignore)
docuver init
```

### 2. Add Office Documents
```bash
# Copy your Office documents to the project directory
cp ~/Documents/Report.docx .
```

### 3. Extract Documents for Version Control
```bash
# Initialize project and track documents
docuver init
docuver track Report.docx
docuver track Budget.xlsx

# OR use sync for individual documents
docuver sync Report.docx
```

### 4. Check Status
```bash
docuver status
```

### 5. Clean Up and Commit
```bash
# Remove binary files (keep extracted folders)
docuver cleanup

# Commit to version control
git add .
git commit -m "Add Office documents for version control"
```

## Commands

### `init`
Initialize docuver in the current directory.

```bash
docuver init
```

This creates:
- `.docuver/` directory for project metadata
- Updates `.gitignore` to exclude Office binary files
- **Initializes Git repository** if one doesn't exist
- Migrates any existing metadata files to centralized storage

### `sync <file|folder>`
Synchronize an Office document or folder.

```bash
# Extract a document (creates Report.docxf/ folder)
docuver sync Report.docx

# Pack a folder (creates Report.docx file)
docuver sync Report.docxf

# Force operation (skip safety checks)
docuver sync Report.docx --force
```

### `track <filename>`
Track Office document(s) for version control with wildcard support and comprehensive safety checks.

```bash
# Track a specific document
docuver track Report.docx

# Track multiple documents with wildcards
docuver track *.docx
docuver track Report*.xlsx
docuver track "Documents/*.pptx"

# Force tracking (skip safety checks)
docuver track *.docx --force

# Track without XML formatting
docuver track *.docx --no-format
```

### `cleanup`
Remove binary Office files that have corresponding extracted folders with comprehensive safety checks.

```bash
# Safe cleanup with safety checks
docuver cleanup

# Force cleanup (skip safety checks)
docuver cleanup --force
```

### `status`
Show the status of Office files and extracted folders.

```bash
docuver status
```

### `completions`
Install shell completions for docuver commands.

```bash
docuver completions
```

## Workflow

### Initial Setup
```bash
# Initialize docuver in your project
docuver init

# Extract existing Office documents
docuver prepare

# Clean up binary files (optional)
docuver cleanup

# Commit the extracted folders
git add .
git commit -m "Initial docuver setup with extracted Office documents"
```

### Working with Documents

#### To edit a document:
```bash
# Pack folder to document
docuver sync Document.docxf

# Edit Document.docx in your Office application
# ... make changes ...

# Extract updated document
docuver sync Document.docx

# Clean up binary file
rm Document.docx

# Commit changes
git add Document.docxf/
git commit -m "Updated document content"
```

### Install Completions
```bash
# Install completion scripts and configure shells automatically
docuver completions

# Completions will be available in new shell sessions
# To use in current session, restart shell or run:
exec $SHELL
```

### Enhanced Completion with argcomplete
For even better completion support, install argcomplete:
```bash
pip install docuver[completions]
```

## Troubleshooting

### "Invalid or corrupted Office document"
- Ensure the file is a valid Office document
- Try opening the file in an Office application first
- Some password-protected files may not be supported

### Git shows binary changes
- Ensure `.gitignore` includes Office extensions
- Run `docuver cleanup` to remove binary files
- Check that you're committing folders, not binary files

## ⚠️ Disclaimer 
Tool is still in development. Use at your own risk. Most of code was written by Windsurf IDE with Claude Sonnet 4.
