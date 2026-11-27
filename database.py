"""
SkillSight AI - Database Access Layer
Supports MySQL connection with seamless fallback to SQLite / Local Embedded Store
if MySQL server credentials or service is not running locally.
"""
import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_DB = os.environ.get("MYSQL_DB", "skillsight_db")
SQLITE_DB = os.path.join(os.path.dirname(__file__), "skillsight.db")

class Database:
    def __init__(self):
        self.use_mysql = False
        self._test_mysql()

    def _test_mysql(self):
        try:
            conn = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                port=MYSQL_PORT,
                connect_timeout=2
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4;")
            conn.commit()
            conn.close()
            self.use_mysql = True
            print(f"[SkillSight DB] Successfully connected to MySQL server on {MYSQL_HOST}:{MYSQL_PORT} (DB: {MYSQL_DB})")
        except Exception as e:
            self.use_mysql = False
            print(f"[SkillSight DB] MySQL not available ({e}). Using robust embedded SQLite storage.")

    def get_connection(self):
        if self.use_mysql:
            return pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                port=MYSQL_PORT,
                database=MYSQL_DB,
                cursorclass=DictCursor,
                autocommit=True
            )
        else:
            conn = sqlite3.connect(SQLITE_DB)
            conn.row_factory = sqlite3.Row
            return conn

    def query(self, sql, params=()):
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    return cursor.fetchall()
            else:
                # Replace %s with ? for sqlite compatibility
                sqlite_sql = sql.replace("%s", "?")
                cursor = conn.cursor()
                cursor.execute(sqlite_sql, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()

    def execute(self, sql, params=()):
        conn = self.get_connection()
        try:
            if self.use_mysql:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params)
                    return cursor.lastrowid
            else:
                sqlite_sql = sql.replace("%s", "?")
                cursor = conn.cursor()
                cursor.execute(sqlite_sql, params)
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

db = Database()
