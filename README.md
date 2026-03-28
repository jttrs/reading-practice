# Reading Practice

A static web app to help a child practice reading. Currently includes two modules:

- **Decoding** — Practice breaking words into spelling sounds (phoneme patterns). Words are sourced from teacher-provided reading group materials.
- **Sight Words** — Digital flashcard practice for high-frequency sight words.

Features adaptive weighting based on performance, optional text-to-speech, and configurable difficulty per element.

## Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager, only needed to regenerate word data from PDFs)

## Quick Start

```bash
# Install frontend dependencies
npm install

# Start development server
npm run dev
```

The app loads pre-extracted word data from `src/data/decoding-words.json` (git-tracked), so you don't need Python/uv for normal development.

## Regenerating Word Data

If you add new PDFs to `materials/`, regenerate the JSON:

```bash
# Extract words from PDFs into JSON
npm run extract
```

This runs `uv run python scripts/extract_decoding_data.py` which reads the PDFs in `materials/decoding/` and outputs `src/data/decoding-words.json`.

See [scripts/README.md](scripts/README.md) for details on the extraction pipeline.

## Build & Deploy

```bash
# Production build (outputs to dist/)
npm run build

# Preview production build locally
npm run preview
```

The `dist/` folder can be deployed to any static hosting (GitHub Pages, Netlify, Vercel, etc.).

## Project Structure

```
reading-practice/
├── materials/          # Source PDFs (teacher emails + books)
├── scripts/            # Python extraction pipeline
├── src/
│   ├── data/           # Generated JSON data (git-tracked)
│   ├── components/     # Shared UI components
│   ├── hooks/          # Shared React hooks (progress, TTS, sessions)
│   ├── modules/        # Practice modules (decoding, sight-words)
│   └── pages/          # Top-level pages (landing)
├── index.html          # Vite entry
├── package.json
├── pyproject.toml      # Python deps for extraction
└── vite.config.ts
```

See [materials/README.md](materials/README.md) for how to add new source materials.
See [src/modules/README.md](src/modules/README.md) for how to add new practice modules.
