# Materials

Source materials used to generate practice word data. Organized by module.

## Structure

```
materials/
└── decoding/
    ├── sophie-emails/         # Teacher email PDFs with spelling sounds & sight words
    └── reading-group-books/   # Book PDFs containing practice words
```

## Adding New Materials

### Adding a new teacher email

1. Save the email as a PDF in `materials/decoding/sophie-emails/`
2. Name it following the pattern: `Gmail - Reading group 3 update - YYYY-MM-DD.pdf`
3. Run `npm run extract` to regenerate the word data

### Adding a new reading group book

1. Save the book PDF in `materials/decoding/reading-group-books/`
2. The book name should match what the teacher references in their email
3. Run `npm run extract` to regenerate the word data

### Adding a new material source type

The extraction pipeline in `scripts/extract_decoding_data.py` uses a registry pattern. To add a new source type (e.g., worksheets, flashcards):

1. Create a new parser function in the script
2. Register it in the source registry
3. See [scripts/README.md](../scripts/README.md) for details
