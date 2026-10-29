"""Content-based recommender: TF-IDF + cosine similarity + weighted, explainable scoring."""
import numpy as np
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models.database import Course, Progress
from .preprocessing import GOAL_KEYWORDS, LEVELS, clean

_cache = {"key": None, "vec": None, "matrix": None, "courses": None}

def _course_doc(c):
    # title repeated twice so it carries more weight than the long description
    return clean(" ".join([c.title, c.title, c.category or "", c.skills or "", c.topics or "",
                           c.description or "", c.difficulty or ""]))

def get_model():
    """Fit TF-IDF once and reuse it; refit only when the course catalog changes."""
    courses = Course.query.order_by(Course.id).all()
    key = (len(courses), max((c.updated_at for c in courses), default=None))
    if _cache["key"] != key:
        vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
        _cache.update(key=key, vec=vec, courses=courses,
                      matrix=vec.fit_transform([_course_doc(c) for c in courses]) if courses else None)
    return _cache

def invalidate():
    _cache["key"] = None

def _norm(x):
    return x / x.max() if x.size and x.max() > 0 else x

def recommend(student, n=12, weights=None):
    w = weights or current_app.config["WEIGHTS"]
    m = get_model()
    courses, vec, mat = m["courses"], m["vec"], m["matrix"]
    if not courses:
        return []

    def sim(text):  # cosine similarity between a student text and every course vector
        return _norm(cosine_similarity(vec.transform([clean(text)]), mat).ravel())

    skills = student.skills or {}
    # Weaker skills are repeated more, so the engine leans toward skills the student should improve
    skill_text = " ".join((s + " ") * (1 + int((100 - v) / 34)) for s, v in skills.items())
    interest = sim(" ".join(student.interests or []))
    skill = sim(skill_text)
    goal = sim(GOAL_KEYWORDS.get(student.learning_goal, student.learning_goal or ""))

    target = 0 if student.assessment_score < 45 else 1 if student.assessment_score < 75 else 2
    pref = LEVELS.get(student.preferred_difficulty, 0)
    lv = np.array([LEVELS.get(c.difficulty, 0) for c in courses])
    assessment = 1 - np.abs(lv - target) / 2
    difficulty = 1 - np.abs(lv - pref) / 2
    styles = set(student.learning_styles or [])
    style = np.array([len(styles & set((c.learning_style or "").split(","))) / max(len(styles), 1)
                      for c in courses])
    time_fit = np.array([min(1, (student.weekly_hours or 1) / max(c.hours_per_week, 1)) for c in courses])

    comps = {"interest": interest, "skill": skill, "goal": goal, "assessment": assessment,
             "difficulty": difficulty, "style": style, "time": time_fit}
    total = sum(w[k] * comps[k] for k in w)

    done = {p.course_id for p in Progress.query.filter_by(student_id=student.id, status="completed")}
    labels = {"interest": "Matches your interests", "skill": "Builds the skills you're working on",
              "goal": "Supports your goal: %s" % student.learning_goal,
              "assessment": "Suitable for your assessed level", "difficulty": "Matches your preferred difficulty",
              "style": "Uses your preferred learning style", "time": "Fits your weekly learning hours"}
    out = []
    for i in np.argsort(-total):
        c = courses[i]
        if c.id in done:
            continue
        out.append({"course": c, "score": round(float(total[i]) * 100, 1),
                    "breakdown": {k: round(float(comps[k][i]) * 100) for k in comps},
                    "reasons": [labels[k] for k in sorted(comps, key=lambda k: -w[k] * comps[k][i])
                                if comps[k][i] >= .6][:5]})
        if len(out) == n:
            break
    return out

def focus_message(student):
    weak = sorted((v, s) for s, v in (student.skills or {}).items() if 0 < v < 60)
    if weak:
        return "Based on your recent performance, we recommend focusing on %s." % weak[0][1]
