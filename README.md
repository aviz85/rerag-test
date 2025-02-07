# ReAG Streamlit Demo

A simple demo UI for ReAG (Reasoning Augmented Generation) using Streamlit.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run Streamlit app:
```bash
streamlit run app.py
```

## Features

- Add and manage documents with metadata
- Configure model and API settings
- Submit queries and view responses with reasoning
- Interactive UI for document management

## Requirements

- Python 3.9+
- Streamlit
- ReAG SDK
- Running LLM API (e.g., Ollama with deepseek-r1:14b model) 