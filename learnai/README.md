# LearnAI – AI-Based Personalized Learning Recommendation System
Learn Smarter. Learn Your Way.

## Stack
Flask · SQLAlchemy (MySQL) · pandas/NumPy/scikit-learn · Bootstrap 5 · Chart.js

## Setup
1. `pip install -r requirements.txt`
2. MySQL: `CREATE DATABASE learnai CHARACTER SET utf8mb4;`
3. `export DATABASE_URL="mysql+pymysql://USER:PASS@localhost/learnai"` (or `sqlite:///learnai.db` for a quick demo)
4. `python seed.py` (100 courses, 500 students, ~1500 interactions)
5. `python app.py` then open http://127.0.0.1:5000

## How recommendation works
1. Every course becomes a document (title, category, skills, topics, description) and is vectorised with TF-IDF (cached; refit only when the catalog changes).
2. The student's interests, skills (weaker skills weighted higher) and goal keywords are transformed with the same vectoriser; cosine similarity against all courses gives interest, skill and goal scores.
3. Rule-free fit scores are added for assessed level, preferred difficulty, learning style and weekly time.
4. Final score = weighted sum (weights in `config.py`: 25/20/20/15/10/5/5). Courses already completed are excluded.
5. The per-component breakdown powers the "Why this course?" panel.

## Not built yet
Assessment quiz, dataset upload, PDF report, admin panel, feedback-driven re-ranking, separate student/interest/skill tables.
