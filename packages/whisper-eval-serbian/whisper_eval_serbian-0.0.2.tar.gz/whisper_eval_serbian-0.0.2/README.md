# AiDA Whisper Evaluation Framework (Serbian)


[An evaluation framework for Serbian Whisper models.](https://aida.guru)

# Project Setup

Follow these steps to set up the **AiDA-Whisper-Eval** project.

---

### Using Conda

### 1. Create a new Conda environment

```bash
conda create --name aida python=3.12 -y
conda activate aida
```

#### 2. Install Poetry

```bash
pip install poetry
```

#### 3. Install project dependencies

Navigate to the project's root directory and run:

```bash
poetry install
```

---

### Using Plain Python

#### 1. Create and activate a virtual environment

```bash
python -m venv venv

# On Linux/macOS
source venv/bin/activate

# On Windows
.\venv\Scripts\activate
```

#### 2. Upgrade pip and install Poetry

```bash
pip install --upgrade pip
pip install poetry
```

#### 3. Install project dependencies

From the project's root directory, run:

```bash
poetry install
```

```bash
pip install pre-commit
```

### 4. Set up pre-commit hooks

```bash
poetry run pre-commit install
```

---

### Verifying Installation

Check installation by running tests:

```bash
# On Linux/macOS
make test

# On Windows
poetry run pytest
```

Your setup is complete!
