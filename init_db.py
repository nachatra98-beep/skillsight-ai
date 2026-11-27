"""
SkillSight AI - Database Initializer & Seed Data Generator
Populates all trending skills, historical demand/supply timeseries,
Upskill courses, Outdated courses, and regional analytics matching the SRS and reference UI.
"""
from database import db
import datetime

def init_db():
    print("[SkillSight AI] Initializing tables and schema...")
    
    if db.use_mysql:
        # Tables for MySQL
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'Learner',
            region VARCHAR(100) DEFAULT 'Global',
            target_role VARCHAR(100) DEFAULT 'Software Developer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INT AUTO_INCREMENT PRIMARY KEY,
            skill_name VARCHAR(100) NOT NULL UNIQUE,
            category VARCHAR(100) NOT NULL,
            growth_rate DECIMAL(5,2) DEFAULT 0.00,
            demand_level VARCHAR(50) DEFAULT 'Moderate',
            is_outdated BOOLEAN DEFAULT FALSE,
            outdated_reason TEXT NULL
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            provider VARCHAR(150) NOT NULL,
            level VARCHAR(50) DEFAULT 'Beginner',
            duration VARCHAR(50) DEFAULT '4 Weeks',
            domain VARCHAR(100) NOT NULL,
            status VARCHAR(50) DEFAULT 'upskill',
            relevance_score INT DEFAULT 85,
            key_reason TEXT,
            replacement_course VARCHAR(200) NULL,
            is_free BOOLEAN DEFAULT TRUE,
            badge_icon VARCHAR(50) DEFAULT 'code'
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS demand_timeseries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            skill_name VARCHAR(100) NOT NULL,
            month_label VARCHAR(20) NOT NULL,
            demand_count INT NOT NULL,
            period_order INT NOT NULL
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(100) NOT NULL,
            sender VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            intent VARCHAR(50) DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    else:
        # Tables for SQLite
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'Learner',
            region TEXT DEFAULT 'Global',
            target_role TEXT DEFAULT 'Software Developer',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            growth_rate REAL DEFAULT 0.00,
            demand_level TEXT DEFAULT 'Moderate',
            is_outdated INTEGER DEFAULT 0,
            outdated_reason TEXT NULL
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            provider TEXT NOT NULL,
            level TEXT DEFAULT 'Beginner',
            duration TEXT DEFAULT '4 Weeks',
            domain TEXT NOT NULL,
            status TEXT DEFAULT 'upskill',
            relevance_score INTEGER DEFAULT 85,
            key_reason TEXT,
            replacement_course TEXT NULL,
            is_free INTEGER DEFAULT 1,
            badge_icon TEXT DEFAULT 'code'
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS demand_timeseries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            month_label TEXT NOT NULL,
            demand_count INTEGER NOT NULL,
            period_order INTEGER NOT NULL
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            intent TEXT DEFAULT 'general',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

    seed_data()

def seed_data():
    existing_skills = db.query("SELECT COUNT(*) as count FROM skills")
    if existing_skills and existing_skills[0]['count'] > 0:
        print("[SkillSight AI] Database already contains initial seed data.")
        return

    print("[SkillSight AI] Seeding skills, courses, time series, and analytics...")

    # 1. Skills
    skills_data = [
        # In-Demand / Upskill Skills
        ("Python", "Programming", 24.5, "Very High", 0, None),
        ("Data Analysis", "Data Science", 18.2, "Very High", 0, None),
        ("Cloud Computing (AWS/GCP/Azure)", "Cloud & DevOps", 21.0, "Very High", 0, None),
        ("AI & Machine Learning", "Artificial Intelligence", 32.8, "Very High", 0, None),
        ("SQL & Database Engineering", "Database", 14.2, "High", 0, None),
        ("Cybersecurity & Zero Trust", "Security", 19.5, "High", 0, None),
        ("React & Modern Frontend", "Web Development", 16.4, "High", 0, None),
        ("Docker & Kubernetes", "Cloud & DevOps", 22.1, "Very High", 0, None),

        # Outdated / Declining Skills
        ("Java (Legacy / J2EE / Applets)", "Programming", -28.4, "Declining", 1, "Replaced by Modern Spring Boot, Kotlin, and Cloud-Native Microservices"),
        ("Microsoft Office 2010", "Productivity", -45.0, "Declining", 1, "Obsolete. Replaced by Microsoft 365, Copilot & Google Workspace"),
        ("Basic Excel (Old Formulas / Manual Entry)", "Productivity", -34.0, "Declining", 1, "Replaced by Excel with Power BI, Python integration & modern DAX"),
        ("Flash & ActionScript", "Web Development", -92.0, "Declining", 1, "Deprecated globally. Modern Web runs on HTML5/Canvas/WebGL"),
        ("Objective-C", "Mobile Development", -48.2, "Declining", 1, "Superseded by Swift and Cross-Platform Flutter"),
        ("Visual Basic 6 (VB6)", "Software Engineering", -62.0, "Declining", 1, "Legacy system without modern security or cloud compatibility"),
        ("COBOL (Maintenance Only)", "Mainframe", -19.5, "Declining", 1, "Limited to legacy bank maintenance; modern workloads migrate to cloud microservices")
    ]

    for name, cat, rate, demand, outdated, reason in skills_data:
        db.execute(
            "INSERT INTO skills (skill_name, category, growth_rate, demand_level, is_outdated, outdated_reason) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, cat, rate, demand, outdated, reason)
        )

    # 2. Courses (Upskill & Outdated)
    courses_data = [
        # --- UPSKILL COURSES ---
        ("Python for Data Science", "SkillSight Academy", "Beginner", "6 Weeks", "Data Science", "upskill", 96, "High hiring demand (+24.5%), positive skill shortage in US/EU/Asia.", None, 1, "python"),
        ("AWS Cloud Fundamentals (Certified)", "CloudTech Global", "Intermediate", "8 Weeks", "Cloud & DevOps", "upskill", 94, "Global enterprise cloud migration rising by 21% annually.", None, 0, "cloud"),
        ("Data Analytics with SQL & PowerBI", "DataForge", "Beginner", "5 Weeks", "Data Science", "upskill", 91, "Core prerequisite for business analysts with 30k+ active vacancies.", None, 1, "database"),
        ("Deep Learning & LLM Engineering", "AI Institute", "Advanced", "10 Weeks", "Artificial Intelligence", "upskill", 98, "Fastest growing demand category (+32.8% YoY).", None, 0, "brain"),
        ("Full-Stack Modern Web (React + Node)", "DevSprint", "Intermediate", "8 Weeks", "Web Development", "upskill", 88, "High market adoption across 4.7M open tech positions.", None, 1, "globe"),
        ("Docker & Kubernetes Containerization", "DevOps Pro", "Intermediate", "6 Weeks", "Cloud & DevOps", "upskill", 92, "Standard for production cloud operations and CI/CD pipelines.", None, 1, "server"),

        # --- OUTDATED COURSES ---
        ("Java (Legacy J2EE & Applets)", "OldTech Training", "Beginner", "4 Weeks", "Programming", "outdated", 22, "Demand down -28.4%. Employers require Modern Spring Boot or Cloud-Native Java.", "Modern Java 21 & Spring Boot Microservices", 1, "alert-triangle"),
        ("Microsoft Office 2010 Mastery", "Classic Computer Classes", "Beginner", "3 Weeks", "Office Tools", "outdated", 15, "Unsupported software. Workplaces use Microsoft 365, AI Copilot, and GSuite.", "Microsoft 365 & Copilot Automation", 1, "alert-triangle"),
        ("Basic Excel (Old Version & Manual Entry)", "OfficeSkills 2007", "Beginner", "2 Weeks", "Office Tools", "outdated", 31, "Traditional manual entry replaced by Automated Power Query, DAX & Python in Excel.", "Data Analytics with Modern Excel & Power BI", 1, "alert-triangle"),
        ("ActionScript 3 & Adobe Flash Design", "Legacy Media School", "Intermediate", "5 Weeks", "Design", "outdated", 8, "Flash player discontinued worldwide and blocked on modern browsers.", "HTML5 Canvas, CSS3 & Three.js Interactive Web", 1, "alert-triangle"),
        ("Objective-C iOS App Development", "Mobile Past Hub", "Intermediate", "6 Weeks", "Mobile Development", "outdated", 28, "Apple ecosystem officially transitioned to Swift and SwiftUI.", "iOS App Development with Swift 6 & SwiftUI", 0, "alert-triangle"),
        ("Visual Basic 6 Desktop Systems", "Enterprise Archive", "Beginner", "4 Weeks", "Desktop Software", "outdated", 12, "Architecture unsupported on modern 64-bit systems; migrate to C# / .NET 9.", "C# and .NET 9 Modern Software Development", 1, "alert-triangle")
    ]

    for title, prov, lvl, dur, dom, st, score, rsn, rep, free, badge in courses_data:
        db.execute(
            """INSERT INTO courses (title, provider, level, duration, domain, status, relevance_score, key_reason, replacement_course, is_free, badge_icon)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (title, prov, lvl, dur, dom, st, score, rsn, rep, free, badge)
        )

    # 3. Monthly Demand Forecast Series (Dec -> Nov matching Reference UI)
    months = ["Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    trend_series = {
        "Python": [42000, 48000, 56000, 65000, 74000, 83000, 92000, 101000, 110000, 120000, 131000, 142000],
        "Data Analysis": [32000, 36000, 41000, 48000, 54000, 61000, 68000, 75000, 82000, 90000, 99000, 108000],
        "Cloud Computing": [28000, 32000, 37000, 43000, 49000, 56000, 63000, 71000, 79000, 87000, 96000, 105000],
        "AI & ML": [20000, 24000, 30000, 37000, 46000, 56000, 68000, 81000, 95000, 111000, 128000, 147000]
    }

    for skill, counts in trend_series.items():
        for order, (m, cnt) in enumerate(zip(months, counts)):
            db.execute(
                "INSERT INTO demand_timeseries (skill_name, month_label, demand_count, period_order) VALUES (%s, %s, %s, %s)",
                (skill, m, cnt, order)
            )

    print("[SkillSight AI] Initial data seeding completed successfully!")

if __name__ == "__main__":
    init_db()
