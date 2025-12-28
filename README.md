# DocTagger

DocTagger is a Python tool that analyzes documents (PDF, DOCX, PPTX, TXT) to extract system metadata and generate AI-powered abstracts and tags using local LLMs via Ollama. It uses a hierarchical Map-Reduce approach with automatic fallbacks to ensure robust analysis even for very large documents.

## Features

- **Metadata Extraction**: Extracts file size, creation/modification dates, and file type.
- **Text Extraction**: Supports PDF, DOCX, PPTX, and TXT formats.
- **Hierarchical Map-Reduce Analysis**:
  - Chunks documents into manageable pieces (default 6000 chars with 500 char overlap).
  - Performs per-chunk analysis (MAP phase).
  - Hierarchically reduces summaries with group-level condensing.
  - Falls back to field-by-field prompts if JSON parsing fails.
- **AI Analysis**: Uses local Ollama models (e.g., Gemma3, Mistral, Llama) to generate:
  - Abstract in English (~300-400 words) with scope, methodology, results, conclusions.
  - 10 technical tags in Italian (`tags_it`).
  - 10 technical tags in English (`tags_en`).
  - List of tools, software, and algorithms mentioned (`technical_specs`).
- **Per-Chunk Debugging**: Optionally save individual chunk summaries with errors.
- **Reduce Pipeline Debugging**: Optionally dump raw reduce outputs and JSON extraction attempts.
- **JSON Output**: Saves complete analysis results including partial chunks and metadata.

## Prerequisites

- Python 3.11+ (tested with 3.11.14)
- [Ollama](https://ollama.com/) installed and running locally.
- An Ollama model pulled (e.g., `ollama pull gemma3`, `ollama pull llama2`, etc.).

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/andreapede/doctagger.git
cd doctagger
```

### 2. Set Up Conda Environment (Recommended)

If you have Miniconda or Anaconda installed:

```bash
# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate doctagger
```

Alternatively, initialize conda for your shell (one-time):
```powershell
# PowerShell on Windows
C:/ProgramData/miniconda3/Scripts/conda.exe init powershell
# Then restart your terminal
conda activate doctagger
```

### 3. Install Model

Pull your preferred Ollama model:

```bash
ollama pull gemma3
# or
ollama pull mistral
# or
ollama pull llama2
```

**Note**: `gemma3` is the default model (lighter and faster). `llama2`, `mistral`, and others are also supported.

## Usage

### Basic Usage

Analyze a document with the default model (`gemma3`):

```bash
# Using conda environment (Windows)
C:/ProgramData/miniconda3/Scripts/conda.exe run -p C:\Users\<your-user>\.conda\envs\doctagger python doctagger2.py path/to/document.pdf

# Or if conda is initialized:
conda activate doctagger
python doctagger2.py path/to/document.pdf
```

### Advanced Usage

#### Specify a Different Model

```bash
python doctagger2.py path/to/document.pdf --model mistral
```

#### Dump Per-Chunk Summaries

Save individual chunk analyses to `<filename>.chunks.json`:

```bash
python doctagger2.py path/to/document.pdf --dump-chunks
```

Output file includes:
- Chunk index, character count, summary, any error, model, and timestamp for each chunk.

#### Enable Reduce Pipeline Debugging

Save raw reduce outputs for troubleshooting JSON parsing:

```bash
python doctagger2.py path/to/document.pdf --debug-reduce
```

Output files:
- `<filename>.reduce_raw.txt` – final reduce raw text (if JSON formatting failed).
- `<filename>.reduce_group_<N>.raw.txt` – intermediate group raw text (optional).

Useful if the final abstract/tags appear empty; inspect raw output to understand the model's actual response.

#### Combine Flags

```bash
python doctagger2.py path/to/document.pdf --model gemma3 --dump-chunks --debug-reduce
```

### Script Variants

- **`doctagger2.py`** (recommended): Includes hierarchical map-reduce with fallbacks, per-chunk tracking, and debugging.
- **`doctagger.py`**: Simpler version with basic map-reduce (older, fewer options).

## Output

The tool generates a `.json` file with the same name as the input file (e.g., `document.pdf.json`) containing:

### JSON Structure

```json
{
  "file_info": {
    "filename": "document.pdf",
    "extension": ".pdf",
    "size_bytes": 1024000,
    "created_at": "2025-12-28T10:00:00.000000",
    "modified_at": "2025-12-28T12:00:00.000000"
  },
  "analysis": {
    "abstract": "A comprehensive summary in English describing scope, methodology, results, and conclusions...",
    "tags": {
      "it": ["Tag Italiano 1", "Tag Italiano 2", ...],
      "en": ["English Tag 1", "English Tag 2", ...]
    },
    "technical_specs": ["Tool 1", "Software 2", "Algorithm 3", ...],
    "method": "map_reduce",
    "chunks_processed": 27,
    "word_count": 23264,
    "model_used": "gemma3",
    "processed_date": "2025-12-28T13:00:00.000000",
    "partials_dump": false,
    "reduce_debug": false,
    "partial_chunks": [
      {
        "index": 0,
        "chunk_chars": 5984,
        "summary": "Summary of chunk 0...",
        "error": null,
        "model": "gemma3",
        "timestamp": "2025-12-28T13:00:00.000000"
      },
      ...
    ]
  }
}
```

### Output Files

- **`<filename>.json`** – Main analysis output (always created).
- **`<filename>.chunks.json`** – Per-chunk summaries (created with `--dump-chunks`).
- **`<filename>.reduce_raw.txt`** – Raw reduce output (created with `--debug-reduce` if reduce fails JSON parsing).
- **`<filename>.reduce_group_<N>.raw.txt`** – Intermediate group reduce outputs (created with `--debug-reduce` if hierarchical reduce encounters issues).

## Pipeline Details

### Document Processing Flow

1. **Extraction**: Text is extracted from the document based on its file type.
2. **Chunking**: Text is divided into overlapping chunks (default: 6000 chars with 500 char overlap) to avoid exceeding LLM context limits.
3. **MAP Phase**: Each chunk is independently analyzed to extract key technical points, methodologies, and results.
4. **Hierarchical REDUCE**: 
   - Chunks are grouped (size 6) and intermediate summaries are condensed.
   - All condensed summaries are merged into a single final prompt.
   - The model generates structured JSON with abstract, tags (IT/EN), and technical specs.
5. **Fallback Strategy**:
   - If the final reduce doesn't return valid JSON, the pipeline:
     - Attempts to extract JSON from free-form text.
     - Falls back to asking for each field (`abstract`, `tags_it`, `tags_en`, `technical_specs`) separately.
   - This ensures the final JSON is never empty, even if the model struggles with strict JSON formatting.

### Temperature & Retries

- **Temperature**: Set to 0 for deterministic, focused output.
- **Retries**: Each JSON call retries up to 2 times with fallback on failure.

## Model Recommendations

- **Gemma3** (default): Lightweight, fast, good for technical documents.
- **Mistral**: Balanced performance and quality.
- **Llama2**: More capable but slower.
- **Llama3.2**: Higher quality (slower, may exceed context on very large chunks).

## Troubleshooting

### Empty Abstract or Tags

1. Check that Ollama is running: `ollama serve` or ensure the Ollama daemon is active.
2. Verify the model is installed: `ollama list`.
3. Enable debug mode to inspect raw outputs:
   ```bash
   python doctagger2.py path/to/document.pdf --debug-reduce
   ```
4. Check `<filename>.reduce_raw.txt` to see what the model actually returned.

### Model Not Found Error

```
[!] Errore chunk 0: model 'gemma3' not found (status code: 404)
```

**Solution**: Pull the model first:
```bash
ollama pull gemma3
```

### Context Overflow (for very large documents)

If chunks are still too large and cause issues:
1. The hierarchical reduce will condense them in groups of 6.
2. If still problematic, reduce `chunk_size` manually in the code (default: 6000):
   ```python
   chunks = self._smart_chunking(self.content, chunk_size=4000, overlap=300)
   ```

### Conda Not Found

Ensure Miniconda/Anaconda is installed and in your PATH:
```powershell
# Windows: try explicit path
C:/ProgramData/miniconda3/Scripts/conda.exe --version

# Or initialize conda:
C:/ProgramData/miniconda3/Scripts/conda.exe init powershell
# Restart terminal and retry
```

## License

MIT
