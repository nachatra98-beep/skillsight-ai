"""
SkillSight AI - Intelligent Rule-Based & Semantic Chatbot Engine
Provides real-time answers for skill demand, job trends, upskill course suggestions,
outdated technology warnings, and system usage guidance as specified in SRS 3.8.
"""
import re
from database import db

class SkillSightChatbot:
    def __init__(self):
        self.intents = [
            ("outdated", [r"outdated", r"obsolete", r"legacy", r"avoid", r"deprecat", r"old skill", r"old course"]),
            ("upskill", [r"upskill", r"recommend", r"courses? to take", r"best course", r"learn", r"study", r"start course"]),
            ("in_demand", [r"in.?demand", r"growing", r"trending", r"top skill", r"future skill", r"popular"]),
            ("jobs_country", [r"job.*(usa|india|uk|canada|europe|asia)", r"(usa|india|uk|canada|europe|asia).*job", r"job market", r"openings"]),
            ("forecast", [r"forecast", r"predict", r"12 month", r"growth", r"demand.*next", r"trend"]),
            ("time_to_hire", [r"time to hire", r"hiring duration", r"how long.*hire"]),
            ("greeting", [r"^hi", r"^hello", r"^hey", r"^greetings", r"^good morning", r"^good afternoon"])
        ]

    def detect_intent(self, user_msg):
        msg = user_msg.lower().strip()
        for intent, patterns in self.intents:
            for p in patterns:
                if re.search(p, msg):
                    return intent
        return "general"

    def respond(self, user_msg):
        intent = self.detect_intent(user_msg)
        msg = user_msg.lower()

        # 1. OUTDATED SKILLS OR COURSES
        if intent == "outdated":
            outdated_courses = db.query("SELECT title, key_reason, replacement_course FROM courses WHERE status = 'outdated' LIMIT 3")
            outdated_skills = db.query("SELECT skill_name, outdated_reason FROM skills WHERE is_outdated = 1 LIMIT 3")
            
            reply = "⚠️ **Skills & Courses Becoming Outdated**:\n\n"
            reply += "Technology evolves rapidly, and these legacy skills have declining demand:\n"
            for c in outdated_courses:
                reply += f"• **{c['title']}**: {c['key_reason']}"
                if c['replacement_course']:
                    reply += f" *(Recommended upgrade: **{c['replacement_course']}**)*"
                reply += "\n"
            reply += "\n💡 *Tip: We suggest focusing your training budget and time on modern cloud-native and AI equivalents.*"
            return {"reply": reply, "intent": intent, "badge": "Alert", "type": "outdated_alert"}

        # 2. COURSES / UPSKILLING
        if intent == "upskill":
            courses = db.query("SELECT title, domain, level, duration, is_free FROM courses WHERE status = 'upskill' ORDER BY relevance_score DESC LIMIT 3")
            reply = "🚀 **Recommended Upskill Courses for Current Market Demand**:\n\n"
            for c in courses:
                free_tag = "Free" if c['is_free'] else "Certified"
                reply += f"• **{c['title']}** ({c['domain']})\n   Level: {c['level']} | Duration: {c['duration']} | **[{free_tag}]**\n"
            reply += "\n👉 Click on **'Courses'** on the left menu or explore the **Courses for You** section to get started directly!"
            return {"reply": reply, "intent": intent, "badge": "Recommendation", "type": "course_recommendation"}

        # 3. IN-DEMAND SKILLS
        if intent == "in_demand" or ("which skills" in msg or "what skills" in msg):
            skills = db.query("SELECT skill_name, category, growth_rate FROM skills WHERE is_outdated = 0 ORDER BY growth_rate DESC LIMIT 4")
            reply = "📈 **Top In-Demand Skills Globally (2026-2027)**:\n\n"
            for s in skills:
                reply += f"• **{s['skill_name']}** ({s['category']}): Projected growth of **+{s['growth_rate']}%** YoY\n"
            reply += "\n💡 Employers worldwide are heavily investing in AI/ML, Cloud Infrastructure, and Data Automation."
            return {"reply": reply, "intent": "in_demand", "badge": "Market Intelligence", "type": "skill_growth"}

        # 4. JOB MARKET / COUNTRIES
        if intent == "jobs_country":
            if "india" in msg:
                reply = "🇮🇳 **India Job Market Overview**:\n• **3.1M** Active Job Seekers (35.6% global share)\n• Highest hiring velocity in Software Engineering, AI/ML, and Cloud Services\n• Bengaluru, Hyderabad, and Pune lead in open requisitions."
            elif "usa" in msg:
                reply = "🇺🇸 **USA Job Market Overview**:\n• **1.8M** Active Job Seekers (20.7% global share)\n• Dominant demand in AI Engineering, Cybersecurity, and AWS/Azure Cloud Infrastructure\n• Average time-to-hire: ~30 days."
            elif "uk" in msg:
                reply = "🇬🇧 **UK Job Market Overview**:\n• **1.2M** Active Job Seekers (13.8% global share)\n• Strong growth in FinTech, Healthcare Data Analytics, and Green Tech skills."
            else:
                reply = "🌍 **Global Job Market Overview**:\n• **Total Job Openings**: 12.4M (+6.3% increase)\n• **Active Job Seekers**: 8.7M (+4.1% increase)\n• **In-Demand Skills Identified**: 245+ across 45 countries\n• Leading hiring regions: Asia (4.7M jobs), North America (2.8M jobs), Europe (2.1M jobs)."
            return {"reply": reply, "intent": "jobs_country", "badge": "Regional Data", "type": "regional_stats"}

        # 5. FORECAST
        if intent == "forecast":
            reply = "📊 **12-Month Skill Demand Forecast**:\n\n"
            reply += "• **AI & Machine Learning**: Fastest growth from 20K to 147K monthly hiring mentions (+32.8%)\n"
            reply += "• **Python for Data Science**: Projected to cross 142K openings by November\n"
            reply += "• **Cloud Computing (AWS/GCP)**: Steady climb toward 105K monthly demand\n"
            reply += "• **Data Analysis & SQL**: Sustained baseline above 108K monthly roles."
            return {"reply": reply, "intent": "forecast", "badge": "Forecasting", "type": "forecast_data"}

        # 6. TIME TO HIRE
        if intent == "time_to_hire":
            reply = "⏱️ **Average Time to Hire**: **32 Days** (down -8.1% compared to previous cycle), driven by AI-powered matching and skill-based recruitment."
            return {"reply": reply, "intent": "time_to_hire", "badge": "Metric", "type": "metric"}

        # 7. GREETING
        if intent == "greeting":
            reply = "Hi! 👋 I am **SkillSight AI Assistant**. I can help you with:\n\n"
            reply += "• Identifying **in-demand vs. outdated skills**\n"
            reply += "• Recommending **upskill courses** with high career ROI\n"
            reply += "• Exploring **global job market trends** and hiring forecasts\n\n"
            reply += "Feel free to ask a question or click any of the suggestion chips below!"
            return {"reply": reply, "intent": "greeting", "badge": "SkillSight AI", "type": "welcome"}

        # FALLBACK
        fallback = "I can help clarify questions on **skill demand forecasts**, **upskilling courses**, **outdated legacy tools**, and **regional job market analytics**.\n\nTry asking:\n• *'Which skills are in demand?'*\n• *'What courses should I take?'*\n• *'Show me outdated skills to avoid'*\n• *'Show me job trends in USA or India'*"
        return {"reply": fallback, "intent": "fallback", "badge": "Help & Guidance", "type": "fallback"}

chatbot = SkillSightChatbot()
