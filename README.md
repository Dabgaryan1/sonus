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

## Google Colab Setup

1. Open notebooks/sonus_setup/ipynb from the GitHub repository.
2. Click Open in Colab if available, or download the notebook and upload it to Google Colab.
3. Select Runtime -> Run all
4. The notebook will clone the Sonus repository, install the dependencies from requirements.txt, and verify that the environment is configured correctly.
   
- **Note:** Google Colab environments are temporary. Dependencies may need to be reinstalled when starting a new session.

  
## Project Status

Currently in early development.
