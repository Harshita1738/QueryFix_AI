import json, re
import streamlit as st
from google import genai
from google.genai import types

def _client():
    key=st.secrets.get("GEMINI_API_KEY","")
    if not key: raise RuntimeError("GEMINI_API_KEY is missing in Streamlit secrets.")
    return genai.Client(api_key=key)

def _text(prompt):
    model = st.secrets.get("GEMINI_MODEL", "gemini-2.5-flash") # or keep your default
    client = _client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=1800)
    )
    return (response.text or "").strip()

def _extract_sql(text):
    match=re.search(r"```(?:sql)?\s*(.*?)```",text,flags=re.I|re.S)
    sql=match.group(1).strip() if match else text.strip()
    sql=re.sub(r"^\s*SQL\s*:\s*","",sql,flags=re.I)
    return sql.strip().rstrip(";")+";"

def generate_sql(question,schema):
    prompt=f"""You are QueryFix AI, a careful natural-language-to-SQL assistant. Convert the user's question into ONE SQLite query.
Return only SQL, preferably in a sql code fence. Read-only SELECT/WITH only; never write or DDL statements, PRAGMA, ATTACH, or multiple statements. Use only supplied schema. For revenue, use order_items.quantity * order_items.unit_price. Use SQLite-compatible syntax and LIMIT 100 unless aggregation makes it unnecessary.
SCHEMA: {json.dumps(schema)}
QUESTION: {question}"""
    return _extract_sql(_text(prompt))

def repair_sql(question,schema,failed_sql,error):
    prompt=f"""Repair this SQLite query after a real execution error. Return ONLY one corrected read-only SELECT/WITH query. Use only schema below, preserve user intent, no writes/DDL/PRAGMA/ATTACH/multiple statements, and use LIMIT 100 where sensible.
QUESTION: {question}
SCHEMA: {json.dumps(schema)}
FAILED SQL: {failed_sql}
ACTUAL DATABASE ERROR: {error}
Fix the specific error and return corrected SQL only."""
    return _extract_sql(_text(prompt))

def validate_result(question,sql,columns,rows):
    try:
        prompt=f"""Review whether this SQL result appears plausibly responsive to the question. This is a lightweight sanity check, NOT proof of correctness. Return strict JSON only: {{ "supported": boolean, "message": "short string" }}.
Question: {question}
SQL: {sql}
Columns: {json.dumps(columns)}
Sample rows: {json.dumps([list(r) for r in rows[:8]],default=str)}"""
        raw=_text(prompt); match=re.search(r"\{.*\}",raw,re.S); data=json.loads(match.group(0)) if match else {}
        return {"supported":bool(data.get("supported",False)),"message":str(data.get("message","Sanity check inconclusive."))}
    except Exception as e:
        return {"supported":False,"message":f"Sanity check unavailable ({type(e).__name__}); SQL ran, but logical correctness is unverified."}
