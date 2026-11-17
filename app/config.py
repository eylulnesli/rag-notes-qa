import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", ROOT / "docs"))
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
BACKEND = os.getenv("EMBEDDING_BACKEND", "tfidf")  # tfidf | sbert
CHUNK_CHARS = 900
CHUNK_OVERLAP = 150
TOP_K = 4
