"""
SkillSight AI - Flask Application Backend Server
Provides REST API endpoints for:
1. Dashboard KPIs & Global Job Market Data
2. Skill Demand Forecasting (Time Series)
3. Courses Analysis (Upskill vs Outdated)
4. AI Chatbot Assistant for user doubts
5. Reports and Search
"""
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from database import db
from chatbot import chatbot
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Ensure static & templates directory exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# ----------------- UI ROUTE -----------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------- API ENDPOINTS -----------------

@app.route("/api/dashboard/overview", methods=["GET"])
def get_dashboard_overview():
    """Returns top KPI metrics and overview statistics matching the reference UI."""
    return jsonify({
        "status": "success",
        "kpis": {
            "total_job_openings": "12.4M",
            "job_openings_growth": "+6.3%",
            "active_job_seekers": "8.7M",
            "job_seekers_growth": "+4.1%",
            "in_demand_skills": "245+",
            "in_demand_growth": "+12.7%",
            "avg_time_to_hire": "32 Days",
            "time_to_hire_change": "-8.1%"
        },
        "regions": [
            {"name": "Asia", "jobs": "4.7M Jobs", "growth": "+7.1%", "coords": [100, 35]},
            {"name": "North America", "jobs": "2.8M Jobs", "growth": "+5.2%", "coords": [-100, 40]},
            {"name": "Europe", "jobs": "2.1M Jobs", "growth": "+3.9%", "coords": [15, 50]},
            {"name": "S. America", "jobs": "1.2M Jobs", "growth": "+2.8%", "coords": [-60, -15]}
        ],
        "job_seekers_by_country": [
            {"country": "India", "flag": "🇮🇳", "count": "3.1M", "percentage": 35.6, "color": "#4361ee"},
            {"country": "USA", "flag": "🇺🇸", "count": "1.8M", "percentage": 20.7, "color": "#7209b7"},
            {"country": "UK", "flag": "🇬🇧", "count": "1.2M", "percentage": 13.8, "color": "#3a0ca3"},
            {"country": "Canada", "flag": "🇨🇦", "count": "1.0M", "percentage": 11.5, "color": "#4cc9f0"},
            {"country": "Others", "flag": "🌐", "count": "2.5M", "percentage": 18.4, "color": "#90e0ef"}
        ],
        "ai_insights": [
            {"title": "Python and Data Analysis skills", "desc": "are expected to grow by 18% in the next 6 months globally.", "status": "positive"},
            {"title": "Healthcare & Green Skills", "desc": "are emerging strongly across renewable infrastructure.", "status": "emerging"},
            {"title": "Demand for Cloud Computing", "desc": "will rise by 14% in 2026 across enterprise migrations.", "status": "positive"}
        ]
    })

@app.route("/api/forecast/demand", methods=["GET"])
def get_forecast():
    """Returns monthly demand forecast time-series for chart rendering."""
    range_filter = request.args.get("range", "1Y")  # 6M, 1Y, 2Y
    
    months = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    if range_filter == "6M":
        months = months[:6]
    
    rows = db.query("SELECT skill_name, month_label, demand_count, period_order FROM demand_timeseries ORDER BY period_order ASC")
    
    series_map = {}
    for r in rows:
        skill = r['skill_name']
        if skill not in series_map:
            series_map[skill] = []
        if r['month_label'] in months:
            series_map[skill].append(r['demand_count'])

    return jsonify({
        "status": "success",
        "months": months,
        "series": [
            {"name": "Python", "data": series_map.get("Python", []), "color": "#4361ee"},
            {"name": "Data Analysis", "data": series_map.get("Data Analysis", []), "color": "#4cc9f0"},
            {"name": "Cloud Computing", "data": series_map.get("Cloud Computing", []), "color": "#2ec4b6"},
            {"name": "AI & ML", "data": series_map.get("AI & ML", []), "color": "#f77f00"}
        ]
    })

@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Fetches courses classified as upskill, outdated, or all."""
    status = request.args.get("status")  # upskill, outdated, or None
    search = request.args.get("q", "").strip()

    sql = "SELECT * FROM courses"
    params = []
    conditions = []

    if status and status != "all":
        conditions.append("status = %s")
        params.append(status)

    if search:
        conditions.append("(title LIKE %s OR domain LIKE %s OR provider LIKE %s)")
        like_str = f"%{search}%"
        params.extend([like_str, like_str, like_str])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY relevance_score DESC"
    courses = db.query(sql, tuple(params))
    return jsonify({"status": "success", "count": len(courses), "courses": courses})

@app.route("/api/courses/summary", methods=["GET"])
def get_courses_summary():
    """Returns curated upskill and outdated courses directly for the dashboard view."""
    upskill = db.query("SELECT * FROM courses WHERE status = 'upskill' ORDER BY relevance_score DESC LIMIT 3")
    outdated = db.query("SELECT * FROM courses WHERE status = 'outdated' ORDER BY relevance_score ASC LIMIT 3")
    return jsonify({
        "status": "success",
        "upskill_courses": upskill,
        "outdated_courses": outdated
    })

@app.route("/api/skills/trending", methods=["GET"])
def get_trending_skills():
    """Returns top in-demand skills and outdated/declining skills."""
    in_demand = db.query("SELECT * FROM skills WHERE is_outdated = 0 ORDER BY growth_rate DESC LIMIT 8")
    outdated = db.query("SELECT * FROM skills WHERE is_outdated = 1 ORDER BY growth_rate ASC LIMIT 8")
    return jsonify({
        "status": "success",
        "in_demand_skills": in_demand,
        "outdated_skills": outdated
    })

@app.route("/api/chatbot/message", methods=["POST"])
def chatbot_message():
    """Solves user queries using rule-based/semantic intelligence over MySQL data."""
    data = request.get_json() or {}
    user_query = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session")

    if not user_query:
        return jsonify({"error": "Empty message"}), 400

    # Save user message
    try:
        db.execute(
            "INSERT INTO chat_messages (session_id, sender, message, intent) VALUES (%s, %s, %s, %s)",
            (session_id, "user", user_query, "incoming")
        )
    except Exception as e:
        print("[Chatbot Log Error]", e)

    # Process query
    bot_result = chatbot.respond(user_query)

    # Save bot response
    try:
        db.execute(
            "INSERT INTO chat_messages (session_id, sender, message, intent) VALUES (%s, %s, %s, %s)",
            (session_id, "bot", bot_result["reply"], bot_result.get("intent", "general"))
        )
    except Exception as e:
        print("[Chatbot Log Error]", e)

    return jsonify({
        "status": "success",
        "reply": bot_result["reply"],
        "intent": bot_result.get("intent", "general"),
        "badge": bot_result.get("badge", "SkillSight AI"),
        "type": bot_result.get("type", "text")
    })

@app.route("/api/chatbot/history", methods=["GET"])
def get_chat_history():
    session_id = request.args.get("session_id", "default_session")
    history = db.query("SELECT sender, message, created_at FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC LIMIT 50", (session_id,))
    return jsonify({"status": "success", "history": history})

if __name__ == "__main__":
    print("[SkillSight AI] Starting server at http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
