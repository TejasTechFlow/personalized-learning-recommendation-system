import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/learnai"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    WEIGHTS = {
        "interest": 0.25,
        "skill": 0.20,
        "goal": 0.20,
        "assessment": 0.15,
        "difficulty": 0.10,
        "style": 0.05,
        "time": 0.05
    }