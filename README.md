# Azerbaijani Morphological Analyzer

This repository contains a rule-based and dictionary-backed Azerbaijani morphological analyzer, supporting data files, and two local interfaces:

- a Flask admin panel for browsing dictionaries, rules, and sentence analysis
- Gradio interfaces for token analysis and model training

The published repository is intended to contain source code and language resources only. Local virtual environments, office documents, archives, and other machine-specific artifacts are excluded.

## Repository Layout

- `admin_panel/` Flask application and templates
- `annotator_ui.py` Gradio interface for sentence-level token analysis
- `train_ui.py` Gradio interface for model training
- `morpho_engine.py` analyzer logic and UI helpers
- `ml_models.py` dictionary lookup and statistical tag prediction helpers
- `roots.json`, `affixes.json`, `rules.json` core morphological data
- `dictionaries/` JSON dictionaries for Azerbaijani, Turkish, and Russian
- `dicts/` linguistic text datasets kept with the repository

## Requirements

Two dependency entry points are documented in this repository:

- `requirements.txt` for root-level scripts and Gradio tools
- `admin_panel/requirements.txt` for the Flask admin panel

Use Python 3.11 or a compatible interpreter.

## Setup

Create and activate a virtual environment, then install one of the dependency sets.

### Root tools

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Admin panel

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r admin_panel/requirements.txt
```

If you want to use both interfaces from the same environment, install both requirement files.

## Running the App

### Flask admin panel

```powershell
Set-Location admin_panel
python app.py
```

The app starts on `http://127.0.0.1:8000`.

### Gradio analyzer

```powershell
python annotator_ui.py
```

The Gradio analyzer starts on `http://127.0.0.1:7860`.

### Training interface

```powershell
python train_ui.py
```

## Data Included In Git

The repository keeps the source datasets required by the analyzer:

- rule and affix JSON files
- language dictionaries under `dictionaries/`
- text resources under `dicts/`

## Security Note

This repository still contains development-only local secrets in the Flask app configuration. Keep the GitHub repository private until those values are moved to environment variables and rotated.

## Publishing Notes

The Git history should not include:

- local virtual environments
- cached Python bytecode
- generated model files
- office documents and archive bundles

Those items are excluded by the root `.gitignore`.