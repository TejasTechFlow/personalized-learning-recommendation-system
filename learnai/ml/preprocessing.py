import re

LEVELS = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
HOURS = {"1-3 hours": 2, "4-7 hours": 5, "8-12 hours": 10, "12+ hours": 14}

GOAL_KEYWORDS = {
    "Become a Data Scientist": "data science machine learning statistics python pandas visualization",
    "Become an AI Engineer": "artificial intelligence deep learning neural networks machine learning python nlp",
    "Become a Web Developer": "web html css javascript react flask frontend backend api",
    "Become a Software Developer": "software java algorithms data structures git testing",
    "Become a Data Analyst": "data analytics sql excel visualization statistics dashboards",
    "Prepare for Placement": "algorithms data structures sql java python interview",
    "Build Projects": "project hands-on capstone portfolio",
    "Learn New Skills": "fundamentals introduction basics",
    "Prepare for Certification": "cloud certification security exam fundamentals",
}

# Interest graph used for "You may also be interested in..."
RELATED = {
    "Data Science": ["Machine Learning", "Statistics", "Data Visualization", "Python"],
    "Artificial Intelligence": ["Machine Learning", "Deep Learning", "Data Science"],
    "Machine Learning": ["Deep Learning", "Statistics", "Data Science", "Python"],
    "Data Analytics": ["SQL", "Data Visualization", "Statistics"],
    "Web Development": ["Software Development", "UI/UX Design", "Cloud Computing"],
    "App Development": ["UI/UX Design", "Software Development", "IoT"],
    "Cyber Security": ["Cloud Computing", "Software Development"],
    "Cloud Computing": ["Cyber Security", "Software Development"],
    "IoT": ["App Development", "Cloud Computing", "Python"],
    "UI/UX Design": ["Web Development", "App Development"],
    "Software Development": ["Web Development", "Cloud Computing"],
    "Digital Marketing": ["Data Analytics", "UI/UX Design"],
    "Python": ["Data Science", "Machine Learning", "Statistics"],
    "SQL": ["Data Analytics", "Data Science"],
    "Statistics": ["Data Science", "Machine Learning", "Data Analytics"],
    "Data Visualization": ["Data Analytics", "Data Science"],
    "Deep Learning": ["Artificial Intelligence", "Machine Learning"],
}
INTERESTS = sorted(set(RELATED) | {i for v in RELATED.values() for i in v})
SKILLS = ["Python", "SQL", "Statistics", "Machine Learning", "Java", "JavaScript", "HTML/CSS", "Data Analysis"]
GOALS = list(GOAL_KEYWORDS)
STYLES = ["Video", "Reading", "Practical Projects", "Quizzes", "Interactive Exercises"]

def clean(text):
    return re.sub(r"[^a-z0-9+# ]", " ", str(text or "").lower())

def suggest_interests(selected, limit=4):
    """Rank unselected interests by how many selected interests point to them."""
    score = {}
    for s in selected:
        for rel in RELATED.get(s, []):
            if rel not in selected:
                score[rel] = score.get(rel, 0) + 1
    return [k for k, _ in sorted(score.items(), key=lambda kv: (-kv[1], kv[0]))][:limit]
