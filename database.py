from app import db  # Import the db instance from app.py

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email_id = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    

class Departments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    vision = db.Column(db.Text)
    mission = db.Column(db.Text)
    hod_name = db.Column(db.String(100))
    hod_email = db.Column(db.String(100))
    hod_photo = db.Column(db.String(200))

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    email = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

class Circulars(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    file = db.Column(db.String(200))
    date_posted = db.Column(db.Date)
    type = db.Column(db.String(100))  # General or Department-specific
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    semester = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

class StudyMaterials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    file = db.Column(db.String(200))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    semester = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)
    date_submitted = db.Column(db.Date)

class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    batch = db.Column(db.String(100))
    testimonial = db.Column(db.Text)
    current_position = db.Column(db.String(200))

class PrincipalInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    message = db.Column(db.Text)
    photo = db.Column(db.String(200))

# To create database
if __name__ == '__main__':
    from app import app  # Import app to access app context
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
