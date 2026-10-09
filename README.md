# Sonus

Sonus is an educational AI tool designed to help students and aspiring music producers better understand music theory.

The goal is to analyze musical elements such as chords, keys, melodies, and chord progressions and provide educational feedback to help users improve their understanding of music.

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** TBD
- **Machine Learning:** Python

## Project Structure

```text
sonus/
├── backend/       # Backend API
├── frontend/      # User interface
├── model/         # ML models and training code
├── data/          # Datasets and preprocessing
└── README.md
```

## Development Workflow

- `main` is the stable branch.
- Create separate branches for new features and bug fixes.
- Use descriptive branch names such as `feature/chord-detection`.
- Submit pull requests before merging changes into `main`.

## Getting Started

### Prerequisites
- Python 3
- Git
- pip

### Local Setup

1. Clone the repository:

```bash
git clone https://github.com/Dabgaryan1/sonus.git
cd sonus
```

2. Create a virtual environment:

```bash
python -m venv backend/.venv
```

3. Activate the virtual environment:

**Windows (PowerShell):**
```powershell
.\backend\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source backend/.venv/bin/activate
```

4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Start the FastAPI server:

```bash
fastapi dev backend/main.py
```

6. Open `http://127.0.0.1:8000/docs` to view the API documentation.

### Google Colab Setup

1. Open [Google Colab](https://colab.research.google.com/).
2. Open `notebooks/sonus_setup.ipynb` from the Sonus GitHub repository.
3. Select **Runtime → Run all**.
4. The notebook will clone the repository, install the required Python dependencies, and verify the environment.

**Note:** Google Colab environments are temporary, so setup may need to be repeated when starting a new session.


## Project Status

Currently in early development.
