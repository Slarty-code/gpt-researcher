# Getting started with Dex-researcher

This guide gets you from zero to running your first research query. No prior setup experience required.

---

## What you need

- **Python 3.11 or later** — [Install Python](https://www.python.org/downloads/) if you don’t have it. Check with: `python --version`.
- **Two API keys** (both have free tiers):
  - **OpenAI** — used by default for the research/writing AI. Get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
  - **Tavily** — used for web search. Get one at [tavily.com](https://tavily.com) (sign up, then API key in dashboard).

---

## Step 1: Open the project

Open the `Dex-researcher` folder in your editor or terminal (e.g. the folder that contains this file).

---

## Step 2: Create your `.env` file

The app reads settings from a file named `.env` in the project root.

1. Copy the example file:
   - **Windows (PowerShell):** `Copy-Item .env.example .env`
   - **Mac/Linux:** `cp .env.example .env`

2. Open `.env` in a text editor and fill in at least these two lines (no quotes needed):

   ```env
   OPENAI_API_KEY=sk-your-openai-key-here
   TAVILY_API_KEY=tvly-your-tavily-key-here
   ```

   Save the file.

---

## Step 3: Install dependencies

In a terminal, from the **project root** (the `Dex-researcher` folder):

```bash
pip install -r requirements.txt
```

If you use a virtual environment, create and activate it first, then run the same command:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

---

## Step 4: Start the server

From the **project root**:

```bash
python main.py
```

You should see something like:

```text
Starting server...
INFO:     Uvicorn running on http://0.0.0.0:8067
```

Leave this terminal open.

---

## Step 5: Run your first research

1. Open a browser and go to: **http://localhost:8067**
2. You should see the GPT Researcher interface.
3. Type a research question (e.g. “What are the main causes of inflation in 2024?”) and start the research.
4. Wait for the report to be generated (it can take a couple of minutes).

If that works, you’re set up.

---

## Where things are saved

- **Reports** — Stored under the `outputs` folder (and available in the UI).
- **Audit log (Dex-researcher)** — Each run is logged. By default, records are appended to `data/audit.jsonl` (the `data` folder is created automatically if needed).

---

## Optional: Use OpenRouter instead of OpenAI

If you want to use [OpenRouter](https://openrouter.ai) (one key, many models) instead of OpenAI:

1. Get an API key from [openrouter.ai/keys](https://openrouter.ai/keys).
2. In `.env` add or set:

   ```env
   OPENROUTER_API_KEY=your-openrouter-key
   FAST_LLM=openrouter:openai/gpt-4o-mini
   SMART_LLM=openrouter:openai/gpt-4o-mini
   STRATEGIC_LLM=openrouter:openai/gpt-4o-mini
   ```

3. Restart the server (`python main.py`). Research will now go through OpenRouter instead of OpenAI.

---

## Optional: Add the RAG service (your own documents)

To also search over your own documents (on-prem RAG):

1. Start the RAG service in a **second** terminal:

   ```bash
   cd rag-service
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8001
   ```

2. In your **main** `.env` (in the project root), add:

   ```env
   RAG_API_URL=http://localhost:8001
   RETRIEVER=tavily,rag
   ```

3. Restart the main app (`python main.py`). Research will use both web search (Tavily) and the RAG service.  
   (Without a RAG index loaded, RAG may return no results; the app will still run.)

---

## Troubleshooting

| Problem | What to try |
|--------|-------------|
| `ModuleNotFoundError` when running `python main.py` | Run `pip install -r requirements.txt` from the project root and try again. |
| “API key not found” or 401 errors | Check that `.env` is in the project root, variable names are correct (`OPENAI_API_KEY`, `TAVILY_API_KEY`), and there are no extra spaces or quotes. |
| Port 8067 already in use | Another app is using 8067. Stop it or set `PORT` in `.env` (e.g. `PORT=8068`). |
| Blank or broken page at http://localhost:8067 | Hard refresh (Ctrl+F5 or Cmd+Shift+R) or try another browser. |
| RAG returns no results | The RAG service runs without an index by default. To get results, you’d need to add a RAG index (e.g. LightRAG with documents). See [docs/DEX-RESEARCHER-MVP.md](docs/DEX-RESEARCHER-MVP.md). |

---

## Next steps

- **Full Dex-researcher options** (private mode, audit, citations): see [docs/DEX-RESEARCHER-MVP.md](docs/DEX-RESEARCHER-MVP.md).
- **Original GPT Researcher docs**: [docs.gptr.dev](https://docs.gptr.dev).
