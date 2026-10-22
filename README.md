# QueryFix AI

Natural-language-to-SQL demo using Gemini, SQLite, Streamlit, and a bounded self-correction loop.

## Run locally
1. Install Python 3.10+.
2. Open terminal in this folder.
3. Windows: `py -m venv .venv` then `.\.venv\Scripts\Activate.ps1`
   macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
4. Install: `python -m pip install -r requirements.txt`
5. Create `.streamlit/secrets.toml` using `.streamlit/secrets.toml.example` as a template; add your Gemini API key.
6. Start: `streamlit run app.py`

## Deploy
Push the project to GitHub without secrets. On https://share.streamlit.io/ choose the repository and `app.py`. Add `GEMINI_API_KEY` and optional `GEMINI_MODEL` in App settings → Secrets, then reboot.

## Limitations
Synthetic demo data only. The query runner allows read-only SELECT/WITH queries and caps results at 500 rows. There are at most 3 execution attempts total. SQL execution success does not prove logical correctness. Gemini model names and free quotas may change.
