from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gpd_site.db'
db = SQLAlchemy(app)

# Database connection function
import os

# Database connection function
def get_db_connection():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    return conn


from datetime import datetime, timedelta



@app.route('/')
def home():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Get alumni
    c.execute('SELECT * FROM alumni WHERE status = "Approved" ORDER BY id DESC')
    alumni = c.fetchall()

    # Academic Year Calculation
    current_month = datetime.now().month
    current_year = datetime.now().year

    if current_month >= 6:
        start_year = current_year
        end_year = current_year + 1
    else:
        start_year = current_year - 1
        end_year = current_year

    default_academic_year = f"{start_year}-{str(end_year)[-2:]}"
    selected_year = request.args.get('academic_year', default_academic_year)

    # Determine date range for selected academic year
    start_date = f"{selected_year.split('-')[0]}-06-01"
    end_date = f"20{selected_year.split('-')[1]}-05-31"

    # Fetch circulars within the selected academic year
    c.execute('''
        SELECT id, title, file, posted_on 
        FROM circulars 
        WHERE date(posted_on) BETWEEN date(?) AND date(?) 
        ORDER BY datetime(posted_on) DESC 
        LIMIT 5
    ''', (start_date, end_date))
    circulars = c.fetchall()

    

    # Format and flag new circulars
    formatted_circulars = []
    for circ in circulars:
        try:
            posted_on_dt = datetime.strptime(circ[3], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            posted_on_dt = datetime.now()

        is_new = (datetime.now() - posted_on_dt) <= timedelta(days=7)

        formatted_circulars.append({
            'id': circ[0],
            'title': circ[1],
            'file': circ[2],
            'posted_on': posted_on_dt.strftime("%d-%m-%Y"),
            'is_new': is_new
        })

    # Academic year dropdown options (you can generate more dynamically if needed)
    academic_years = [f"{y}-{str(y+1)[-2:]}" for y in range(2022, current_year + 2)]
    c.execute("SELECT academic_year, file FROM eoa_letters ORDER BY academic_year DESC")
    eoa_letters = c.fetchall()
    gtu_rows = conn.execute('SELECT year, file FROM gtu_affiliation_letters ORDER BY year DESC').fetchall()
    gtu_letters = [(row[0], row[1]) for row in gtu_rows]

    c.execute("SELECT id, title, file, uploaded_on FROM newsletters ORDER BY uploaded_on DESC LIMIT 5")
    newsletters_raw = c.fetchall()
    conn.close()

    newsletters = []
    for row in newsletters_raw:
        try:
            uploaded_on = datetime.strptime(row['uploaded_on'], "%Y-%m-%d %H:%M:%S")
        except:
            uploaded_on = datetime.now()  # fallback
        is_new = (datetime.now() - uploaded_on) < timedelta(days=3)
        newsletters.append({
           'id': row['id'],
           'title': row['title'],
           'file': row['file'],
           'uploaded_on': row['uploaded_on'],
           'is_new': is_new
        })


    return render_template(
        'home.html',
        alumni=alumni,
        circulars=formatted_circulars,
        academic_years=academic_years,
        selected_year=selected_year,
        eoa_letters=eoa_letters,
        gtu_letters=gtu_letters,
        newsletters=newsletters
    )

@app.route('/hostel')
def hostel():
    from datetime import datetime
    return render_template("hostel.html", current_year=datetime.now().year)

@app.route('/library')
def library():
    return render_template('library.html')

@app.route('/transport')
def transport():
    return render_template('transport.html')


@app.route('/committee/internal-complaint')
def internal_complaint_committee():
    committee_members = [
        {'name': 'Smt. U.B.Trivedi', 'role': 'Convener'},
        {'name': 'Shri S.Y.Ragadiya', 'role': 'Member'},
        {'name': 'Shri A.M.Maheshwari ', 'role': 'Member'},
        {'name': 'Smt. F.K.Lanewala ', 'role': 'Member'},
        {'name': 'Smt. P.D.Patel', 'role': 'Member'},
        {'name': 'Shri D.A.Bhatia', 'role': 'Member'},
        {'name': 'Shri D.R.Bhuriya', 'role': 'Member'}
    ]
    return render_template('internal_complaint_committee.html', committee_members=committee_members)

@app.route('/committee/grievance_redressal_committee')
def grievance_redressal_committee():
    committee_members = [
        {'name': 'Smt. U.B.Trivedi', 'role': 'Convener'},
        {'name': 'Shri S.Y.Ragadiya', 'role': 'Member'},
        {'name': 'Shri A.M.Maheshwari ', 'role': 'Member'},
        {'name': 'Smt. F.K.Lanewala ', 'role': 'Member'},
        {'name': 'Smt. P.D.Patel', 'role': 'Member'},
        {'name': 'Shri D.A.Bhatia', 'role': 'Member'},
        {'name': 'Shri D.R.Bhuriya', 'role': 'Member'}
    ]
    return render_template('Grievance_Redressal_Committee.html', committee_members=committee_members)

@app.route('/committee/student_feedback_committee')
def student_feedback_committee():
    committee_members = [
        {'name': 'Mr. M.T.Rathwa', 'role': 'Coordinator'},
        {'name': 'Mr. D.P.Patel', 'role': 'CO-Coordinator'},
        {'name': 'Mr. V.R.Ninama', 'role': 'Member'},
        {'name': 'Mr. D.J.Kandpal', 'role': 'Member'},
        {'name': 'Mr. M.A.Josh', 'role': 'Member'},
        {'name': 'Mr. S.S.Charel', 'role': 'Member'},
        {'name': 'Mr.P.R.Bhansar', 'role': 'Member'}
    ]
    return render_template('Student_Feedback_committee.html', committee_members=committee_members)


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        admin = conn.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['name']
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials. Please try again.', 'danger')
    return render_template('login.html')

# Admin Dashboard Route (after login)
@app.route('/dashboard')
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ===================== Manage Circulars ====================

@app.route('/manage-circulars', methods=['GET'])
def manage_circulars():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get filters from query params
    filter_type = request.args.get('type')
    filter_date = request.args.get('date')

    query = "SELECT * FROM circulars WHERE 1=1"
    params = []

    if filter_type:
        query += " AND type = ?"
        params.append(filter_type)
    if filter_date:
        query += " AND DATE(posted_on) = ?"
        params.append(filter_date)

    query += " ORDER BY posted_on DESC"
    cursor.execute(query, tuple(params))
    circulars = cursor.fetchall()

    conn.close()

    return render_template("manage_circulars.html", circulars=circulars, filter_type=filter_type, filter_date=filter_date)


@app.route('/add-circular', methods=['GET', 'POST'])
def add_circular():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM departments")
    departments = cursor.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        type_ = request.form['type']
        department = request.form.get('department') if type_ == 'department' else None
        file = request.files['file']

        file_name = None
        if file and file.filename != '':
            file_name = secure_filename(file.filename)
            file.save(os.path.join('static/uploads/Circulars', file_name))

        cursor.execute('''
            INSERT INTO circulars (title, description, file, type, department)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, file_name, type_, department))  # <--- fixed here
        conn.commit()
        conn.close()

        flash('Circular added successfully!', 'success')
        return redirect(url_for('manage_circulars'))

    conn.close()
    return render_template('add_circular.html', departments=departments)



@app.route('/delete-circular/<int:circular_id>')
def delete_circular(circular_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT file FROM circulars WHERE id = ?', (circular_id,))
    file = cursor.fetchone()
    if file and file[0]:
        file_path = os.path.join('static/uploads/Circulars', file[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    cursor.execute('DELETE FROM circulars WHERE id = ?', (circular_id,))
    conn.commit()
    conn.close()
    flash('Circular deleted successfully!', 'success')
    return redirect(url_for('manage_circulars'))

# ===================== Manage Faculty ====================

@app.route('/manage-faculty')
def manage_faculty():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    department_filter = request.args.get('department')

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if department_filter:
        cursor.execute("SELECT * FROM faculty WHERE department_name = ? ORDER BY name ASC", (department_filter,))
    else:
        cursor.execute("SELECT * FROM faculty ORDER BY name ASC")
    faculty = cursor.fetchall()

    cursor.execute("SELECT name FROM departments ORDER BY name ASC")
    departments = cursor.fetchall()

    conn.close()

    return render_template('manage_faculty.html', faculty=faculty, departments=departments)



@app.route('/add-faculty', methods=['GET', 'POST'])
def add_faculty():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'designation': request.form['designation'],
            'qualification': request.form['qualification'],
            'email': request.form['email'],
            'mobile': request.form.get('mobile'),
            'department': request.form['department'],
            'expertise': request.form.get('expertise'),
            'subjects': request.form.get('subjects'),
            'experience': request.form.get('experience'),
            'research': request.form.get('research'),
            'publications': request.form.get('publications'),
            'awards': request.form.get('awards'),
            'workshops': request.form.get('workshops'),
            'certifications': request.form.get('certifications'),
            'roles': request.form.get('roles'),
        }

        photo = request.files['photo']
        photo_filename = None
        if photo and photo.filename != '':
            photo_filename = photo.filename
            photo.save(os.path.join('static/uploads', photo_filename))

        conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO faculty (name, designation, qualification, email, mobile_number, department_name,
                                 expertise, subjects_taught, experience, research_interests, publications, awards,
                                 workshops, certifications, additional_roles, photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['designation'], data['qualification'], data['email'], data['mobile'],
              data['department'], data['expertise'], data['subjects'], data['experience'], data['research'],
              data['publications'], data['awards'], data['workshops'], data['certifications'], data['roles'], photo_filename))
        conn.commit()
        conn.close()

        flash('Faculty added successfully!', 'success')
        return redirect(url_for('manage_faculty'))

    return render_template('add_faculty.html')


@app.route('/delete-faculty/<int:faculty_id>')
def delete_faculty(faculty_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT photo FROM faculty WHERE id = ?', (faculty_id,))
    photo = cursor.fetchone()
    if photo and photo[0]:
        photo_path = os.path.join('static/uploads', photo[0])
        if os.path.exists(photo_path):
            os.remove(photo_path)

    cursor.execute('DELETE FROM faculty WHERE id = ?', (faculty_id,))
    conn.commit()
    conn.close()
    flash('Faculty deleted successfully!', 'success')
    return redirect(url_for('manage_faculty'))

# ===================== Manage Subjects ====================

@app.route('/manage-subjects')
def manage_subjects():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    department = request.args.get('department')
    semester = request.args.get('semester')

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Filtering logic
    if department and semester:
        cursor.execute("SELECT * FROM subjects WHERE department_name = ? AND semester = ? ORDER BY name",
                       (department, semester))
    elif department:
        cursor.execute("SELECT * FROM subjects WHERE department_name = ? ORDER BY name", (department,))
    elif semester:
        cursor.execute("SELECT * FROM subjects WHERE semester = ? ORDER BY name", (semester,))
    else:
        cursor.execute("SELECT * FROM subjects ORDER BY department_name, semester")

    subjects = cursor.fetchall()
    cursor.execute("SELECT DISTINCT name FROM departments ORDER BY name")
    departments = cursor.fetchall()
    conn.close()

    return render_template('manage_subjects.html', subjects=subjects, departments=departments)


@app.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT name FROM departments")
    departments = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        subject_name = request.form['subject_name']
        department_name = request.form['department_name']
        semester = request.form['semester']

        conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO subjects (name, department_name, semester)
            VALUES (?, ?, ?)
        ''', (subject_name, department_name, semester))
        conn.commit()
        conn.close()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('manage_subjects'))

    return render_template('add_subject.html', departments=departments)

@app.route('/delete-subject/<int:subject_id>')
def delete_subject(subject_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
    conn.commit()
    conn.close()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('manage_subjects'))

# ===================== Manage Materials ====================

@app.route('/manage-materials')
def manage_materials():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials ORDER BY department_name, semester")
    materials = cursor.fetchall()
    conn.close()
    return render_template('manage_materials.html', materials=materials)

@app.route('/add-material', methods=['GET', 'POST'])
def add_material():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        department = request.form['department']
        semester = request.form['semester']
        file = request.files['file']

        file_filename = None
        if file and file.filename != '':
            file_filename = file.filename
            file.save(os.path.join('static/materials', file_filename))

        conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO materials (title, description, department_name, semester, file)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, department, semester, file_filename))
        conn.commit()
        conn.close()
        flash('Material added successfully!', 'success')
        return redirect(url_for('manage_materials'))

    return render_template('add_material.html')

@app.route('/delete-material/<int:material_id>')
def delete_material(material_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT file FROM materials WHERE id = ?', (material_id,))
    file = cursor.fetchone()
    if file and file[0]:
        file_path = os.path.join('static/materials', file[0])
        if os.path.exists(file_path):
            os.remove(file_path)

    cursor.execute(' = ?', (material_id,))
    conn.commit()
    conn.close()
    flash('Material deleted successfully!', 'success')
    return redirect(url_for('manage_materials'))

# ===================== Student Corner ====================

@app.route('/student-corner')
def student_corner():
    return render_template('student_corner.html')

@app.route('/view-materials')
def view_materials():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials ORDER BY department_name, semester")
    materials = cursor.fetchall()
    conn.close()
    return render_template('view_materials.html', materials=materials)

@app.route('/view-faculty')
def view_faculty():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM faculty ORDER BY department_name")
    faculty = cursor.fetchall()
    conn.close()
    return render_template('view_faculty.html', faculty=faculty)

@app.route('/academic-calendar')
def academic_calendar():
    con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = con.cursor()
    cur.execute("SELECT * FROM AcademicCalendar")
    calendars = [
        {'id': row[0], 'title': row[1], 'term': row[2], 'session': row[3], 'filename': row[4]}
        for row in cur.fetchall()
    ]
    con.close()
    return render_template('academic_calendar.html', calendars=calendars)

import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/Academic_Calenders/'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/admin/calendar', methods=['GET', 'POST'])
def upload_calendar():
    if request.method == 'POST':
        title = request.form['title']
        semester = request.form['term']
        session = request.form['session']
        file = request.files['file']
        if file and file.filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
            cur = con.cursor()
            cur.execute("INSERT INTO AcademicCalendar (title, term, session, filename) VALUES (?, ?, ?, ?)", 
                        (title, semester, session, filename))
            con.commit()
            con.close()
    con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = con.cursor()
    cur.execute("SELECT * FROM AcademicCalendar")
    calendars = [{'id': row[0], 'title': row[1], 'term': row[2], 'session': row[3], 'filename': row[4]} for row in cur.fetchall()]
    con.close()
    return render_template('admin_manage_calendar.html', calendars=calendars)

@app.route('/admin/calendar/delete/<int:id>')
def delete_calendar(id):
    con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = con.cursor()
    cur.execute("SELECT filename FROM AcademicCalendar WHERE id=?", (id,))
    file = cur.fetchone()
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        cur.execute("DELETE FROM AcademicCalendar WHERE id=?", (id,))
        con.commit()
    con.close()
    return redirect(url_for('upload_calendar'))

from flask import render_template, request
import sqlite3, os

@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    timetables = []
    no_result = False
    filters_applied = False

    con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = con.cursor()

    if request.method == 'POST':
        academic_year = request.form.get('academic_year')
        department = request.form.get('department')
        semester = request.form.get('semester')

        filters_applied = any([academic_year, department, semester])

        query = "SELECT * FROM TimeTables WHERE 1=1"
        params = []

        if academic_year:
            query += " AND academic_year=?"
            params.append(academic_year)
        if department:
            query += " AND department=?"
            params.append(department)
        if semester:
            query += " AND semester=?"
            params.append(semester)

        query += " ORDER BY id DESC"  # Assuming newer ones have higher IDs
        cur.execute(query, params)
        rows = cur.fetchall()
    else:
        cur.execute("SELECT * FROM TimeTables ORDER BY id DESC")
        rows = cur.fetchall()

    con.close()

    for row in rows:
        timetables.append({
            'id': row[0],
            'title': row[1],
            'department': row[2],
            'semester': row[3],
            'academic_year': row[4],
            'filename': row[5]
        })

    if filters_applied and not timetables:
        no_result = True

    return render_template('timetable.html',
                           timetables=timetables,
                           filters_applied=filters_applied,
                           no_result=no_result)



@app.route('/admin/timetable', methods=['GET', 'POST'])
def upload_timetable():
    if request.method == 'POST':
        title = request.form['title']
        department = request.form['department']
        semester = request.form['semester']
        academic_year = request.form['academic_year']
        file = request.files['file']

        if file and file.filename.split('.')[-1].lower() == 'pdf':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
            cur = con.cursor()
            cur.execute("INSERT INTO TimeTables (title, department, semester, academic_year, filename) VALUES (?, ?, ?, ?, ?)",
                        (title, department, semester, academic_year, filename))
            con.commit()
            con.close()

    con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = con.cursor()
    cur.execute("SELECT * FROM TimeTables")
    timetables = [
        {'id': row[0], 'title': row[1], 'department': row[2], 'semester': row[3], 'academic_year': row[4], 'filename': row[5]}
        for row in cur.fetchall()
    ]
    con.close()

    return render_template('admin_manage_timetable.html', timetables=timetables)

@app.route('/admin/timetable/delete/<int:id>')
def delete_timetable(id):
    con = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = con.cursor()
    cur.execute("SELECT filename FROM TimeTables WHERE id=?", (id,))
    file = cur.fetchone()
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        cur.execute("DELETE FROM TimeTables WHERE id=?", (id,))
        con.commit()
    con.close()
    return redirect(url_for('upload_timetable'))


UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Alumni Registration Page
@app.route('/alumni/register', methods=['GET', 'POST'])
def alumni_register():
    if request.method == 'POST':
        name = request.form['name']
        passing_year = request.form['passing_year']
        current_position = request.form['current_position']
        company = request.form['company']
        testimonial = request.form['testimonial']
        
        # Photo upload
        photo = request.files['photo']
        photo_filename = ''
        if photo:
            photo_filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
        c = conn.cursor()
        c.execute('''
                  INSERT INTO alumni (name, passing_year, current_position, company, testimonial, photo, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (name, passing_year, current_position, company, testimonial, photo_filename, 'Pending'))
        conn.commit()
        conn.close()
        flash('Registration Successful!', 'success')
        return render_template('alumni_success.html')
    return render_template('alumni_register.html')

# Alumni List Page
@app.route('/alumni')
def alumni_list():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT * FROM alumni WHERE status="Approved"')
    alumni_data = c.fetchall()
    conn.close()
    return render_template('alumni_list.html', alumni=alumni_data)

@app.route('/admin/alumni')
def admin_alumni():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT * FROM alumni')
    alumni_data = c.fetchall()
    conn.close()
    return render_template('admin_alumni.html', alumni=alumni_data)

# Approve Alumni
@app.route('/admin/alumni/approve/<int:id>')
def approve_alumni(id):
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('UPDATE alumni SET status="Approved" WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Alumni Approved Successfully!', 'success')
    return redirect(url_for('admin_alumni'))

# Reject Alumni
@app.route('/admin/alumni/reject/<int:id>')
def reject_alumni(id):
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('DELETE FROM alumni WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Alumni Rejected and Deleted!', 'danger')
    return redirect(url_for('admin_alumni'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form['email']
    
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        flash('Thank you for subscribing!', 'success')
    except sqlite3.IntegrityError:
        flash('You are already subscribed!', 'info')
    
    conn.close()
    return redirect(url_for('home'))

@app.route('/admin/subscribers')
def admin_subscribers():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT * FROM subscribers')
    subscribers = c.fetchall()
    conn.close()
    return render_template('admin_subscribers.html', subscribers=subscribers)

@app.route('/admin/subscribers/delete/<int:id>')
def delete_subscriber(id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('DELETE FROM subscribers WHERE id=?', (id,))
    conn.commit()
    conn.close()
    flash('Subscriber deleted successfully!', 'success')
    return redirect(url_for('admin_subscribers'))

# Send Newsletter Page
@app.route('/admin/send-newsletter')
def send_newsletter_page():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    return render_template('admin_send_newsletter.html')

import smtplib
from email.mime.text import MIMEText

# Send Newsletter Logic
@app.route('/admin/send-newsletter', methods=['POST'])
def send_newsletter():
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    subject = request.form['subject']
    message = request.form['message']

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT email FROM subscribers')
    subscribers = c.fetchall()
    conn.close()

    sender_email = 'your_email@gmail.com'   # <-- Use your email
    sender_password = 'your_password'       # <-- Use your app password

    for subscriber in subscribers:
        try:
            receiver_email = subscriber[0]
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = receiver_email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        except Exception as e:
            print(f"Failed to send email to {receiver_email}: {e}")

    flash('Newsletter sent successfully to all subscribers!', 'success')
    return redirect(url_for('admin_dashboard'))

from datetime import datetime, timedelta

@app.route('/upload_newsletter', methods=['GET', 'POST'])
def upload_newsletter():
    db_path = os.path.join(app.instance_path, 'gpd_site.db')
    upload_folder = os.path.join(app.static_folder, 'uploads/Newsletters')

    if request.method == 'POST':
        title = request.form['title']
        file = request.files['file']
        filename = secure_filename(file.filename)

        # Ensure the folder exists
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        # Save to DB
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO newsletters (title, file, uploaded_on) VALUES (?, ?, ?)",
                       (title, filename, datetime.now()))
        conn.commit()
        conn.close()

        flash('Newsletter uploaded successfully!', 'success')
        return redirect(url_for('upload_newsletter'))

    # For GET request - fetch all newsletters
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, file, uploaded_on FROM newsletters ORDER BY uploaded_on DESC")
    rows = cursor.fetchall()
    newsletters = [dict(row) for row in rows]
    conn.close()

    return render_template('upload_newsletter.html', newsletters=newsletters)



@app.route('/delete_newsletter/<int:newsletter_id>', methods=['POST'])
def delete_newsletter(newsletter_id):
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT file FROM newsletters WHERE id = ?", (newsletter_id,))
    result = cursor.fetchone()

    if result:
        file_path = os.path.join(app.static_folder, 'uploads/newsletters', result[0])
        if os.path.exists(file_path):
            os.remove(file_path)

        cursor.execute("DELETE FROM newsletters WHERE id = ?", (newsletter_id,))
        conn.commit()
        flash('Newsletter deleted successfully!', 'success')
    else:
        flash('Newsletter not found.', 'danger')

    conn.close()
    return redirect(url_for('upload_newsletter'))




from datetime import datetime, timedelta

@app.route('/circulars')
def view_circulars():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT id, title, description, department, type, file, posted_on FROM circulars ORDER BY posted_on DESC')
    circulars = c.fetchall()
    conn.close()

    # Prepare a list with "new" flag
    formatted_circulars = []
    for circ in circulars:
        posted_on = datetime.strptime(circ[6], "%Y-%m-%d %H:%M:%S")
        is_new = (datetime.now() - posted_on) <= timedelta(days=7)
        formatted_circulars.append({
            'id': circ[0],
            'title': circ[1],
            'description': circ[2],
            'department': circ[3],
            'type': circ[4],
            'file': circ[5],
            'posted_on': posted_on.strftime("%d-%m-%Y"),
            'is_new': is_new
        })
    
    return render_template('circulars.html', circulars=formatted_circulars)

from werkzeug.utils import secure_filename

@app.route('/admin/achievements', methods=['GET', 'POST'])
def admin_achievements():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_name = request.form['event_name']
        student_names = request.form['student_names']
        department = request.form['department']
        date = request.form['date']
        photo = None

        if 'photo' in request.files:
            file = request.files['photo']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/uploads', filename))
                photo = filename

        c.execute('INSERT INTO achievements (title, description, event_name, student_names, department, date, photo) VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (title, description, event_name, student_names, department, date, photo))
        conn.commit()

    c.execute('SELECT * FROM achievements ORDER BY posted_on DESC')
    achievements = c.fetchall()
    conn.close()

    return render_template('admin_achievements.html', achievements=achievements)

@app.route('/achievements')
def achievements():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT id, title, description, event_name, student_names, department, date, photo FROM achievements ORDER BY posted_on DESC')
    achievements = c.fetchall()
    conn.close()

    return render_template('achievements.html', achievements=achievements)

@app.route('/department/<dept_name>')
def department_page(dept_name):
    # Fetch department details from database
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()

    # Fetch Department Info (Vision, Mission, HOD)
    c.execute('SELECT vision, mission, hod_name, hod_email, hod_photo FROM Departments WHERE name = ?', (dept_name,))
    dept_info = c.fetchone()

    if dept_info is None:
        conn.close()
        flash('Department not found.', 'danger')
        return redirect(url_for('home'))

    c.execute("SELECT * FROM faculty_table WHERE department = ?", (dept_name,))
    faculty_table = c.fetchall()


    # Fetch Department Circulars
    c.execute('SELECT id, title, description, file, posted_on FROM Circulars WHERE department = ?', (dept_name,))
    circulars = c.fetchall()

    # Fetch Subjects List
    c.execute('SELECT semester, name FROM Subjects WHERE department_name = ?', (dept_name,))
    subjects = c.fetchall()

    # Fetch Study Materials
    c.execute('SELECT semester, title, file FROM Materials WHERE department_name = ?', (dept_name,))
    materials = c.fetchall()

    # Fetch Lab Gallery Images
    c.execute('SELECT title, image_path FROM LabGallery WHERE department_name = ?', (dept_name,))
    labs = c.fetchall()

    conn.close()


    return render_template('department_page.html', 
                           dept_info=dept_info, 
                           faculty_list=faculty_table, 
                           circulars=circulars,
                           subjects=subjects,
                           materials=materials,
                           labs=labs,
                           dept_name=dept_name)

@app.route('/faculty/<int:faculty_id>')
def faculty_profile(faculty_id):
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()

    # Fetch faculty details
    c.execute('''
        SELECT name, designation, department_name, qualification, email, mobile_number, photo,
               expertise, subjects_taught, experience, research_interests,
               publications, awards, workshops, certifications, additional_roles
        FROM faculty
        WHERE id = ?
    ''', (faculty_id,))
    faculty = c.fetchone()
    conn.close()

    if faculty is None:
        flash("Faculty profile not found.", "danger")
        return redirect(url_for('home'))

    # Map to dictionary for easier use in Jinja
    faculty_data = {
        "name": faculty[0],
        "designation": faculty[1],
        "department": faculty[2],
        "qualification": faculty[3],
        "email": faculty[4],
        "mobile": faculty[5],
        "photo": faculty[6],
        "expertise": faculty[7],
        "subjects": faculty[8],
        "experience": faculty[9],
        "research": faculty[10],
        "publications": faculty[11].split('|') if faculty[11] else [],
        "awards": faculty[12],
        "workshops": faculty[13].split('|') if faculty[13] else [],
        "certifications": faculty[14].split('|') if faculty[14] else [],
        "roles": faculty[15]
    }

    return render_template('faculty_profile.html', faculty=faculty_data)


@app.route('/admin/lab_gallery', methods=['GET', 'POST'])
def admin_lab_gallery():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()

    if request.method == 'POST':
        department_name = request.form['department_name']
        title = request.form['title']
        image = request.files.get('image')  # Safely get the file

        if image and image.filename != '':
            # Ensure folder exists before saving
            upload_folder = os.path.join('static', 'images', 'labs')
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(image.filename)
            save_path = os.path.join(upload_folder, filename)
            image.save(save_path)

            image_path = filename  # Save only filename in DB

            c.execute('INSERT INTO LabGallery (department_name, title, image_path) VALUES (?, ?, ?)',
                      (department_name, title, image_path))
            conn.commit()
            flash('Image uploaded successfully!', 'success')
        else:
            flash('Please select an image to upload.', 'danger')

        return redirect(url_for('admin_lab_gallery'))

    # Fetch all images
    c.execute('SELECT id, department_name, title, image_path FROM LabGallery')
    images = c.fetchall()
    conn.close()

    return render_template('admin_lab_gallery.html', images=images)



@app.route('/admin/delete_lab_image/<int:id>', methods=['POST'])
def delete_lab_image(id):
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    c = conn.cursor()
    c.execute('SELECT image_path FROM LabGallery WHERE id = ?', (id,))
    img = c.fetchone()
    
    if img:
        file_path = os.path.join('static', 'images','labs', img[0])
        if os.path.exists(file_path):
            os.remove(file_path)
    
    c.execute('DELETE FROM LabGallery WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('admin_lab_gallery'))


@app.route('/manage-committees')
def manage_committees():
    conn = get_db_connection()
    committees = conn.execute("SELECT * FROM committees").fetchall()
    conn.close()
    return render_template('admin/manage_committees.html', committees=committees)

@app.route('/add-committee', methods=['GET', 'POST'])
def add_committee():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        department = request.form['department']
        type_ = request.form['type']

        conn = get_db_connection()
        conn.execute("INSERT INTO committees (name, description, department, type) VALUES (?, ?, ?, ?)",
                     (name, description, department, type_))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_committees'))
    return render_template('admin/add_committee.html')

@app.route('/edit-committee/<int:id>', methods=['GET', 'POST'])
def edit_committee(id):
    conn = get_db_connection()
    committee = conn.execute("SELECT * FROM committees WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        department = request.form['department']
        type_ = request.form['type']

        conn.execute("UPDATE committees SET name=?, description=?, department=?, type=? WHERE id=?",
                     (name, description, department, type_, id))
        conn.commit()
        conn.close()
        return redirect(url_for('manage_committees'))

    return render_template('admin/edit_committee.html', committee=committee)

@app.route('/delete-committee/<int:id>', methods=['POST'])
def delete_committee(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM committees WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_committees'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
import os
import sqlite3
from werkzeug.utils import secure_filename

admin_eoa = Blueprint('admin_eoa', __name__)
UPLOAD_FOLDER = 'static/uploads/eoa_letters'

@app.route('/eoa')
def eoa_dashboard():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM eoa_letters ORDER BY uploaded_on DESC")
    letters = cur.fetchall()
    conn.close()
    return render_template('eoa_dashboard.html', letters=letters)

@app.route('/upload_eoa', methods=['POST'])
def upload_eoa():
    academic_year = request.form['academic_year']
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
        cur = conn.cursor()
        cur.execute("INSERT INTO eoa_letters (academic_year, file) VALUES (?, ?)", (academic_year, filename))
        conn.commit()
        conn.close()
        flash("EOA Letter uploaded successfully!", "success")
    return redirect(url_for('eoa_dashboard'))

@app.route('/eoa/delete/<int:id>')
def delete_eoa(id):
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cur = conn.cursor()
    cur.execute("SELECT file FROM eoa_letters WHERE id=?", (id,))
    file = cur.fetchone()
    if file:
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, file['file']))
        except:
            pass
        cur.execute("DELETE FROM eoa_letters WHERE id=?", (id,))
        conn.commit()
    conn.close()
    flash("EOA Letter deleted!", "success")
    return redirect(url_for('eoa_dashboard'))



app.config['UPLOAD_FOLDER'] = 'static/uploads/gtu_affiliation_letters'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin/manage_gtu_letters', methods=['GET', 'POST'])
def manage_gtu_letters():
    conn = get_db_connection()

    # Upload logic
    if request.method == 'POST':
        year = request.form['year']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            conn.execute("INSERT INTO gtu_affiliation_letters (year, file) VALUES (?, ?)", (year, filename))
            conn.commit()
            flash("Letter uploaded successfully", "success")
        else:
            flash("Only PDF files are allowed", "danger")

    # Fetch all letters
    gtu_letters = conn.execute("SELECT * FROM gtu_affiliation_letters ORDER BY year DESC").fetchall()
    conn.close()

    return render_template("manage_gtu_letters.html", gtu_letters=gtu_letters)

@app.route('/admin/delete_gtu_letter/<int:id>')
def delete_gtu_letter(id):
    conn = get_db_connection()
    letter = conn.execute("SELECT * FROM gtu_affiliation_letters WHERE id = ?", (id,)).fetchone()

    if letter:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], letter['file'])
        if os.path.exists(file_path):
            os.remove(file_path)
        conn.execute("DELETE FROM gtu_affiliation_letters WHERE id = ?", (id,))
        conn.commit()
        flash("Letter deleted successfully", "success")
    else:
        flash("Letter not found", "danger")
    
    conn.close()
    return redirect(url_for('manage_gtu_letters'))


# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))  # Use your actual DB filename
    conn.row_factory = sqlite3.Row
    return conn

# Department Login Route
@app.route('/department_login', methods=['GET', 'POST'])
def department_login():
    if request.method == 'POST':
        department_id = request.form['department_id']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        department = conn.execute(
            'SELECT * FROM departments WHERE id = ? AND hod_email = ? AND password = ?',
            (department_id, email, password)
        ).fetchone()
        conn.close()

        if department:
            # Store department session data
            session['department_id'] = department['id']
            session['department_name'] = department['name']
            flash('Login successful!', 'success')
            return redirect(url_for('department_dashboard'))
        else:
            flash('Invalid login credentials. Please try again.', 'danger')

    return render_template('department_login.html')

@app.route('/department/dashboard')
def department_dashboard():
    if 'department_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('department_login'))

    # You can query additional info here if needed
    return render_template('department_dashboard.html', department_name=session['department_name'])

# Dashboard route after login
# app.py (partial)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    return conn

# --- Route: Edit HoD Info ---
@app.route('/edit_hod', methods=['GET', 'POST'])
def edit_hod():
    dept_id = session.get('department_id')
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()

    if request.method == 'POST':
        hod_name = request.form['hod_name']
        hod_email = request.form['hod_email']
        vision = request.form['vision']
        mission = request.form['mission']

        if 'hod_photo' in request.files:
            photo = request.files['hod_photo']
            photo_path = os.path.join('static/uploads', photo.filename)
            photo.save(photo_path)
            cursor.execute("""UPDATE departments SET hod_name=?, hod_email=?, vision=?, mission=?, hod_photo=?
                              WHERE id=?""",
                           (hod_name, hod_email, vision, mission, photo_path, dept_id))
        else:
            cursor.execute("""UPDATE departments SET hod_name=?, hod_email=?, vision=?, mission=?
                              WHERE id=?""",
                           (hod_name, hod_email, vision, mission, dept_id))

        conn.commit()
        flash('HoD info updated successfully!')
        return redirect(url_for('edit_hod'))

    cursor.execute("SELECT * FROM departments WHERE id=?", (dept_id,))
    hod = cursor.fetchone()
    conn.close()

    return render_template("edit_hod.html", hod=hod)

# --- Route: Upload Circular ---
from flask import render_template, request, redirect, url_for, session, flash
import sqlite3, os
from werkzeug.utils import secure_filename

@app.route('/upload_circular', methods=['GET', 'POST'])
def upload_department_circular():
    department_id = session.get('department_id')
    if not department_id:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('department_login'))

    # Get department name to display in form
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM departments WHERE id = ?", (department_id,))
    row = cursor.fetchone()
    department_name = row['name'] if row else 'Unknown'

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        circular_type = request.form['type']

        # File handling
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join('static/circulars', filename)
            file.save(file_path)
        else:
            file_path = ''

        # Insert into DB
        cursor.execute("""INSERT INTO circulars (title, description, department, type, file) 
                          VALUES (?, ?, ?, ?, ?)""",
                       (title, description, department_id, circular_type, file_path))
        conn.commit()
        conn.close()

        flash('Circular uploaded successfully!', 'success')
        return redirect(url_for('upload_department_circular'))

    # Render form
    return render_template("department_circular.html", department_name=department_name)

@app.route('/department/lab-gallery', methods=['GET', 'POST'])
def lab_gallery():
    if 'department_id' not in session:
        return redirect(url_for('department_login'))

    department_id = session['department_id']
    
    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get department name
    cursor.execute("SELECT name FROM departments WHERE id = ?", (department_id,))
    department_name = cursor.fetchone()['name']

    if request.method == 'POST':
        title = request.form['title']
        image = request.files['image']

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image_path = f"lab_photos/{filename}"
            full_path = os.path.join('static', image_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            image.save(full_path)

            cursor.execute(
                "INSERT INTO LabGallery (department_name, title, image_path) VALUES (?, ?, ?)",
                (department_name, title, image_path)
            )
            conn.commit()
            flash("Photo uploaded successfully!", "success")
            return redirect(url_for('lab_gallery'))

    # Fetch photos of this department
    cursor.execute("SELECT * FROM LabGallery WHERE department_name = ?", (department_name,))
    photos = cursor.fetchall()
    conn.close()

    return render_template('lab_gallery.html', photos=photos)

@app.route('/department/delete-photo/<int:photo_id>', methods=['POST'])
def delete_lab_photo(photo_id):
    if 'department_id' not in session:
        return redirect(url_for('department_login'))

    conn = sqlite3.connect(os.path.join(app.instance_path, 'gpd_site.db'))
    cursor = conn.cursor()

    cursor.execute("SELECT image_path FROM LabGallery WHERE id = ?", (photo_id,))
    row = cursor.fetchone()
    if row:
        image_path = os.path.join('static', row[0])
        if os.path.exists(image_path):
            os.remove(image_path)

        cursor.execute("DELETE FROM LabGallery WHERE id = ?", (photo_id,))
        conn.commit()

    conn.close()
    flash("Photo deleted successfully.", "info")
    return redirect(url_for('lab_gallery'))

# (More routes for subjects, materials etc. will follow...)


# Logout route
@app.route('/department/logout')
def department_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('department_login'))



# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
