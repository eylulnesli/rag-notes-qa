"""Prompt variants + the model call (Anthropic Messages API)."""
import os
import anthropic
from .config import MODEL

REFUSAL = "I could not find this in the notes."
_BASE = ("You answer questions about software project management course notes. "
         "Reply in the same language as the question.")

PROMPTS = {
    "basic": "You are a helpful assistant. Answer the question using the context below.",
    "grounded": (_BASE + " Use ONLY the numbered context passages. If they do not contain the answer, "
                 f'reply exactly: "{REFUSAL}" Never use outside knowledge.'),
    "grounded_cited": (_BASE + " Use ONLY the numbered context passages. If they do not contain the answer, "
                       f'reply exactly: "{REFUSAL}" Be concise (max 4 sentences) and cite passages like [1] after each claim.'),
}


def _client() -> anthropic.Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or key.startswith("paste-"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key.")
    return anthropic.Anthropic(api_key=key)


def build_context(passages) -> str:
    return "\n\n".join(f"[{i}] ({p['source']}, p.{p['page']})\n{p['text']}" for i, p in enumerate(passages, 1))


def answer(question: str, passages, variant: str = "grounded_cited") -> str:
    if variant not in PROMPTS:
        raise ValueError(f"Unknown variant '{variant}'. Options: {list(PROMPTS)}")
    msg = _client().messages.create(
        model=MODEL, max_tokens=500, system=PROMPTS[variant],
        messages=[{"role": "user", "content": f"Context:\n{build_context(passages)}\n\nQuestion: {question}"}],
    )
    return "".join(b.text for b in msg.content if b.type == "text")
