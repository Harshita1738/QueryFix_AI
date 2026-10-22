# 🔍 QueryFix AI — Natural Language to SQL Assistant

> An intelligent database assistant powered by **Google Gemini** and **Streamlit** that translates natural language questions into executable SQL queries, automatically repairs schema mismatches, and visualizes data insights in real time.

---

## 🚀 Overview

**QueryFix AI** bridges the gap between non-technical users and complex database systems. Instead of writing manual SQL queries, users can ask questions in plain English. The underlying AI agent analyzes the database schema, constructs the corresponding SQL query, executes it against an SQLite database, and presents the output in a clean, interactive table.

If a generated query encounters a database execution error, QueryFix AI's self-healing pipeline automatically analyzes the error context and schema structure to fix and re-run the query.

---

## ✨ Core Features

- 💬 **Natural Language Processing:** Converts everyday English questions into precise SQL queries.
- 🛡️ **Self-Healing Query Pipeline:** Automatically detects execution errors, inspects schema definitions, and attempts to repair queries.
- 📊 **Interactive Data Display:** Renders clear tabular views of database results instantly.
- 🔒 **Secure Credentials Management:** Utilizes Streamlit's secrets management (`.streamlit/secrets.toml`) to keep API keys isolated from source code.
- ⚡ **Lightweight & Fast:** Streamlined UI built on Streamlit with AI-powered SQL generation using Google Gemini (`gemini-3.8-flash`).

---

## 🏗️ Architecture & How It Works

1. **User Prompt Input:** The user submits a question via the Streamlit interactive dashboard.
2. **Schema Inspection:** The system dynamically extracts the SQLite database tables, column names, and data types.
3. **AI Query Generation:** The prompt and schema context are sent to the Google Gemini API to construct an accurate SQL query.
4. **Execution & Error Recovery:**
   - The query runs against the SQLite database.
   - If successful, results are rendered in an interactive dataframe.
   - If an error occurs, the self-healing handler captures the error context, sends it to Gemini for correction, and re-executes the corrected query.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Frontend Framework** | [Streamlit](https://streamlit.io/) |
| **LLM Engine** | [Google Gemini API (`google-genai` SDK)](https://ai.google.dev/) |
| **Database** | SQLite3 |
| **Language** | Python 3.11+ |
| **Deployment** | Streamlit Community Cloud |

---

## 📁 Repository Structure

```text
QueryFix_AI/
├── .streamlit/
│   ├── secrets.toml          # Private environment secrets (Git-ignored)
│   └── secrets.toml.example  # Example secrets configuration
├── agent.py                  # Gemini API integration and SQL generation agent
├── app.py                    # Streamlit web frontend and user interface
├── database.py               # SQLite database management and query runner
├── requirements.txt          # Python package dependencies
└── README.md                 # Project documentation
```

---

## 💻 Local Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Harshita1738/QueryFix_AI.git
cd QueryFix_AI
```

### 2. Set Up a Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Local Secrets

Create a file named `secrets.toml` inside the `.streamlit` folder at the root of your project.

If the `.streamlit` folder does not exist, create it first.

Add the following configuration to `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_google_gemini_api_key_here"
GEMINI_MODEL = "gemini-3.8-flash"
```

Replace the placeholder API key with your actual Google Gemini API key.

**Important:** Never commit your actual API key or private secrets to GitHub.

### 5. Launch the Application

```bash
streamlit run app.py
```

---

## 🌐 Live Deployment

This application is deployed on Streamlit Community Cloud.

**Deployment Settings Summary:**

- **Repository:** [Harshita1738/QueryFix_AI](https://github.com/Harshita1738/QueryFix_AI)
- **Branch:** `main`
- **Main File Path:** `app.py`
- **Environment Secrets:** `GEMINI_API_KEY` and `GEMINI_MODEL`, configured under the app's Secrets settings in Streamlit Community Cloud.

---

## 📄 License

This project is licensed under the MIT License.