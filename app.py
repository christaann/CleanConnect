
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from config import Config
import os, uuid, json, re

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

app = Flask(__name__)
app.config.from_object(Config)
mysql = MySQL(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def ensure_upload_folder():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def validate_password(password):
    """Returns list of unmet password rules. Empty list = all good."""
    errors = []
    if len(password) < 8:              errors.append("at least 8 characters")
    if not re.search(r'[A-Z]', password): errors.append("one uppercase letter")
    if not re.search(r'[a-z]', password): errors.append("one lowercase letter")
    if not re.search(r'[0-9]', password): errors.append("one digit")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        errors.append("one special character")
    return errors

# PUBLIC ROUTES

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# USER AUTHENTICATION

# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_logged_in' in session:
        return redirect(url_for('my_complaints'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Validate
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')

        pwd_errors = validate_password(password)
        if pwd_errors:
            flash(f'Password must contain: {", ".join(pwd_errors)}.', 'danger')
            return render_template('register.html')

        try:
            cur = mysql.connection.cursor()
            # Check if email already exists
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                flash('This email is already registered. Please login.', 'warning')
                cur.close()
                return render_template('register.html')

            hashed = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, hashed)
            )
            mysql.connection.commit()
            cur.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user_login'))

        except Exception as e:
            flash(f'Registration error: {str(e)}', 'danger')

    return render_template('register.html')


# --- USER LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if 'user_logged_in' in session:
        return redirect(url_for('my_complaints'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter email and password.', 'danger')
            return render_template('user_login.html')

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT id, name, email, password FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()
            cur.close()

            if user and check_password_hash(user[3], password):
                session['user_logged_in'] = True
                session['user_id']        = user[0]
                session['user_name']      = user[1]
                session['user_email']     = user[2]
                flash(f'Welcome back, {user[1]}!', 'success')
                return redirect(url_for('my_complaints'))
            else:
                flash('Invalid email or password!', 'danger')

        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')

    return render_template('user_login.html')


# --- USER LOGOUT ---
@app.route('/logout')
def user_logout():
    session.pop('user_logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('user_login'))


# USER COMPLAINT ROUTES (login required)

# SUBMIT ISSUE 
@app.route('/submit', methods=['GET', 'POST'])
def submit_issue():
    if 'user_logged_in' not in session:
        flash('Please login to submit a complaint.', 'warning')
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        issue_type  = request.form.get('issue_type')
        location    = request.form.get('location')
        latitude    = request.form.get('latitude') or None
        longitude   = request.form.get('longitude') or None
        description = request.form.get('description', '').strip()

        if not issue_type or not location:
            flash('Please fill in Issue Type and Location!', 'danger')
            return render_template('submitissue.html')

        if not description:
            description = 'No description provided.'

        # Photo upload
        photo_filename = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename != '' and allowed_file(photo.filename):
                ensure_upload_folder()
                ext = photo.filename.rsplit('.', 1)[1].lower()
                photo_filename = f"{uuid.uuid4().hex}.{ext}"
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO complaints
                    (user_id, issue_type, location, latitude, longitude,
                     description, photo, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (session['user_id'], issue_type, location, latitude,
                  longitude, description, photo_filename))
            mysql.connection.commit()
            cur.close()
            flash('✅ Complaint submitted successfully!', 'success')
            return redirect(url_for('my_complaints'))

        except Exception as e:
            flash(f'Database error: {str(e)}', 'danger')

    return render_template('submitissue.html')


# --- MY COMPLAINTS (user dashboard) ---
@app.route('/my_complaints')
def my_complaints():
    if 'user_logged_in' not in session:
        flash('Please login to view your complaints.', 'warning')
        return redirect(url_for('user_login'))

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, issue_type, location, description,
                   photo, status, submitted_at
            FROM complaints
            WHERE user_id = %s
            ORDER BY submitted_at DESC
        """, (session['user_id'],))
        complaints = cur.fetchall()

        # Stats for this user
        cur.execute("SELECT COUNT(*) FROM complaints WHERE user_id=%s", (session['user_id'],))
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE user_id=%s AND status='Pending'", (session['user_id'],))
        pending = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE user_id=%s AND status='In Progress'", (session['user_id'],))
        inprogress = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE user_id=%s AND status='Resolved'", (session['user_id'],))
        resolved = cur.fetchone()[0]
        cur.close()

        return render_template('my_complaints.html',
                               complaints=complaints,
                               total=total, pending=pending,
                               inprogress=inprogress, resolved=resolved)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('my_complaints.html',
                               complaints=[], total=0,
                               pending=0, inprogress=0, resolved=0)


# --- PUBLIC TRACK PAGE ---
@app.route('/track')
def track():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT c.id, c.issue_type, c.location, c.description,
                   c.photo, c.status, c.submitted_at, u.name
            FROM complaints c
            LEFT JOIN users u ON c.user_id = u.id
            ORDER BY c.submitted_at DESC
        """)
        complaints = cur.fetchall()
        cur.close()
        return render_template('track.html', complaints=complaints)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('track.html', complaints=[])


# --- MAP PAGE ---
@app.route('/map')
def map_view():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, issue_type, location, latitude, longitude,
                   status, description
            FROM complaints
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        complaints = cur.fetchall()
        cur.close()

        complaints_data = [{
            'id':         c[0],
            'issue_type': c[1],
            'location':   c[2],
            'latitude':   float(c[3]),
            'longitude':  float(c[4]),
            'status':     c[5],
            'description':c[6]
        } for c in complaints]

        complaints_json = json.dumps(complaints_data, ensure_ascii=True)
        return render_template('map.html',
                               complaints=complaints_data,
                               complaints_json=complaints_json)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('map.html', complaints=[], complaints_json='[]')


# ADMIN ROUTES

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        pwd_errors = validate_password(password)
        if pwd_errors:
            flash(f'Password must contain: {", ".join(pwd_errors)}.', 'danger')
            return render_template('login.html')

        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
            admin = cur.fetchone()
            cur.close()

            if admin and check_password_hash(admin[2], password):
                session['admin_logged_in'] = True
                session['admin_username']  = admin[1]
                flash(f'Welcome back, {admin[1]}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid username or password!', 'danger')

        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')

    return render_template('login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        flash('Please login to access the admin panel.', 'warning')
        return redirect(url_for('admin_login'))

    # Search/filter parameters
    search_id       = request.args.get('search_id', '').strip()
    search_name     = request.args.get('search_name', '').strip()
    search_location = request.args.get('search_location', '').strip()
    search_status   = request.args.get('search_status', '').strip()
    active_category = request.args.get('category', 'All').strip()

    try:
        cur = mysql.connection.cursor()

        query = """
            SELECT c.id, c.issue_type, c.location, c.latitude, c.longitude,
                   c.description, c.photo, c.status, c.submitted_at,
                   COALESCE(u.name, 'Guest') AS user_name
            FROM complaints c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        params = []

        if search_id:
            query += " AND c.id = %s"
            params.append(search_id)
        if search_name:
            query += " AND u.name LIKE %s"
            params.append(f'%{search_name}%')
        if search_location:
            query += " AND c.location LIKE %s"
            params.append(f'%{search_location}%')
        if search_status:
            query += " AND c.status = %s"
            params.append(search_status)
        if active_category and active_category != 'All':
            query += " AND c.issue_type = %s"
            params.append(active_category)

        query += " ORDER BY c.submitted_at DESC"
        cur.execute(query, params)
        complaints = cur.fetchall()

        # Convert decimals to float
        complaints = [
            (c[0], c[1], c[2],
             float(c[3]) if c[3] else None,
             float(c[4]) if c[4] else None,
             c[5], c[6], c[7], c[8], c[9])
            for c in complaints
        ]

        # Stats
        cur.execute("SELECT COUNT(*) FROM complaints")
        total_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
        pending_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'")
        inprogress_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
        resolved_count = cur.fetchone()[0]

        # Category counts
        categories = ['Garbage', 'Water Leakage', 'Street Light Not Working',
                      'Road Damage', 'Drainage Blockage']
        category_counts = {}
        for cat in categories:
            cur.execute("SELECT COUNT(*) FROM complaints WHERE issue_type=%s", (cat,))
            category_counts[cat] = cur.fetchone()[0]

        cur.close()

        return render_template('admin.html',
                               complaints=complaints,
                               total_count=total_count,
                               pending_count=pending_count,
                               inprogress_count=inprogress_count,
                               resolved_count=resolved_count,
                               categories=categories,
                               category_counts=category_counts,
                               active_category=active_category,
                               search_id=search_id,
                               search_name=search_name,
                               search_location=search_location,
                               search_status=search_status)

    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin.html', complaints=[],
                               total_count=0, pending_count=0,
                               inprogress_count=0, resolved_count=0,
                               categories=[], category_counts={},
                               active_category='All',
                               search_id='', search_name='',
                               search_location='', search_status='')


@app.route('/admin/update_status/<int:complaint_id>', methods=['POST'])
def update_status(complaint_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    new_status = request.form.get('status')
    if new_status not in ['Pending', 'In Progress', 'Resolved']:
        flash('Invalid status!', 'danger')
        return redirect(url_for('admin_dashboard'))

    category = request.form.get('category', 'All')

    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE complaints SET status=%s WHERE id=%s",
                    (new_status, complaint_id))
        mysql.connection.commit()
        cur.close()
        flash(f'Complaint #{complaint_id} updated to "{new_status}".', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('admin_dashboard', category=category))


@app.route('/admin/delete/<int:complaint_id>', methods=['POST'])
def delete_complaint(complaint_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    category = request.form.get('category', 'All')

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT photo FROM complaints WHERE id=%s", (complaint_id,))
        row = cur.fetchone()
        if row and row[0]:
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], row[0])
            if os.path.exists(photo_path):
                os.remove(photo_path)
        cur.execute("DELETE FROM complaints WHERE id=%s", (complaint_id,))
        mysql.connection.commit()
        cur.close()
        flash(f'Complaint #{complaint_id} deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('admin_dashboard', category=category))


# UTILITY ROUTES

@app.route('/setup_admin')
def setup_admin():
    try:
        hashed = generate_password_hash('Admin@123')
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM admin_users WHERE username='admin'")
        cur.execute("INSERT INTO admin_users (username, password) VALUES ('admin',%s)", (hashed,))
        mysql.connection.commit()
        cur.close()
        return """<html><body style="font-family:Arial;padding:40px;max-width:500px;margin:auto;">
            <h2 style="color:#16a34a;">✅ Admin Setup Complete!</h2>
            <p><strong>Username:</strong> admin</p>
            <p><strong>Password:</strong> Admin@123</p>
            <a href="/admin/login" style="background:#16a34a;color:white;padding:12px 24px;
               border-radius:8px;text-decoration:none;display:inline-block;margin-top:16px;">
               Go to Admin Login →</a>
        </body></html>"""
    except Exception as e:
        return f"<h2>❌ Failed: {str(e)}</h2>"


@app.route('/api/complaints')
def api_complaints():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, issue_type, location, latitude, longitude,
                   status, description, submitted_at
            FROM complaints
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """)
        rows = cur.fetchall()
        cur.close()
        result = [{'id':r[0],'issue_type':r[1],'location':r[2],
                   'latitude':float(r[3]),'longitude':float(r[4]),
                   'status':r[5],'description':r[6],'submitted_at':str(r[7])}
                  for r in rows]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    ensure_upload_folder()
    app.run(debug=True, port=5000)