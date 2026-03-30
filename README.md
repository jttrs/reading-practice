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

If you add new PDFs to `materials/`, regenerate the data and audio:

```bash
# Extract words from PDFs into JSON (uses Datamuse API for phoneme lookup)
npm run extract

# Generate TTS audio files (requires Google Cloud credentials)
npm run generate-audio

# Run 12 validation checks on the generated data
npm run validate
```

See [scripts/README.md](scripts/README.md) for details on each script.

## Testing

```bash
# Run everything: validate data + build + Playwright e2e tests
npm test

# Run only e2e tests
npm run test:e2e
```

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
├── public/audio/       # Pre-generated TTS audio (phonemes + words)
├── scripts/            # Python extraction, audio generation, validation
├── src/
│   ├── data/           # Generated JSON data (git-tracked)
│   ├── components/     # Shared UI components
│   ├── hooks/          # Shared React hooks (progress, TTS, sessions)
│   ├── modules/        # Practice modules (decoding, sight-words)
│   └── pages/          # Top-level pages (landing)
├── tests/              # Playwright e2e tests
├── index.html          # Vite entry
├── package.json
├── pyproject.toml      # Python deps for extraction scripts
└── vite.config.ts
```

See [materials/README.md](materials/README.md) for how to add new source materials.
See [src/modules/README.md](src/modules/README.md) for how to add new practice modules.
