# Cuadre App

Cross-platform cash reconciliation application for CP Company retail stores.

## Purpose

Standardize the daily cash reconciliation process across stores, providing a consistent calculation, validation and submission workflow.

## Features

- Store identification and daily reconciliation.
- Centralized cash calculation.
- Employee confirmation of expected cash.
- Mandatory discrepancy notes when cash does not match.
- Submission records and historical traceability.
- PDF report generation and printing.
- NTFY notifications.

## Technology

- Python 3.12+
- PySide6 6.12.0 (Qt)
- SQLite
- ReportLab 5.1.0
- pytest (development and testing only)

## Supported platforms

- Debian 13 Linux
- Arch Linux (development)
- Windows

---

# Installation — Debian 13

## 1. Prerequisites

Install Git, Python, virtual environment support and system libraries:

```bash
sudo apt update
sudo apt install -y \
    git \
    python3 \
    python3-venv \
    python3-pip \
    cups \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libegl1 \
    libgl1
```

Python 3.12 or newer is required. Debian 13 includes a compatible Python version.

Check:

```bash
python3 --version
git --version
```

CUPS must be installed and the store printer must be configured in the operating system for printing to work.

## 2. Clone the repository

```bash
git clone https://github.com/cp-transfer/cuadre-app.git
cd cuadre-app
```

## 3. Create the virtual environment

```bash
python3 -m venv .venv
```

## 4. Install Cuadre and its dependencies

```bash
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install .
```

## 5. Launch

```bash
.venv/bin/python -m cuadre
```

Always launch using the virtual environment created for this repository.

---

# Installation — Windows

## 1. Download prerequisites

Install these programs before cloning the repository:

1. **Git for Windows:** https://git-scm.com/download/win
2. **Python 3.12 or newer:** https://www.python.org/downloads/windows/

   Make sure the Python Launcher (`py`) is installed.

3. **Adobe Acrobat Reader:** https://get.adobe.com/reader/

   A PDF application with a registered Windows print action is required for printing. Set the PDF application as the default for `.pdf` files.

## 2. Clone the repository

Open PowerShell:

```powershell
git clone https://github.com/cp-transfer/cuadre-app.git
cd cuadre-app
```

## 3. Install Cuadre

Run the included installer:

```powershell
.\install_windows.cmd
```

The installer automatically:

- Checks that Python 3.12 or newer is available.
- Creates the `.venv` virtual environment.
- Updates pip.
- Installs Cuadre and its required dependencies.

## 4. Launch

```powershell
.\.venv\Scripts\python.exe -m cuadre
```

Always launch using the virtual environment inside the cloned repository.

---

# Updating an existing installation

## Debian

From the repository directory:

```bash
git pull origin master
.venv/bin/python -m pip install --upgrade --force-reinstall .
```

## Windows

From the repository directory:

```powershell
git pull origin master
.\.venv\Scripts\python.exe -m pip install --upgrade --force-reinstall .
```

Always use the Python executable inside the repository's `.venv`.

---

# Printing and notifications

## Debian

Printing uses CUPS and the `lp` command. A working CUPS installation and configured printer are required.

## Windows

Printing uses the Windows PDF application's registered print action. A compatible PDF reader and a configured Windows printer are required.

## NTFY

Notifications require internet connectivity and valid NTFY configuration.

Printing and notification are separate operations within the application's workflow: a printing failure must not prevent an NTFY notification from being sent.

---

# Development and testing

Create a virtual environment and install development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest -q
```

## License

Internal CP Company project. Not for public distribution.
