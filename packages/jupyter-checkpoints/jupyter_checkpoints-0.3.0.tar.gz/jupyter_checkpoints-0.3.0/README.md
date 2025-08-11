# JupyterCheckpoints

A JupyterLab extension for managing multiple checkpoints, allowing users to save and restore multiple historical versions of files.

## Features

- Maintains up to 5 checkpoints for each file (configurable)
- Restore to any checkpoint directly from the JupyterLab interface
- Supports notebooks (.ipynb) and regular text files
- Provides a user-friendly interface showing checkpoint creation time and relative time (e.g., "5 minutes ago")
- Automatically manages checkpoints, removing older versions

## Installation

### Using pip

```bash
pip install jupyter-checkpoints
```

### From Source

1. Clone the repository

```bash
git clone https://github.com/yourusername/jupyter-checkpoints.git
cd jupyter-checkpoints
```

2. Install the Python package

```bash
pip install -e .
```

3. Install the frontend extension

```bash
jupyter labextension develop --overwrite .
```

## Usage

After installation, JupyterCheckpoints will be automatically activated. A "Restore Checkpoint" button will be added to the toolbar of each open notebook and file editor.

### Restoring to a Checkpoint

1. Open any file or notebook
2. Click the "Restore Checkpoint" button (undo icon) in the toolbar
3. Select the checkpoint to restore from the dropdown menu
4. Confirm the restore operation

### Configuration

You can set the maximum number of checkpoints to keep for each file in your Jupyter configuration file:

```python
c.AsyncMultiCheckpoints.max_checkpoints = 10  # Default is 5
```

## Development

### Prerequisites

- JupyterLab >= 4.0.0
- Python >= 3.12
- Node.js

### Setting Up Development Environment

1. Clone the repository

```bash
git clone https://github.com/yourusername/jupyter-checkpoints.git
cd jupyter-checkpoints
```

2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install development dependencies

```bash
pip install -e .
```

4. Install JavaScript dependencies and build

```bash
cd js
npm install
npm run build
```

5. Install the extension in development mode

```bash
jupyter labextension develop --overwrite .
```

### Development Workflow

- After modifying Python code, restart the Jupyter server
- After modifying JavaScript code:
  ```bash
  cd js
  npm run build
  ```
  Then refresh the JupyterLab page

## License

MIT
