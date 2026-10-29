from datetime import date, datetime, timedelta
from flask import Blueprint, jsonify, request
from models.database import db, Course, Progress, PathItem, Interaction, DailyActivity
from ml.preprocessing import suggest_interests
from .helpers import current_student, log_activity

bp = Blueprint("api", __name__)

@bp.route("/suggest")
def suggest():
    return jsonify(suggest_interests(request.args.getlist("i")))

@bp.route("/progress/<int:cid>", methods=["POST"])
def advance(cid):
    """Add progress to a course. Awards XP and logs activity (one streak day per date)."""
    s = current_student()
    course = db.session.get(Course, cid)
    if not s or not course:
        return jsonify(error="Please complete your profile first."), 400
    step = max(1, min(100, int(request.json.get("step", 25))))
    p = Progress.query.filter_by(student_id=s.id, course_id=cid).first()
    if not p:
        p = Progress(student_id=s.id, course_id=cid, progress_percentage=0, time_spent=0)
        db.session.add(p)
        db.session.add(Interaction(student_id=s.id, course_id=cid, action="start"))
    if p.status != "completed":
        p.progress_percentage = min(100, p.progress_percentage + step)
        hrs = course.duration_hours * step / 100
        p.time_spent += hrs
        p.last_activity = datetime.utcnow()
        s.xp += step // 5 * 2
        log_activity(s, int(hrs * 60))
        if p.progress_percentage >= 100:
            p.status, p.completed_at = "completed", datetime.utcnow()
            s.xp += 100
            db.session.add(Interaction(student_id=s.id, course_id=cid, action="complete"))
    db.session.commit()
    return jsonify(pct=p.progress_percentage, xp=s.xp)

@bp.route("/path/<int:cid>", methods=["POST"])
def add_to_path(cid):
    s = current_student()
    if not s or not db.session.get(Course, cid):
        return jsonify(error="Please complete your profile first."), 400
    if not PathItem.query.filter_by(student_id=s.id, course_id=cid).first():
        pos = PathItem.query.filter_by(student_id=s.id).count()
        db.session.add(PathItem(student_id=s.id, course_id=cid, position=pos))
        db.session.commit()
    return jsonify(ok=True)

@bp.route("/feedback/<int:cid>", methods=["POST"])
def feedback(cid):
    s = current_student()
    rating = int(request.json.get("rating", 0))
    if not s or not 1 <= rating <= 5:
        return jsonify(error="Please choose a rating from 1 to 5."), 400
    db.session.add(Interaction(student_id=s.id, course_id=cid, action="rate", rating=rating,
                               comment=str(request.json.get("comment", ""))[:300]))
    db.session.commit()
    return jsonify(ok=True)

@bp.route("/progress-data")
def progress_data():
    s = current_student()
    if not s:
        return jsonify(error="Please complete your profile first."), 400
    prog = Progress.query.filter_by(student_id=s.id).all()
    path_n = PathItem.query.filter_by(student_id=s.id).count()
    done = sum(p.status == "completed" for p in prog)
    started = len(prog) - done
    week = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    mins = {a.day: a.minutes for a in DailyActivity.query.filter(
        DailyActivity.student_id == s.id, DailyActivity.day >= week[0])}
    # Skill chart: self-rated skill blended with the average progress of courses teaching it
    skill_vals = {}
    for k, v in (s.skills or {}).items():
        rel = [p.progress_percentage for p in prog if k.lower() in (p.course.skills or "").lower()]
        skill_vals[k] = round((v + sum(rel) / len(rel)) / 2) if rel else v
    return jsonify(
        doughnut=[done, started, max(path_n - done - started, 0)],
        weekly={"labels": [d.strftime("%a") for d in week], "hours": [round(mins.get(d, 0) / 60, 1) for d in week]},
        skills={"labels": list(skill_vals), "values": list(skill_vals.values())},
        overall=round(sum(p.progress_percentage for p in prog) / max(path_n, 1)),
        completed=done, in_progress=started,
        hours=round(sum(p.time_spent for p in prog), 1))
