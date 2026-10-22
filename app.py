import streamlit as st
import pandas as pd
import plotly.express as px
from database import build_database, get_schema, run_read_only_query
from agent import generate_sql, repair_sql, validate_result

st.set_page_config(page_title="QueryFix AI", page_icon="🩺", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #05070b; color: #f8fafc; }
.block-container { width: 100%; max-width: 1450px; padding: 2.7rem clamp(1rem, 2.5vw, 2rem) 2.5rem !important; overflow: visible; }
[data-testid="stHeader"] { height: 3.5rem; background: rgba(5, 7, 11, .96); z-index: 999; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1.2rem !important; }
h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: #f8fafc; line-height: 1.25 !important; overflow: visible; }

.brand { display: flex; align-items: center; gap: 14px; margin: 0 0 24px; padding-top: 4px; }
.brand-icon { width: 48px; height: 48px; flex: 0 0 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0ea5e9, #6366f1); color: #fff; font-size: 24px; box-shadow: 0 0 20px rgba(14, 165, 233, 0.4); }
.brand-title { font-family: 'Manrope', sans-serif; font-weight: 800; font-size: 1.6rem; line-height: 1.3; letter-spacing: -.04em; background: linear-gradient(135deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.brand-sub { color: #94a3b8; font-size: .88rem; line-height: 1.5; }

.panel { background: #0b101d; border: 1px solid #1e293b; border-radius: 18px; padding: 22px; margin-bottom: 16px; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6); }
[data-testid="stVerticalBlockBorderWrapper"] { box-sizing: border-box; background-color: #0b101d !important; border: 1px solid #1e293b !important; border-radius: 18px !important; box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.6); }
[data-testid="stVerticalBlockBorderWrapper"] > div { box-sizing: border-box; }

.kicker { color: #38bdf8; font-size: .76rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; margin-bottom: 8px; line-height: 1.4; }
.panel-title { font-family: 'Manrope', sans-serif; font-size: 1.15rem; font-weight: 750; color: #f8fafc; margin-bottom: 6px; line-height: 1.4; }
.muted { color: #94a3b8; font-size: .92rem; line-height: 1.5; }
.step-note { color: #e2e8f0; font-size: .88rem; margin-top: 12px; line-height: 1.5; padding: 12px 16px; background: #05070b; border-radius: 12px; border: 1px solid #1e293b; }

div[data-testid="stButton"] { width: 100%; }
div[data-testid="stButton"] > button { border-radius: 12px; border: 1px solid #334155; background: #111827; color: #f8fafc !important; font-weight: 700; font-size: .9rem; line-height: 1.35; min-height: 2.8rem; height: auto; padding: .5rem .4rem; white-space: normal; overflow: visible; box-shadow: none; transition: all 0.2s ease; }
div[data-testid="stButton"] > button p { color: inherit !important; font-size: inherit !important; line-height: 1.35 !important; white-space: normal !important; overflow: visible !important; }
div[data-testid="stButton"] > button[kind="primary"] { background: linear-gradient(135deg, #0ea5e9, #6366f1); border-color: transparent; color: #fff !important; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4); }
div[data-testid="stButton"] > button[kind="primary"] p { color: #fff !important; }
div[data-testid="stButton"] > button:hover { border-color: #38bdf8; color: #38bdf8 !important; background: #1f2937; }
div[data-testid="stButton"] > button[kind="primary"]:hover { background: linear-gradient(135deg, #0284c7, #4f46e5); color: #fff !important; box-shadow: 0 6px 20px rgba(14, 165, 233, 0.6); }

div[data-testid="stTextArea"] textarea { border-radius: 12px; border-color: #334155; background: #05070b; color: #f8fafc; font-size: 1rem; line-height: 1.5; }
div[data-testid="stTextArea"] textarea:focus { border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25); }
div[data-testid="stTextArea"] label { color: #cbd5e1; }

/* EXPANDER DARK OVERRIDES */
[data-testid="stExpander"] { background-color: #0b101d !important; border: 1px solid #334155 !important; border-radius: 14px !important; }
[data-testid="stExpander"] details { background-color: #0b101d !important; border-radius: 14px !important; }
[data-testid="stExpander"] summary { background-color: #111827 !important; color: #ffffff !important; font-weight: 700 !important; border-radius: 10px !important; padding: 10px 14px !important; border: 1px solid #334155; }
[data-testid="stExpander"] summary:hover { border-color: #38bdf8; color: #38bdf8 !important; }
[data-testid="stExpander"] div[role="group"] { background-color: #0b101d !important; }
div[data-testid="stExpanderDetails"] { background-color: #0b101d !important; border-top: 1px solid #1e293b; padding: 16px !important; }

/* CUSTOM PURE BLACK HTML TABLES WITH NEON BORDER */
.custom-table-container {
    width: 100%;
    background-color: #000000;
    border: 1px solid #38bdf8;
    border-radius: 12px;
    overflow-x: auto;
    margin-bottom: 12px;
    box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);
}
.custom-table {
    width: 100%;
    border-collapse: collapse;
    background-color: #000000;
    color: #ffffff;
    font-size: 0.92rem;
}
.custom-table th {
    background-color: #111827;
    color: #ffffff;
    font-weight: 800;
    text-align: left;
    padding: 12px 16px;
    border-bottom: 2px solid #38bdf8;
    letter-spacing: 0.03em;
}
.custom-table td {
    background-color: #000000;
    color: #ffffff;
    padding: 11px 16px;
    border-bottom: 1px solid #1e293b;
}
.custom-table tr:last-child td {
    border-bottom: none;
}

footer { visibility: hidden; }

@media (max-width: 900px) {
  .block-container { padding: 1.5rem 1rem 2rem !important; }
  .panel { padding: 16px; }
  .brand { margin-bottom: 16px; }
}
</style>
""", unsafe_allow_html=True)

db_path = build_database()
for key, default in [("attempts", []), ("active_panel", "Schema"), ("question", "Show monthly revenue by product category for 2025")]:
    if key not in st.session_state: 
        st.session_state[key] = default

st.markdown("""
<div class="brand">
    <div class="brand-icon">✚</div>
    <div>
        <div class="brand-title">QueryFix AI</div>
        <div class="brand-sub">Analysis Console · Natural language to SQL</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Helper function to render any DataFrame as a clean Custom Pure Black HTML Table
def render_html_df(df):
    if df.empty:
        st.info("No data available.")
        return
    html = '<div class="custom-table-container"><table class="custom-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df.iterrows():
        html += '<tr>'
        for val in row:
            html += f'<td>{val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

# Helper function specifically for schema tables
def render_schema_table(columns_data):
    df_schema = pd.DataFrame(columns_data, columns=["Column", "Type"])
    render_html_df(df_schema)

# Top row: Two balanced columns for Ask Your Data & Execution Pipeline
left, right = st.columns([1, 1], gap="large")

with left:
    with st.container(border=True):
        st.markdown('<div class="kicker">01 / ASK YOUR DATA</div><div class="panel-title">What would you like to know?</div><div class="muted">Ask in plain English. QueryFix generates SQL and repairs execution errors.</div>', unsafe_allow_html=True)
        
        # 1. Quick prompt buttons
        excols = st.columns(3)
        for col, label, value in zip(excols, ["Monthly revenue", "Top customers", "Low stock"], ["Show monthly revenue by product category for 2025", "List the top 5 customers by total spending", "Which products have fewer than 20 units in stock?"]):
            with col:
                if st.button(label, key="ex_" + label, use_container_width=True):
                    st.session_state.question = value
                    st.rerun()

        # 2. Text input widget using session state key
        question = st.text_area("Your question", key="question", height=100, label_visibility="collapsed", placeholder="e.g. Which category generated the most revenue?")
        
        # 3. Run and Reset buttons (defining run_clicked here)
        run_col, reset_col = st.columns(2)
        with run_col:
            run_clicked = st.button("✦  Run analysis", type="primary", use_container_width=True)
        with reset_col:
            if st.button("Reset session", use_container_width=True):
                st.session_state.attempts = []
                st.session_state.active_panel = "Schema"
                st.rerun()
                
with right:
    with st.container(border=True):
        st.markdown('<div class="kicker">02 / EXECUTION PIPELINE</div><div class="panel-title">From question to verified result</div><div class="muted">Select a stage to inspect what happened.</div>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        for col, name, icon in zip(cols, ["Schema", "Generate", "Execute", "Validate"], ["▦", "⌘", "▶", "✓"]):
            with col:
                if st.button(f"{icon} {name}", key="stage_" + name, use_container_width=True, type="primary" if st.session_state.active_panel == name else "secondary"):
                    st.session_state.active_panel = name
                    
        descriptions = {
            "Schema": "Database structure and available columns.",
            "Generate": "The SQL generated for your question.",
            "Execute": "Execution status and returned rows.",
            "Validate": "A concise audit of actual attempts and the selected query."
        }
        st.markdown(f'<div class="step-note"><b>Status Info:</b> {descriptions[st.session_state.active_panel]}</div>', unsafe_allow_html=True)

# Run Analysis Logic
if run_clicked:
    if not question.strip(): 
        st.warning("Enter a question first.")
    elif not st.secrets.get("GEMINI_API_KEY", ""): 
        st.error("Gemini API key missing. Add it to .streamlit/secrets.toml locally or Streamlit Cloud → App settings → Secrets.")
    else:
        attempts = []
        with st.status("QueryFix is working through the pipeline…", expanded=True) as status:
            schema = get_schema(db_path)
            st.write("Reading database schema…")
            sql = generate_sql(question, schema)
            
            for idx in range(1, 4):
                st.write(f"Executing attempt {idx}…")
                result = run_read_only_query(db_path, sql)
                record = {
                    "attempt": idx, 
                    "sql": sql, 
                    "ok": result["ok"], 
                    "error": result.get("error", ""),
                    "row_count": len(result.get("rows", [])) if result["ok"] else 0, 
                    "columns": result.get("columns", []), 
                    "rows": result.get("rows", []), 
                    "selected": False
                }
                if result["ok"]:
                    record["validation"] = validate_result(question, sql, result["columns"], result["rows"])
                    record["selected"] = True
                    attempts.append(record)
                    break
                attempts.append(record)
                if idx < 3:
                    st.write("Query failed; asking Gemini to repair it using the actual error…")
                    sql = repair_sql(question, schema, sql, result["error"])
                    
            status.update(
                label="Analysis complete" if attempts and attempts[-1]["ok"] else "No executable query found",
                state="complete" if attempts and attempts[-1]["ok"] else "error",
                expanded=False
            )
        st.session_state.attempts = attempts
        st.session_state.active_panel = "Validate" if attempts and attempts[-1]["ok"] else "Execute"
        st.rerun()

# Results Section
attempts = st.session_state.attempts
if attempts and attempts[-1]["ok"]:
    final = next((a for a in attempts if a["selected"]), attempts[-1])
    df = pd.DataFrame(final["rows"], columns=final["columns"])
    
    st.markdown('<div class="panel"><div class="kicker">03 / RESULTS</div><div class="panel-title">Analysis results</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Rows returned", len(df))
    b.metric("Attempts used", len(attempts))
    c.metric("SQL execution", "Passed")
    
    render_html_df(df)
    
    numeric = df.select_dtypes(include="number").columns.tolist()
    other = [x for x in df.columns if x not in numeric]
    if len(df) > 1 and numeric and other:
        x_col = st.selectbox("Group by", other)
        y_col = st.selectbox("Measure", numeric)
        fig = px.bar(df, x=x_col, y=y_col, color_discrete_sequence=["#38bdf8"])
        fig.update_layout(plot_bgcolor="#0b101d", paper_bgcolor="#0b101d", font_color="#f8fafc", margin=dict(l=8, r=8, t=10, b=8))
        st.plotly_chart(fig, use_container_width=True)
        
    verdict = final.get("validation", {})
    if verdict:
        (st.success if verdict.get("supported") else st.info)("Result sanity check: " + verdict.get("message", "Logical correctness is not guaranteed."))
    st.markdown('</div>', unsafe_allow_html=True)
elif attempts:
    st.error("No attempt produced an executable query. Inspect the attempt history below.")

# Inspection Details Section
st.markdown(f'<div class="kicker" style="margin-top: 28px;">04 / INSPECTION</div><div class="panel-title">Pipeline details · {st.session_state.active_panel}</div>', unsafe_allow_html=True)

active = st.session_state.active_panel
if active == "Schema":
    for table, columns in get_schema(db_path).items():
        with st.expander(f"Table: {table}", expanded=True):
            render_schema_table(columns)
elif active == "Generate":
    if attempts:
        st.caption("First generated SQL — actual model output")
        st.code(attempts[0]["sql"], language="sql")
        if len(attempts) > 1: 
            st.caption("Retry SQL summaries are shown in Validate.")
    else: 
        st.info("Run an analysis to see generated SQL.")
elif active == "Execute":
    if attempts:
        for a in attempts:
            if a["ok"]: 
                st.success(f'Attempt {a["attempt"]}: executed successfully; {a["row_count"]} rows returned.')
            else: 
                st.error(f'Attempt {a["attempt"]} failed: {a["error"]}')
                st.code(a["sql"], language="sql")
    else: 
        st.info("No execution history yet.")
elif active == "Validate":
    if attempts:
        rows = []
        for a in attempts:
            summary = " ".join(a["sql"].split())
            if len(summary) > 100: 
                summary = summary[:97] + "..."
            rows.append({
                "Attempt": a["attempt"],
                "Generated SQL (summary)": summary,
                "Result / error": f'{a["row_count"]} rows returned' if a["ok"] else a["error"],
                "Status": ("✓ Passed · FINAL" if a["selected"] else "✓ Passed") if a["ok"] else "✕ Failed"
            })
        render_html_df(pd.DataFrame(rows))
        if attempts[-1]["ok"]:
            st.success(f'Attempt {attempts[-1]["attempt"]} executed successfully and was selected as the final query. Execution success does not prove logical correctness.')
        else: 
            st.warning("No successful attempt within the retry limit.")
    else: 
        st.info("Run a question to populate the real attempt table; no fake attempts are shown.")

st.markdown('<div style="text-align:center;color:#64748b;font-size:.78rem;padding:20px 12px">QueryFix AI · Synthetic demo data · Read-only SQL · Maximum 3 attempts</div>', unsafe_allow_html=True)