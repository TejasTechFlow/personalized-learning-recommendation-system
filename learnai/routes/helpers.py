from datetime import date, datetime
from flask import session
from models.database import db, Student, Progress, DailyActivity

def current_student():
    sid = session.get("sid")
    return db.session.get(Student, sid) if sid else None

def log_activity(student, minutes):
    row = DailyActivity.query.filter_by(student_id=student.id, day=date.today()).first()
    if row:
        row.minutes += minutes
    else:
        db.session.add(DailyActivity(student_id=student.id, day=date.today(), minutes=minutes))

def badges(student):
    cur, longest, _ = student.streaks()
    done = Progress.query.filter_by(student_id=student.id, status="completed").all()
    earned = {
        "Course Complete": bool(done),
        "7-Day Streak": longest >= 7,
        "XP Hunter": student.xp >= 500,
        "ML Explorer": any(p.course.category == "Machine Learning" for p in done),
        "Python Beginner": any(p.course.category == "Python" for p in done),
    }
    return earned
