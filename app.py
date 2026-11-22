from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from prometheus_flask_exporter import PrometheusMetrics
from sqlalchemy import text
from datetime import datetime, timezone
import os
import json
import logging
import re

app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["WTF_CSRF_ENABLED"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("TASKFLOW_DATABASE_URI", "sqlite:///tasks.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

csrf = CSRFProtect(app)

metrics = PrometheusMetrics(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# JSON application logging
LOG_DIR = os.environ.get(
    "LOG_DIR",
    os.path.join(os.path.dirname(__file__), "logs")
)
os.makedirs(LOG_DIR, exist_ok=True)


class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "taskflow",
            "message": record.getMessage()
        })


log_handler = logging.FileHandler(
    os.path.join(LOG_DIR, "taskflow.jsonl")
)
log_handler.setFormatter(JSONLogFormatter())

if not any(
    isinstance(handler, logging.FileHandler)
    and getattr(handler, "baseFilename", None) == log_handler.baseFilename
    for handler in app.logger.handlers
):
    app.logger.addHandler(log_handler)

app.logger.setLevel(logging.INFO)
app.logger.info("TaskFlow application logging initialized")


# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Nullable to preserve existing user accounts during migration
    full_name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), nullable=True, default="Medium")
    category = db.Column(db.String(80), nullable=True)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    task_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(40), nullable=False)
    details = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Safe migration: add new account columns without deleting existing data
def migrate_database():
    db.create_all()

    columns = {
        row[1]
        for row in db.session.execute(
            text("PRAGMA table_info(user)")
        ).fetchall()
    }

    if "full_name" not in columns:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN full_name VARCHAR(150)")
        )

    if "email" not in columns:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN email VARCHAR(255)")
        )

    task_columns = {
        row[1]
        for row in db.session.execute(
            text("PRAGMA table_info(task)")
        ).fetchall()
    }

    additions = {
        "created_at": "DATETIME",
        "updated_at": "DATETIME",
        "due_date": "DATE",
        "priority": "VARCHAR(20)",
        "category": "VARCHAR(80)"
    }

    for column, column_type in additions.items():
        if column not in task_columns:
            db.session.execute(
                text(f"ALTER TABLE task ADD COLUMN {column} {column_type}")
            )

    db.session.execute(
        text("UPDATE task SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
    )
    db.session.execute(
        text("UPDATE task SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
    )
    db.session.execute(
        text("UPDATE task SET priority = 'Medium' WHERE priority IS NULL")
    )

    db.session.commit()
    app.logger.info("TaskFlow database schema checked")


with app.app_context():
    migrate_database()


def log_activity(action, details, task_id=None):
    activity = Activity(
        user_id=current_user.id,
        task_id=task_id,
        action=action,
        details=details
    )
    db.session.add(activity)



# Home
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([full_name, email, username, password, confirm_password]):
            flash("Please complete all required fields.")
            return redirect(url_for("register"))

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.")
            return redirect(url_for("register"))

        user = User(
            full_name=full_name,
            email=email,
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        app.logger.info("New TaskFlow account registered")
        flash("Account created successfully. Please sign in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# Login using either username or email
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get(
            "identifier",
            request.form.get("username", "")
        ).strip()

        password = request.form.get("password", "")

        user = User.query.filter(
            db.or_(
                User.username == identifier,
                db.func.lower(User.email) == identifier.lower()
            )
        ).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            app.logger.info("User signed in to TaskFlow")
            return redirect(url_for("dashboard"))

        flash("Invalid username/email or password.")

    return render_template("login.html")


# Main dashboard
@app.route("/dashboard")
@login_required
def dashboard():
    today = datetime.utcnow().date()
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()

    total_count = len(tasks)
    completed_count = sum(1 for task in tasks if task.completed)
    pending_count = total_count - completed_count
    productivity = round((completed_count / total_count) * 100) if total_count else 0

    priority_counts = {
        "High": sum(1 for task in tasks if (task.priority or "Medium") == "High"),
        "Medium": sum(1 for task in tasks if (task.priority or "Medium") == "Medium"),
        "Low": sum(1 for task in tasks if (task.priority or "Medium") == "Low"),
    }

    category_counts = {}
    for task in tasks:
        category = (task.category or "Uncategorized").strip()
        category_counts[category] = category_counts.get(category, 0) + 1

    today_tasks = [
        task for task in tasks
        if not task.completed and task.due_date == today
    ]

    upcoming_tasks = [
        task for task in tasks
        if not task.completed and task.due_date and task.due_date >= today
    ]
    upcoming_tasks.sort(key=lambda task: task.due_date)

    overdue_tasks = [
        task for task in tasks
        if not task.completed and task.due_date and task.due_date < today
    ]

    week_start = today - __import__("datetime").timedelta(days=today.weekday())
    weekly_completed = sum(
        1 for task in tasks
        if task.completed and task.updated_at and task.updated_at.date() >= week_start
    )

    recent_activity = Activity.query.filter_by(
        user_id=current_user.id
    ).order_by(Activity.created_at.desc()).limit(10).all()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        total_count=total_count,
        completed_count=completed_count,
        pending_count=pending_count,
        productivity=productivity,
        priority_counts=priority_counts,
        category_counts=category_counts,
        today_tasks=today_tasks,
        upcoming_tasks=upcoming_tasks[:8],
        overdue_tasks=overdue_tasks,
        weekly_completed=weekly_completed,
        weekly_goal=5,
        recent_activity=recent_activity,
        today=today
    )


# Add task
@app.route("/add", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not title:
        flash("Task title is required.")
        return redirect(url_for("dashboard"))

    due_date_value = request.form.get("due_date", "").strip()
    try:
        due_date = datetime.strptime(due_date_value, "%Y-%m-%d").date() if due_date_value else None
    except ValueError:
        flash("Please enter a valid due date.")
        return redirect(url_for("dashboard"))

    priority = request.form.get("priority", "Medium").strip()
    if priority not in ("Low", "Medium", "High"):
        priority = "Medium"

    task = Task(
        title=title,
        description=description,
        user_id=current_user.id,
        due_date=due_date,
        priority=priority,
        category=request.form.get("category", "").strip()[:80] or None
    )

    db.session.add(task)
    db.session.flush()
    log_activity("created", f"Created task: {task.title}", task.id)
    db.session.commit()

    flash("Task added successfully.")
    return redirect(url_for("dashboard"))


# Complete or reopen task
@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first_or_404()

    task.completed = not task.completed
    action = "completed" if task.completed else "reopened"
    log_activity(action, f"{action.capitalize()} task: {task.title}", task.id)
    task.updated_at = datetime.utcnow()
    db.session.commit()

    return redirect(url_for("dashboard"))


# Edit task
@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        title = request.form.get("title", "").strip()

        if not title:
            flash("Task title is required.")
            return redirect(
                url_for("edit_task", task_id=task.id)
            )

        task.title = title
        task.description = request.form.get(
            "description", ""
        ).strip()
        due_date_value = request.form.get("due_date", "").strip()
        try:
            task.due_date = datetime.strptime(due_date_value, "%Y-%m-%d").date() if due_date_value else None
        except ValueError:
            flash("Please enter a valid due date.")
            return redirect(url_for("edit_task", task_id=task.id))

        priority = request.form.get("priority", "Medium").strip()
        task.priority = priority if priority in ("Low", "Medium", "High") else "Medium"
        task.category = request.form.get("category", "").strip()[:80] or None
        task.updated_at = datetime.utcnow()
        log_activity("edited", f"Edited task: {task.title}", task.id)

        db.session.commit()
        flash("Task updated successfully.")

        return redirect(url_for("dashboard"))

    return render_template("edit.html", task=task)


# Delete task
@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(
        id=task_id,
        user_id=current_user.id
    ).first_or_404()

    log_activity("deleted", f"Deleted task: {task.title}", task.id)
    db.session.delete(task)
    db.session.commit()

    flash("Task deleted.")
    return redirect(url_for("dashboard"))


# Task API
@app.route("/api/tasks")
@login_required
def api_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    return {
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed
            }
            for task in tasks
        ]
    }





# All tasks page
@app.route("/tasks")
@login_required
def my_tasks():
    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).order_by(Task.created_at.desc()).all()
    return render_template(
        "workspace.html", page="tasks",
        title="My Tasks", tasks=tasks
    )


# Dedicated add task page
@app.route("/add-task")
@login_required
def add_task_page():
    return render_template(
        "workspace.html", page="add_task",
        title="Add New Task"
    )


# Completed tasks
@app.route("/completed")
@login_required
def completed_tasks():
    tasks = Task.query.filter_by(
        user_id=current_user.id, completed=True
    ).order_by(Task.updated_at.desc()).all()
    return render_template("workspace.html", page="completed",
                           title="Completed Tasks", tasks=tasks)


# Calendar
@app.route("/calendar")
@login_required
def calendar():
    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).filter(Task.due_date.isnot(None)).order_by(Task.due_date.asc()).all()
    return render_template("workspace.html", page="calendar",
                           title="Task Calendar", tasks=tasks)


# Activity history
@app.route("/activity")
@login_required
def activity_page():
    activities = Activity.query.filter_by(
        user_id=current_user.id
    ).order_by(Activity.created_at.desc()).all()
    return render_template("workspace.html", page="activity",
                           title="Activity History", activities=activities)


# Analytics
@app.route("/analytics")
@login_required
def analytics_page():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    total = len(tasks)
    completed = sum(1 for task in tasks if task.completed)
    priorities = {
        "High": sum(1 for task in tasks if (task.priority or "Medium") == "High"),
        "Medium": sum(1 for task in tasks if (task.priority or "Medium") == "Medium"),
        "Low": sum(1 for task in tasks if (task.priority or "Medium") == "Low"),
    }
    categories = {}
    for task in tasks:
        category = (task.category or "Uncategorized").strip()
        categories[category] = categories.get(category, 0) + 1
    return render_template(
        "workspace.html", page="analytics", title="Task Analytics",
        tasks=tasks, total=total, completed=completed,
        pending=total-completed,
        productivity=round(completed * 100 / total) if total else 0,
        priorities=priorities, categories=categories
    )


# Profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if len(full_name) > 150 or len(email) > 255:
            flash("Please check the length of your profile details.")
        elif email and User.query.filter(
            User.email == email, User.id != current_user.id
        ).first():
            flash("That email address is already in use.")
        else:
            current_user.full_name = full_name or None
            current_user.email = email or None
            db.session.commit()
            flash("Profile updated successfully.")
            return redirect(url_for("profile"))

    return render_template("workspace.html", page="profile",
                           title="My Profile")


# Settings
@app.route("/settings")
@login_required
def settings_page():
    return render_template("workspace.html", page="settings",
                           title="Settings")


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=5002,
        debug=False
    )
