# DocTagger

DocTagger is a Python tool that analyzes documents (PDF, DOCX, PPTX, TXT) to extract system metadata and generate AI-powered abstracts and tags using local LLMs via Ollama.

## Features

- **Metadata Extraction**: Extracts file size, creation/modification dates, and file type.
- **Text Extraction**: Supports PDF, DOCX, PPTX, and TXT formats.
- **AI Analysis**: Uses local Ollama models (e.g., Llama 3.2, Mistral) to generate:
  - A concise abstract (in English).
  - Relevant tags/keywords (in English).
- **JSON Output**: Saves the analysis results in a JSON file alongside the original document.

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/) installed and running locally.
- An Ollama model pulled (e.g., `ollama pull llama3.2`).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/doctagger.git
   cd doctagger
   ```

2. Install Python dependencies:
   ```bash
   pip install ollama pypdf python-docx python-pptx
   ```

## Usage

Run the script providing the file path to analyze:

```bash
python doctagger.py path/to/document.pdf
```

### Optional Arguments

- `--model`: Specify the Ollama model to use (default: `llama3.2`).

```bash
python doctagger.py path/to/document.pdf --model mistral
```

## Output

The tool generates a `.json` file with the same name as the input file (e.g., `document.pdf.json`) containing:
- File info (size, dates).
- AI analysis (abstract, tags).
- Word count.
- Model used.

## License

MIT
