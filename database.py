

import sqlite3

def save_result(name, exam, math_score, physics_score, chemistry_score):
    conn = sqlite3.connect("learnmate.db")

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                exam TEXT,
                mathematics INTEGER,
                physics INTEGER,
                chemistry INTEGER,
                total_score INTEGER,
                accuracy REAL
            )
        """)

        total = math_score + physics_score + chemistry_score
        accuracy = (total / 60) * 100

        cursor.execute("""
            INSERT INTO results (
                student_name, exam, mathematics, physics,
                chemistry, total_score, accuracy
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            name, exam, math_score, physics_score,
            chemistry_score, total, accuracy
        ))

        conn.commit()

    finally:
        conn.close()

def get_results():
    conn = sqlite3.connect("learnmate.db")

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                exam TEXT,
                mathematics INTEGER,
                physics INTEGER,
                chemistry INTEGER,
                total_score INTEGER,
                accuracy REAL
            )
        """)

        cursor.execute("""
            SELECT id, student_name, exam, mathematics,
                   physics, chemistry, total_score, accuracy
            FROM results
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()
