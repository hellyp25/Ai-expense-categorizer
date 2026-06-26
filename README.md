# AI Financial Assistant

## Overview

AI Financial Assistant is an intelligent expense analysis application built with Python and Streamlit. It enables users to upload financial statements in multiple formats, automatically categorize transactions using Google's Gemini AI, detect unusual spending patterns using machine learning, forecast future expenses, and interact with their financial data through a Retrieval-Augmented Generation (RAG) chatbot.

The project combines Generative AI, Natural Language Processing (NLP), Machine Learning, and data visualization to provide actionable financial insights.

---

## Features

* 📂 Upload financial statements in **CSV, Excel (XLS/XLSX), ODS, and PDF** formats.
* 🤖 AI-powered transaction categorization using **Google Gemini**.
* 🧠 Intelligent financial insights and spending summaries.
* 🔍 Anomaly detection using the **Isolation Forest** algorithm.
* 📈 Expense forecasting using **Facebook Prophet**.
* 💬 RAG-based chatbot for querying uploaded financial data.
* 📊 Interactive dashboard with charts and key financial metrics.
* 📄 Export processed data as CSV and generate PDF reports.
* 🔄 Automatic column detection for different bank statement formats.

---

## Technologies Used

* Python
* Streamlit
* Pandas
* Plotly
* Google Gemini API
* Sentence Transformers
* FAISS
* Scikit-learn
* Prophet
* ReportLab
* PDFPlumber
* OpenPyXL

---

## Dataset

The application accepts user-uploaded financial statements rather than relying on a fixed dataset.

Supported formats include:

* CSV
* XLS
* XLSX
* ODS
* PDF

Expected transaction fields include:

* Transaction Date
* Description / Narration
* Amount (or Debit & Credit)

The preprocessing module automatically detects and standardizes these columns for analysis.

---

## Workflow

1. Upload a financial statement.
2. Automatically detect and clean transaction data.
3. Categorize expenses using Gemini AI.
4. Detect anomalous transactions using Isolation Forest.
5. Forecast future expenses using Prophet.
6. Build a FAISS vector database for semantic search.
7. Ask natural language questions through the AI chatbot.
8. View interactive dashboards and download reports.

---

## How to Run

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure API Key

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Run the application

```bash
streamlit run app.py
```

---

## Project Structure

```
AI_Financial_Assistant/
│
├── app.py
├── requirements.txt
├── .env
│
├── modules/
│   ├── ai_categorizer.py
│   ├── data_processor.py
│   ├── ml_engine.py
│   ├── rag_chatbot.py
│   └── report_gen.py
│
└── sample_data/
```

---

## Future Enhancements

* Budget planning and tracking
* Recurring expense detection
* Multi-currency support
* Bank account integration
* Authentication and user profiles
* Cloud deployment
* Advanced financial analytics

---

## Limitations

* AI categorization depends on the availability of the Gemini API.
* Forecast accuracy improves with larger historical datasets.
* PDF extraction quality depends on the formatting of uploaded documents.
* Financial insights are intended for educational and analytical purposes only.

---

## License

This project is developed for educational and portfolio purposes.
