# Getting Started

## Installation

```powershell
git clone https://github.com/is-leeroy-jenkins/Iyrin.git
cd Iyrin
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```powershell
streamlit run app.py
```

## Build Documentation

```powershell
mkdocs build --strict
```

## Serve Documentation

```powershell
mkdocs serve
```

!!! note "Credentials"
    Provider-specific functionality requires the corresponding environment variable or session credential. Independent providers do not require credentials for unrelated services.

## First Run

1. Start Iyrin.
2. Select one of the eleven application modes.
3. Configure only the credentials required by the selected source.
4. Use processing controls when chunking, embeddings, or vector storage are required.
5. Use Interactive Map for Live World operations and spatial analysis.
