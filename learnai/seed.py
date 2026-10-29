"""Seed realistic catalog + synthetic students/interactions:  python seed.py"""
import random
from urllib.parse import quote_plus
from app import create_app
from models.database import db, Course, Student, Interaction
from ml.preprocessing import INTERESTS, SKILLS, GOALS, STYLES

random.seed(7)
# (name, category, skills, topics, official docs url)
TOPICS = [
 ("Python Programming","Python","python,programming","variables,loops,functions,oop","https://docs.python.org/3/tutorial/"),
 ("NumPy and Pandas","Data Science","python,numpy,pandas,data analysis","arrays,dataframes,data cleaning","https://pandas.pydata.org/docs/"),
 ("Statistics for Data Science","Data Science","statistics,probability","distributions,hypothesis testing,regression","https://www.khanacademy.org/math/statistics-probability"),
 ("Data Visualization","Data Analytics","visualization,matplotlib,data analysis","charts,dashboards,storytelling","https://matplotlib.org/stable/tutorials/"),
 ("SQL for Data Analysis","SQL","sql,databases,data analysis","joins,aggregation,window functions","https://www.postgresql.org/docs/current/tutorial.html"),
 ("Machine Learning","Machine Learning","machine learning,scikit-learn,python,statistics","regression,classification,clustering","https://scikit-learn.org/stable/user_guide.html"),
 ("Deep Learning","AI","deep learning,neural networks,tensorflow","cnn,rnn,backpropagation","https://www.tensorflow.org/tutorials"),
 ("Natural Language Processing","AI","nlp,python,machine learning","tokenization,embeddings,transformers","https://huggingface.co/learn"),
 ("Computer Vision","AI","opencv,deep learning,python","image processing,object detection","https://docs.opencv.org/4.x/"),
 ("Excel for Data Analytics","Data Analytics","excel,data analysis","pivot tables,formulas,dashboards","https://support.microsoft.com/excel"),
 ("HTML and CSS","Web Development","html/css,web development","semantic markup,flexbox,responsive design","https://developer.mozilla.org/docs/Learn"),
 ("JavaScript","Web Development","javascript,web development","dom,async programming,es6","https://developer.mozilla.org/docs/Web/JavaScript"),
 ("React","Web Development","react,javascript","components,hooks,state management","https://react.dev/learn"),
 ("Flask Web Development","Web Development","flask,python,sql","routing,templates,sqlalchemy","https://flask.palletsprojects.com/"),
 ("Node.js and REST APIs","Web Development","node,javascript,api","express,authentication,rest","https://nodejs.org/en/learn"),
 ("Java Programming","Java","java,oop","classes,collections,exceptions","https://docs.oracle.com/javase/tutorial/"),
 ("Data Structures and Algorithms","Software Development","algorithms,data structures,java,python","trees,graphs,sorting,dynamic programming","https://www.geeksforgeeks.org/data-structures/"),
 ("Git and Software Engineering","Software Development","git,testing,software development","branching,code review,ci","https://git-scm.com/doc"),
 ("Cloud Computing with AWS","Cloud Computing","aws,cloud computing","ec2,s3,iam","https://docs.aws.amazon.com/"),
 ("Docker and Kubernetes","Cloud Computing","docker,kubernetes,devops","containers,orchestration,deployment","https://docs.docker.com/get-started/"),
 ("Cyber Security Basics","Cyber Security","security,networking","threats,encryption,authentication","https://owasp.org/www-project-top-ten/"),
 ("Ethical Hacking","Cyber Security","penetration testing,security","reconnaissance,exploitation,reporting","https://owasp.org/www-project-web-security-testing-guide/"),
 ("Android App Development","App Development","kotlin,android,mobile","activities,layouts,room database","https://developer.android.com/courses"),
 ("IoT with Arduino and Raspberry Pi","IoT","iot,arduino,sensors","gpio,mqtt,sensor data","https://docs.arduino.cc/learn/"),
 ("UI/UX Design","UI/UX Design","figma,ux,design","wireframes,prototyping,usability testing","https://www.figma.com/resource-library/"),
]
VARIANTS = [("Fundamentals","Beginner",15,3,"Video,Reading,Quizzes"),
            ("in Practice","Intermediate",24,5,"Practical Projects,Interactive Exercises"),
            ("Advanced","Advanced",32,6,"Reading,Practical Projects"),
            ("Project Bootcamp","Intermediate",40,8,"Practical Projects,Video")]

def run():
    app = create_app()
    with app.app_context():
        if Course.query.count():
            return print("Already seeded.")
        for name, cat, sk, tp, doc in TOPICS:
            for suf, lvl, dur, hpw, sty in VARIANTS:
                db.session.add(Course(
                    title=f"{name} {suf}", category=cat, skills=sk, topics=tp, difficulty=lvl,
                    duration_hours=dur, hours_per_week=hpw, learning_style=sty,
                    rating=round(random.uniform(3.9, 4.9), 1),
                    description=f"A {lvl.lower()}-level course on {name.lower()} covering {tp}. "
                                f"Learn through {sty.lower().replace(',', ' and')}.",
                    youtube_url="https://www.youtube.com/results?search_query=" + quote_plus(f"{name} {lvl} tutorial"),
                    resource_url=doc, practice_url="https://www.kaggle.com/learn"))
        db.session.commit()
        first = ["Aarav","Priya","Rohan","Sneha","Kabir","Ananya","Vikram","Isha","Arjun","Meera","Neha","Siddharth","Tanvi","Aditya","Riya"]
        last = ["Patil","Deshmukh","Sharma","Kulkarni","Joshi","Iyer","Nair","Shinde","Gupta","More"]
        ids = [c.id for c in Course.query.all()]
        for _ in range(500):
            skills = {k: random.randint(20, 95) for k in random.sample(SKILLS, random.randint(2, 5))}
            s = Student(name=f"{random.choice(first)} {random.choice(last)}", age=random.randint(17, 26),
                        education_level=random.choice(["Undergraduate", "Postgraduate", "Diploma"]),
                        interests=random.sample(INTERESTS, random.randint(2, 4)), skills=skills,
                        learning_goal=random.choice(GOALS), weekly_hours=random.choice([2, 5, 10, 14]),
                        preferred_difficulty=random.choice(["Beginner", "Intermediate", "Advanced"]),
                        learning_styles=random.sample(STYLES, 2),
                        assessment_score=sum(skills.values()) / len(skills))
            db.session.add(s); db.session.flush()
            for cid in random.sample(ids, random.randint(2, 4)):
                act = random.choice(["view", "start", "complete", "rate"])
                db.session.add(Interaction(student_id=s.id, course_id=cid, action=act,
                                           rating=random.randint(3, 5) if act == "rate" else None))
        db.session.commit()
        print("Seeded", Course.query.count(), "courses,", Student.query.count(), "students,",
              Interaction.query.count(), "interactions")

if __name__ == "__main__":
    run()
