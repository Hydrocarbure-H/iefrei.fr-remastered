from typing import Dict, Any, List

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db() -> None:
    from app import app
    db.init_app(app)
    with app.app_context():
        db.create_all()


class Course(db.Model):
    """
    Course Model
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    path = db.Column(db.String(200), nullable=False, unique=True)
    html_path = db.Column(db.String(200), nullable=False, unique=True)
    pdf_path = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=True)


def get_all_courses() -> List[Dict[str, Any]]:
    """
    Get all courses from the database
    :return: Dict list of all courses
    """
    courses = Course.query.all()
    return [
        {
            "id": course.id,
            "title": course.title,
            "author": course.author,
            "path": course.path,
            "html_path": course.html_path,
            "pdf_path": course.pdf_path,
            "size": course.size,
            "date": course.date,
            "last_update": course.last_update
        }
        for course in courses
    ]


def update_course(course_data: Dict[str, Any]) -> None:
    """
    Update a course in the database
    :param course_data: the course data
    :return: None
    """
    course = Course.query.filter_by(html_path=course_data['html_path']).first()
    if course:
        course.last_update = course_data['date']
        course.size = course_data['size']
        db.session.commit()


def add_course(course_data: Dict[str, Any]) -> None:
    """
    Add a course to the database
    :param course_data: the course data
    :return: None
    """
    new_course = Course(
        title=course_data['title'],
        author=course_data['author'],
        path=course_data['path'],
        html_path=course_data['html_path'],
        pdf_path=course_data['pdf_path'],
        size=course_data['size'],
        date=course_data['date']
    )
    db.session.add(new_course)
    db.session.commit()
