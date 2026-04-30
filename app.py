from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

# --- MIDDLEWARE ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session: return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin': return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# --- AUTHENTICATION ---
@app.route('/auth', methods=['GET'])
def auth():
    return render_template('auth.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    role = request.form['role'] # 'admin' or 'member'
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)", 
                       (username, email, password, role))
        conn.commit()
    except mysql.connector.IntegrityError:
        flash('Email already exists.', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('auth'))

@app.route('/api/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    
    flash('Invalid credentials.', 'danger')
    return redirect(url_for('auth'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth'))

# --- CORE APPLICATION ---
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    if session['role'] == 'admin':
        # Admin sees all projects
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('dashboard_admin.html', projects=projects)
    else:
        # Member sees their assigned tasks
        cursor.execute("""
            SELECT t.*, p.name as project_name 
            FROM tasks t JOIN projects p ON t.project_id = p.id 
            WHERE t.assigned_to = %s ORDER BY t.due_date ASC
        """, (session['user_id'],))
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('dashboard_member.html', tasks=tasks)

@app.route('/api/projects/create', methods=['POST'])
@login_required
@admin_required
def create_project():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name, description, created_by) VALUES (%s, %s, %s)",
                   (request.form['name'], request.form['description'], session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/project/<int:project_id>')
@login_required
@admin_required
def view_project(project_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Get Project details
    cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
    project = cursor.fetchone()
    
    # Get all users to assign tasks to
    cursor.execute("SELECT id, username FROM users WHERE role = 'member'")
    users = cursor.fetchall()
    
    # Get tasks for this project
    cursor.execute("""
        SELECT t.*, u.username as assignee 
        FROM tasks t LEFT JOIN users u ON t.assigned_to = u.id 
        WHERE t.project_id = %s
    """, (project_id,))
    tasks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('project.html', project=project, users=users, tasks=tasks)

@app.route('/api/tasks/create', methods=['POST'])
@login_required
@admin_required
def create_task():
    project_id = request.form['project_id']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (project_id, title, description, assigned_to, due_date, created_by) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (project_id, request.form['title'], request.form['description'], 
          request.form['assigned_to'], request.form['due_date'], session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('view_project', project_id=project_id))

@app.route('/api/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", 
                   (request.form['status'], task_id))
    conn.commit()
    cursor.close()
    conn.close()
    
    if session['role'] == 'admin':
        return redirect(request.referrer) # Reloads current page
    return redirect(url_for('dashboard'))
