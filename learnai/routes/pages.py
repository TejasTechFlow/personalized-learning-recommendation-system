from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import db, Student, Course, Progress, PathItem, Interaction
from ml.preprocessing import INTERESTS, SKILLS, GOALS, STYLES, HOURS, LEVELS
from ml.recommender import recommend, focus_message
from .helpers import current_student, badges

bp = Blueprint("pages", __name__)

@bp.route("/")
def home():
    stats = {"courses": Course.query.count(), "students": Student.query.count(),
             "interactions": Interaction.query.count(),
             "recommendations": Student.query.count() * 10}  # TODO: log real generations in a recommendations table
    return render_template("home.html", stats=stats)

@bp.route("/profile", methods=["GET", "POST"])
def profile():
    s = current_student()
    if request.method == "POST":
        f = request.form
        name = f.get("name", "").strip()
        try:
            age = int(f.get("age", ""))
            assert 10 <= age <= 80 and 1 <= len(name) <= 100
            assert f.get("goal") in GOALS and f.get("hours") in HOURS and f.get("difficulty") in LEVELS
        except (ValueError, AssertionError):
            flash("Please complete every field with valid values.", "danger")
            return render_template("profile.html", s=s, **_opts()), 400
        skills = {k: max(0, min(100, int(f.get("skill_" + k, 0) or 0))) for k in SKILLS}
        skills = {k: v for k, v in skills.items() if v > 0}
        s = s or Student()
        s.name, s.age, s.education_level = name, age, f.get("education", "")[:60]
        s.interests = [i for i in f.getlist("interests") if i in INTERESTS]
        s.skills, s.learning_goal = skills, f["goal"]
        s.weekly_hours, s.preferred_difficulty = HOURS[f["hours"]], f["difficulty"]
        s.learning_styles = [x for x in f.getlist("styles") if x in STYLES]
        # Until the assessment module is added, the mean self-rated skill acts as the assessment feature
        s.assessment_score = sum(skills.values()) / len(skills) if skills else 50
        db.session.add(s)
        db.session.commit()
        session["sid"] = s.id
        flash("Profile saved. Here are your recommendations.", "success")
        return redirect(url_for("pages.recommendations"))
    return render_template("profile.html", s=s, **_opts())

def _opts():
    return dict(interests=INTERESTS, skills=SKILLS, goals=GOALS, styles=STYLES, hours=list(HOURS))

@bp.route("/recommendations")
def recommendations():
    s = current_student()
    if not s:
        flash("Please complete your profile before requesting recommendations.", "warning")
        return redirect(url_for("pages.profile"))
    recs = recommend(s)
    if not recs:
        flash("No courses match your current profile.", "info")
    in_path = {p.course_id for p in PathItem.query.filter_by(student_id=s.id)}
    return render_template("recommendations.html", s=s, recs=recs, focus=focus_message(s), in_path=in_path)

@bp.route("/learning-path")
def learning_path():
    s = current_student()
    if not s:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("pages.profile"))
    items = PathItem.query.filter_by(student_id=s.id).order_by(PathItem.position).all()
    if not items:  # auto-build: easiest first, best match first inside each level
        recs = sorted(recommend(s, 7), key=lambda r: (LEVELS[r["course"].difficulty], -r["score"]))
        for i, r in enumerate(recs):
            db.session.add(PathItem(student_id=s.id, course_id=r["course"].id, position=i))
        db.session.commit()
        items = PathItem.query.filter_by(student_id=s.id).order_by(PathItem.position).all()
    prog = {p.course_id: p for p in Progress.query.filter_by(student_id=s.id)}
    levels, unlocked = [], True
    for i, it in enumerate(items, 1):
        p = prog.get(it.course_id)
        pct = p.progress_percentage if p else 0
        status = "completed" if pct >= 100 else ("locked" if not unlocked else "current" if pct else "available")
        levels.append({"n": i, "course": it.course, "pct": pct, "status": status, "xp": 100})
        unlocked = unlocked and pct >= 100
    return render_template("learning_path.html", s=s, levels=levels, badges=badges(s))

@bp.route("/progress")
def progress():
    s = current_student()
    if not s:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("pages.profile"))
    cur, longest, last = s.streaks()
    return render_template("progress.html", s=s, cur=cur, longest=longest, last=last, badges=badges(s))
