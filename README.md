# Sonus

Sonus is an AI-powered music generation application designed to create original music and generate accompaniment for existing musical compositions.

The project aims to explore generative AI in music production and human-AI musical collaboration. Its long-term goal is to enable AI-generated music to be performed alongside live musicians, responding to musical input in real time.

## Project Goals

- Generate music using pretrained machine learning models.
- Generate accompaniment for existing melodies and musical sequences.
- Develop an accessible interface for AI-assisted music generation.
- Integrate MIDI input and output for musical interaction.
- Explore real-time music generation and collaboration with live musicians.

## Tech Stack

- **Backend:** Python, FastAPI
- **Frontend:** TBD
- **Machine Learning:** PyTorch, Hugging Face Transformers
- **Music Generation:** Stanford Anticipatory Music Transformer
- **MIDI Processing:** Mido, FluidSynth
- **Development:** Git, GitHub, Google Colab

## Project Structure

```text
sonus/
├── backend/             # FastAPI backend and music generation
│   ├── main.py
│   └── music_generator.py
├── frontend/            # User interface
├── model/               # Model-related code and experiments
├── data/                # Musical datasets and preprocessing
├── notebooks/           # Jupyter notebooks and experiments
├── requirements.txt     # Python dependencies
└── README.md
```

## Development Workflow

- `main` is the stable branch.
- Create separate branches for new features and bug fixes.
- Use descriptive branch names such as `feature/music-generation`.
- Submit pull requests before merging changes into `main`.

## Getting Started

### Prerequisites

- Python 3.11
- Git
- pip
- A virtual environment
- NVIDIA GPU with CUDA support (recommended for local model inference)

### Local Setup

1. Clone the repository:

```bash
git clone https://github.com/Dabgaryan1/sonus.git
cd sonus
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
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
4. Follow the notebook instructions to configure the environment.

**Note:** Google Colab environments are temporary, so setup may need to be repeated when starting a new session.

## AI Music Generation

Sonus is being developed using Stanford University's Anticipatory Music Transformer (AMT), a pretrained generative model capable of producing symbolic music and generating accompaniment conditioned on existing musical sequences.

The model generates musical events that can be converted into MIDI files for playback and further processing.

The current development objective is to integrate these capabilities into the Sonus backend and eventually extend them to support live musical interaction.

### Research and Attribution

- **Paper:** [Anticipatory Music Transformer](https://arxiv.org/abs/2306.08620)
- **Original Implementation:** [Stanford AMT GitHub Repository](https://github.com/jthickstun/anticipation)
- **Pretrained Model:** [Stanford CRFM Music Model](https://huggingface.co/stanford-crfm/music-medium-800k)

The original implementation and pretrained model are distributed under the Apache License 2.0. Sonus builds upon this research while developing its own application architecture, user interface, and musical interaction capabilities.

Any redistributed Stanford code or model components must retain applicable license and attribution notices.

## Project Status

**In active development.**

### December 2026 Milestone

Develop a functional prototype capable of generating music and accompaniment using pretrained AI models.

### Spring 2027 Milestone

Extend Sonus to support live musical collaboration, with the goal of demonstrating AI-generated music alongside human musicians.

## Future Development

- Music generation controls and customization
- Melody-conditioned accompaniment
- MIDI file input and export
- Real-time MIDI input processing
- Tempo synchronization
- Low-latency music generation for live performance
