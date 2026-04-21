# 🌊 Río Ozama Data Sentinel

> **Bridging the information gap on one of the Dominican Republic's most important and polluted rivers.**

An open-source, AI-powered full-stack platform that aggregates, processes, and visualizes historical water quality data for the **Río Ozama** — transforming scattered public reports into a centralized, interactive intelligence dashboard.

---

## 📖 Background

The Río Ozama flows through the heart of Santo Domingo, yet comprehensive, machine-readable water quality data has historically been scattered across PDF reports and government documents — or simply unavailable online. This project was built to **close that information gap**.

Using an AI-driven ETL pipeline, the platform extracts measurement data from institutional PDF reports (e.g., URBE), stores it in a structured relational database, and exposes it through an interactive dashboard that tracks contamination trends and legal compliance over time.

---

## ✨ Features

- 🧠 **AI-Powered PDF Ingestion** — Gemini AI parses complex environmental reports and extracts structured measurement data automatically
- 📊 **Interactive Dashboard** — Multi-chart React frontend with time-series graphs and compliance status indicators
- ⚡ **High-Performance API** — Flask API backed by a PostgreSQL materialized view for fast queries
- 🗺️ **Location-Aware Data** — Measurements are geo-tagged by sampling site along the river
- ✅ **Compliance Monitoring** — Measures each reading against Dominican Republic legal limits (`limite_maximo` / `limite_minimo`)
- 🔄 **Incremental Data Loading** — Smart deduplication maps incoming PDF data to existing locations and contaminant parameters

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────┐
│                     Data Sources                           │
│         URBE PDF Reports (2012, 2013, ...)                 │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│              AI ETL Pipeline  (Python)                     │
│  PyPDF2 → Gemini AI (JSON extraction) → SQLAlchemy         │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│          Database  (Neon PostgreSQL)                       │
│   ubicaciones | parametros | mediciones | normas_legales   │
│          mv_mediciones_estado (Materialized View)          │
└──────────────────────┬─────────────────────────────────────┘
                       │
               ┌───────┴────────┐
               ▼                ▼
┌──────────────────────┐  ┌──────────────────────────────────┐
│   Flask REST API     │  │   React + Vite Dashboard         │
│   /api/mediciones    │  │   Chart.js · lucide-react        │
└──────────────────────┘  └──────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI / LLM** | Google Gemini API (`gemini-3-flash-preview`) |
| **PDF Parsing** | PyPDF2 |
| **Backend API** | Python · Flask · Flask-CORS |
| **Database** | Neon (Serverless PostgreSQL) · SQLAlchemy |
| **Frontend Framework** | React 19 · Vite |
| **Charts** | Chart.js · react-chartjs-2 |
| **Icons** | lucide-react |
| **ORM / Queries** | SQLAlchemy Core (raw SQL with `text()`) |

---

## 📁 Project Structure

```
Ozama_River_Analysis/
├── data/                        # Raw source PDF reports
│   ├── URBE_Informe_2012.pdf
│   └── URBE_Informe_2013.pdf
│
├── src/                         # Python backend & pipeline
│   ├── api.py                   # Flask REST API gateway
│   ├── chatbot.py               # Gemini AI wrapper class
│   ├── database_controller.py   # SQLAlchemy DB helper class
│   └── ingesta_historica.py     # AI-powered ETL pipeline script
│
├── frontend/                    # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx              # Main dashboard component
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── .env                         # Environment variables (not committed)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Neon](https://neon.tech) PostgreSQL database
- A Google Gemini API key

### 1. Clone the Repository

```bash
git clone https://github.com/Josriel123/Ozama_River_Analysis.git
cd Ozama_River_Analysis
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
API_KEY=your_google_gemini_api_key
DB_URL=postgresql://user:password@your-neon-host/neondb?sslmode=require
```

### 3. Set Up the Python Backend

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install flask flask-cors sqlalchemy psycopg2-binary python-dotenv PyPDF2 google-genai
```

### 4. Run the AI Ingestion Pipeline

Place your PDF reports in the `data/` folder, then run:

```bash
python src/ingesta_historica.py
```

The Gemini AI will extract all water quality measurements from the PDF and load them into the database automatically.

### 5. Start the Flask API

```bash
python src/api.py
# API now running at http://127.0.0.1:5000
```

### 6. Start the Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
# Dashboard now running at http://localhost:5173
```

---

## 📡 API Reference

### `GET /api/mediciones`

Returns all water quality measurements with compliance status from the materialized view.

**Response example:**

```json
[
  {
    "id": 1,
    "fecha": "2013-08-01",
    "valor": 4.5,
    "operador": "<",
    "ubicacion": "Sabana Larga",
    "latitud": 18.4861,
    "longitud": -69.9312,
    "parametro": "DBO5",
    "unidad": "mg/L",
    "limite_maximo": 5.0,
    "limite_minimo": null,
    "estado": "CUMPLE"
  }
]
```

---

## 🤝 Contributing

Contributions are welcome! If you have access to additional URBE reports, INDRHI studies, or other public environmental data about the Río Ozama, feel free to open a PR or an issue.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-data-source`)
3. Commit your changes (`git commit -m 'Add data from INDRHI 2018 report'`)
4. Push and open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Joel B.** — [@Josriel123](https://github.com/Josriel123)

*Built to make environmental data about the Dominican Republic more accessible to researchers, policy makers, and the public.*
