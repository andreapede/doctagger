import os
import argparse
import json
import datetime
import platform
import ollama

from pypdf import PdfReader
from docx import Document
from pptx import Presentation

class DocumentAnalyzer:
    def __init__(self, filepath, model="gemma3"):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.extension = os.path.splitext(filepath)[1].lower()
        self.model = model
        self.content = ""
        self.metadata = {}

    def process(self):
        print(f"[*] Processing file: {self.filename}...")
        self._extract_system_metadata()
        
        try:
            self._extract_text()
        except Exception as e:
            print(f"[!] Text extraction error: {e}")
            return

        if not self.content:
            print("[!] The file appears empty or unreadable.")
            return

        print(f"[*] AI analysis in progress with local model '{self.model}'... (this may take time)")
        self._analyze_content_ai() # Real AI method
        
        self._save_json()
        print(f"[V] Done. Metadata saved in {self.filename}.json")

    def _extract_system_metadata(self):
        stats = os.stat(self.filepath)
        if platform.system() == 'Windows':
            creation_time = stats.st_ctime
        else:
            try:
                creation_time = stats.st_birthtime
            except AttributeError:
                creation_time = stats.st_ctime

        self.metadata['file_info'] = {
            'filename': self.filename,
            'extension': self.extension,
            'size_bytes': stats.st_size,
            'created_at': datetime.datetime.fromtimestamp(creation_time).isoformat(),
            'modified_at': datetime.datetime.fromtimestamp(stats.st_mtime).isoformat()
        }

    def _extract_text(self):
        # ... (Same extraction code as before) ...
        if self.extension == '.txt':
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.content = f.read()
        elif self.extension == '.pdf':
            reader = PdfReader(self.filepath)
            text_parts = [page.extract_text() or "" for page in reader.pages]
            self.content = "\n".join(text_parts)
        elif self.extension == '.docx':
            doc = Document(self.filepath)
            self.content = "\n".join([para.text for para in doc.paragraphs])
        elif self.extension == '.pptx':
            prs = Presentation(self.filepath)
            text_parts = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text_parts.append(shape.text)
            self.content = "\n".join(text_parts)
        
        self.content = self.content.strip()

    def _analyze_content_ai(self):
        """
        Uses local Ollama to generate abstract and tags.
        """
        # 1. Text truncation
        # Local models have a context limit. We take the first 6000 characters
        # (about 1000-1500 words) which usually contain the introduction and summary.
        input_text = self.content[:6000]
        if len(self.content) > 6000:
            input_text += "... [Text truncated for analysis]"

        # 2. Prompt Construction (System + User)
        # We explicitly ask for pure JSON.
        prompt = f"""
        You are a document analysis assistant. Your task is to analyze the provided text and return output STRICTLY in JSON format.
        
        RULES:
        1. 'abstract': Write a clear summary in ENGLISH (max 100 words).
        2. 'tags': A list of 5-8 relevant tags/keywords in ENGLISH.
        3. Do not add comments, markdown, or other text outside the JSON.

        TEXT TO ANALYZE:
        {input_text}
        """

        try:
            # Call to Ollama
            response = ollama.chat(model=self.model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ], format='json') # format='json' forces the model to structure data (Ollama Feature)

            # Response parsing
            ai_content = response['message']['content']
            data = json.loads(ai_content)

            # Metadata integration
            self.metadata['analysis'] = {
                'abstract': data.get('abstract', 'N/A'),
                'tags': data.get('tags', []),
                'word_count': len(self.content.split()),
                'model_used': self.model,
                'processed_date': datetime.datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[!] Error during AI analysis: {e}")
            # Fallback in case of error
            self.metadata['analysis'] = {
                'error': str(e),
                'raw_content_preview': self.content[:200]
            }

    def _save_json(self):
        output_filename = f"{self.filename}.json"
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File to analyze")
    parser.add_argument("--model", default="gemma3", help="Ollama model to use (e.g., gemma3, mistral)")
    args = parser.parse_args()

    if os.path.exists(args.file):
        analyzer = DocumentAnalyzer(args.file, model=args.model)
        analyzer.process()
    else:
        print("File not found.")