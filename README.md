# Course Notes RAG API

A small retrieval-augmented question-answering service built on my Software Project Management lecture notes.
It exposes a REST API (FastAPI), retrieves relevant slides with vector search, and asks an LLM (Anthropic Messages API) to answer **only** from the retrieved passages. A built-in eval set compares three prompt designs.

## Architecture

```
PDF notes -> clean + chunk (900 chars, 150 overlap, page metadata)
          -> vectorize (TF-IDF default, optional multilingual sentence-transformers)
question  -> top-k cosine search -> prompt (variant) -> LLM -> answer + sources
```

|Part|File|
|-|-|
|Ingestion / chunking|`app/ingest.py`|
|Vector search|`app/retrieval.py`|
|Prompt variants + model call|`app/llm.py`|
|REST API (`/ask`, `/health`, `/variants`)|`app/main.py`|
|Eval set + runner|`eval/`|

## Quickstart

```bash
python -m venv .venv \&\& source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env                                # then add ANTHROPIC\_API\_KEY
# put your PDFs in docs/
uvicorn app.main:app --reload                       # open http://127.0.0.1:8000/docs
```

Example request:

```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" \\
  -d '{"question": "What is the payback period in the example?", "variant": "grounded\_cited"}'
```

## Prompt variants

* `basic`: plain "answer using the context"
* `grounded`: use only the passages, refuse when the answer is missing
* `grounded\_cited`: same, plus concise answers with `\[n]` citations

## Evaluation

20 questions (18 answerable, 2 deliberately unanswerable to test hallucination). Metrics: retrieval hit@k, context recall, keyword-based answer accuracy, correct refusals, latency.

```bash
python -m eval.run\_eval --retrieval-only   # no API key needed
python -m eval.run\_eval                    # compares all prompt variants
```

Results (20 questions, claude-haiku-5-5, TF-IDF retrieval, top\_k=4):



| Prompt variant | Answer accuracy | Correct refusals | Avg latency (s) |

|---|---|---|---|

| basic | 81% | 0/2 | 2.59 |

| grounded | 81% | 2/2 | 1.98 |

| grounded\_cited | 76% | 2/2 | 2.15 |



Findings:

\- The baseline prompt answered both unanswerable questions with invented content; both grounded prompts refused correctly (small sample: 2 questions).

\- Prompt wording changed accuracy only slightly; the remaining misses are mostly data/retrieval issues.

\- NPV questions failed in all variants because those slides store their tables as images, which text extraction cannot read (OCR would be the next step).

\- The metric is keyword matching, a rough proxy; hit@k also counts the wrong lecture as correct for question 1.

## Design decisions and limitations

* TF-IDF keeps setup to zero downloads; set `EMBEDDING\_BACKEND=sbert` for neural, multilingual embeddings (useful for Turkish questions over English slides).
* Answer accuracy uses keyword matching, which is a cheap proxy; an LLM-as-judge or human review would be the next step.
* Index is rebuilt at startup (fast for a few hundred chunks); a persistent vector store would be needed at larger scale.
* Lecture PDFs are not committed (copyright); add your own to `docs/`.

