from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    education_level = db.Column(db.String(60))
    interests = db.Column(db.JSON, default=list)
    skills = db.Column(db.JSON, default=dict)          # {"Python": 80, ...}
    learning_goal = db.Column(db.String(80))
    weekly_hours = db.Column(db.Integer, default=5)
    preferred_difficulty = db.Column(db.String(20), default="Beginner")
    learning_styles = db.Column(db.JSON, default=list)
    assessment_score = db.Column(db.Float, default=50)  # 0-100, input feature for the ML engine
    xp = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def streaks(self):
        """Current/longest streak from DailyActivity (one row per day, so duplicates can't inflate it)."""
        days = sorted(a.day for a in DailyActivity.query.filter_by(student_id=self.id))
        longest = cur = 0
        prev = None
        for d in days:
            cur = cur + 1 if prev and (d - prev).days == 1 else 1
            longest, prev = max(longest, cur), d
        current = cur if days and (date.today() - days[-1]).days <= 1 else 0
        return current, longest, (days[-1] if days else None)

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(60))
    skills = db.Column(db.String(255))
    topics = db.Column(db.String(255))
    difficulty = db.Column(db.String(20))
    duration_hours = db.Column(db.Integer)
    hours_per_week = db.Column(db.Integer, default=4)
    rating = db.Column(db.Float)
    learning_style = db.Column(db.String(120))
    youtube_url = db.Column(db.String(300))
    resource_url = db.Column(db.String(300))
    practice_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Progress(db.Model):
    __tablename__ = "student_progress"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    progress_percentage = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Float, default=0)   # hours
    status = db.Column(db.String(20), default="in_progress")
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    course = db.relationship("Course")
    __table_args__ = (db.UniqueConstraint("student_id", "course_id"),)

class PathItem(db.Model):
    __tablename__ = "learning_path_items"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    position = db.Column(db.Integer)
    course = db.relationship("Course")

class Interaction(db.Model):
    __tablename__ = "course_interactions"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), index=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    action = db.Column(db.String(20))   # view | start | complete | rate
    rating = db.Column(db.Integer)
    comment = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyActivity(db.Model):
    __tablename__ = "daily_activity"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), index=True)
    day = db.Column(db.Date, default=date.today)
    minutes = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint("student_id", "day"),)
