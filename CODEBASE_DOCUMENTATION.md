# GPD Website - Codebase Documentation

## Project Overview

This is a Flask-based web application for a Government Polytechnic Department (GPD) website. The application provides a comprehensive management system for academic institutions including features for faculty management, student resources, circulars, materials, and administrative functions.

## Technology Stack

- **Backend Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML templates with Jinja2 templating
- **File Handling**: Werkzeug for secure file uploads
- **Session Management**: Flask sessions
- **Authentication**: Custom session-based authentication

## Project Structure

```
gpd_website/
├── app.py                 # Main Flask application
├── database.py           # Database models (SQLAlchemy)
├── gpd_site.db          # SQLite database file
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── instance/           # Flask instance folder
├── static/             # Static files (CSS, JS, images, uploads)
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
└── templates/          # HTML templates
    ├── base.html
    ├── home.html
    ├── dashboard.html
    └── [50+ template files]
```

## Core Features

### 1. Public Website Features
- **Homepage**: Displays circulars, newsletters, alumni information
- **Department Pages**: Individual pages for each department
- **Faculty Profiles**: Detailed faculty information and profiles
- **Student Resources**: Library, hostel, transport information
- **Committee Information**: Various institutional committees
- **Academic Calendar**: Academic year-based content filtering

### 2. Admin Panel Features
- **Dashboard**: Administrative overview
- **Circular Management**: Add, edit, delete circulars
- **Faculty Management**: Complete faculty database management
- **Subject Management**: Academic subject organization
- **Material Management**: Study materials upload and organization
- **Alumni Management**: Alumni database and testimonials
- **Newsletter System**: Newsletter creation and distribution
- **Committee Management**: Institutional committee management
- **EOA Letters**: End of Affiliation letter management
- **GTU Letters**: GTU affiliation letter management
- **Lab Gallery**: Laboratory image gallery management

### 3. Department-Level Features
- **Department Login**: Separate login for department heads
- **Department Dashboard**: Department-specific management
- **Circular Upload**: Department-specific circular management
- **Lab Gallery Management**: Department lab photo management
- **HoD Information Management**: Head of Department profile management

## Database Schema

### Key Tables

1. **admin** - Administrative users
2. **departments** - Department information and HoD details
3. **faculty** - Faculty members with detailed profiles
4. **circulars** - Institutional and department circulars
5. **subjects** - Academic subjects by department and semester
6. **materials** - Study materials linked to subjects
7. **alumni** - Alumni database with testimonials
8. **newsletters** - Newsletter management
9. **committees** - Various institutional committees
10. **eoa_letters** - End of Affiliation letters
11. **gtu_affiliation_letters** - GTU affiliation documents
12. **LabGallery** - Laboratory images by department

## Key Application Routes

### Public Routes
- `/` - Homepage with circulars and academic information
- `/department/<dept_name>` - Department-specific pages
- `/faculty/<faculty_id>` - Individual faculty profiles
- `/hostel`, `/library`, `/transport` - Student services
- `/committee/*` - Various committee pages

### Admin Routes
- `/login` - Admin authentication
- `/dashboard` - Admin dashboard
- `/manage-circulars` - Circular management
- `/manage-faculty` - Faculty management
- `/manage-subjects` - Subject management
- `/manage-materials` - Material management
- `/admin/lab_gallery` - Lab gallery management

### Department Routes
- `/department_login` - Department authentication
- `/department/dashboard` - Department dashboard
- `/upload_circular` - Department circular upload
- `/department/lab-gallery` - Department lab gallery
- `/edit_hod` - HoD information management

## File Upload System

The application handles multiple types of file uploads:

- **Circulars**: `static/uploads/Circulars/`
- **Faculty Photos**: `static/uploads/`
- **Study Materials**: `static/materials/`
- **Lab Images**: `static/images/labs/`
- **EOA Letters**: `static/uploads/eoa_letters/`
- **GTU Letters**: `static/uploads/gtu_affiliation_letters/`
- **Newsletter Files**: Various locations

## Authentication System

### Admin Authentication
- Username/password based login
- Session management with `admin_id` and `admin_name`
- Required for all administrative functions

### Department Authentication
- Department ID, email, and password based login
- Session management with `department_id` and `department_name`
- Limited to department-specific functions

## Academic Year Management

The application includes sophisticated academic year handling:
- Automatic academic year calculation (June to May cycle)
- Year-based content filtering for circulars and materials
- Academic year dropdown generation for historical data

## Database Models (SQLAlchemy)

Key model definitions in `database.py`:

- **Admin**: Administrative user management
- **Departments**: Department information with HoD details
- **Faculty**: Comprehensive faculty profiles
- **Circulars**: Document management with type classification
- **Subjects**: Academic curriculum organization
- **StudyMaterials**: Educational resource management
- **Alumni**: Alumni database with testimonials
- **PrincipalInfo**: Principal information management

## Security Features

- **Secure File Uploads**: Using `werkzeug.utils.secure_filename()`
- **Session-based Authentication**: Secure session management
- **File Type Validation**: Restricted file extensions
- **Path Security**: Absolute path handling for file operations

## Development Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Initialization**:
   ```bash
   python database.py
   ```

3. **Run Application**:
   ```bash
   python app.py
   ```

## Configuration

- **Secret Key**: Set in `app.secret_key` for session management
- **Database URI**: SQLite database in instance folder
- **Upload Folders**: Various static directories for file uploads
- **Debug Mode**: Enabled for development

## Template System

The application uses Jinja2 templating with:
- **Base Template**: `base.html` for common layout
- **Component Templates**: Modular template design
- **Dynamic Content**: Academic year filtering and user-specific content
- **Responsive Design**: Mobile-friendly layouts

## Notable Features

1. **Academic Year Intelligence**: Automatic academic year calculation and filtering
2. **Multi-level Authentication**: Admin and department-level access control
3. **File Management**: Comprehensive upload and management system
4. **Dynamic Content**: Real-time content updates with "new" indicators
5. **Department Autonomy**: Department-specific management capabilities
6. **Alumni Integration**: Alumni database with approval workflow
7. **Newsletter System**: Mass communication capabilities

## Future Enhancement Opportunities

- API development for mobile applications
- Advanced search functionality
- Email notification system
- Student portal integration
- Advanced reporting and analytics
- Backup and recovery system

## Maintenance Notes

- Regular database backups recommended
- Monitor upload folder sizes
- Review and update academic year calculations annually
- Periodic security audits for file upload functionality
- Template optimization for performance
