# SkillSight AI — AI-Enabled Labour Market Intelligence & Skill Forecasting Engine

An end-to-end intelligent web platform that analyzes job market demands, forecasts skill demand/supply trends, classifies courses into **Upskill (Recommended)** vs. **Outdated**, and features an interactive **AI Chatbot Assistant** to solve user doubts in real-time.

---

## 🛠️ Technology Stack & Constraints Compliance
1. **Frontend**: HTML5, CSS3, Modern JavaScript (ES6+), Plotly & Chart.js, Feather Icons.
2. **Backend**: Python Flask REST API, CORS support, PyMySQL, Statistical forecasting models.
3. **Database**: MySQL 8.x schema (`schema.sql`) with seamless fallback to embedded store (`skillsight.db`).
4. **Core Capabilities**:
   - **Upskill vs Outdated Courses**: Courses analyzed with relevance scoring, reasons, and modern replacement pathways (e.g. Legacy Java to Modern Spring Boot/Java 21, Flash to HTML5/Canvas, VB6 to .NET 9).
   - **Interactive AI Chatbot**: Real-time intent detection for market queries, skills forecasts, country trends (India, USA, UK, Global), and course recommendations.
   - **Labour Market Intelligence**: Interactive charts with 6M, 1Y, and 2Y forecasting horizons, country hiring distribution, and key KPIs.

---

## 🚀 How to Run the Application

### 1. Install Dependencies
```bash
pip install flask flask-cors pymysql
```

### 2. (Optional) Configure MySQL
If you have MySQL running locally, create the database using `schema.sql`:
```bash
mysql -u root -p < schema.sql
```
*Note: If MySQL is not running or credentials are not supplied, the app automatically runs on the integrated SQLite store (`skillsight.db`) with complete pre-seeded data.*

### 3. Initialize Database & Seed Data
```bash
python init_db.py
```

### 4. Start the Flask Server
```bash
python app.py
```
Open your browser at: **`http://127.0.0.1:5000`**

---

## 📂 Project Architecture
```text
skillsight AI/
├── app.py              # Flask server & REST API endpoints
├── chatbot.py          # AI chatbot intent & retrieval engine
├── database.py         # MySQL connection & query abstraction layer
├── init_db.py          # Database initializer and seed dataset
├── schema.sql          # MySQL database schema definition
├── static/
│   ├── app.js          # Client-side controller, chart rendering & chat logic
│   └── style.css       # Responsive styling matching reference UI
└── templates/
    └── index.html      # Dashboard presentation tier
```
