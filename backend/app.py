from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

from models import db, User, Alert
from chatbot import predict_with_model   # ✅ only need this, model is managed inside chatbot.py


# --- Flask setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = 'replace-with-a-secure-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'health.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --- User loader ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- DB create ---
with app.app_context():
    db.create_all()


# --- Public routes ---
@app.route('/')
def root():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        role = request.form.get('role', 'public')
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))

        u = User(username=username, password=generate_password_hash(password), role=role)
        db.session.add(u)
        db.session.commit()

        flash('Registered successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard' if user.role == 'officer' else 'public_home'))

        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/public_home')
@login_required
def public_home():
    if current_user.role != 'public':
        return redirect(url_for('dashboard'))
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    return render_template('public_home.html', alerts=alerts)


@app.route('/vaccination')
@login_required
def vaccination():
    schedule = [
        {"age": "At Birth", "vaccine": "BCG, HepB, OPV"},
        {"age": "6 weeks", "vaccine": "DTaP, IPV, Hib, HepB"},
        {"age": "10 weeks", "vaccine": "DTaP, IPV, Hib"},
        {"age": "14 weeks", "vaccine": "DTaP, IPV, Hib, HepB"},
        {"age": "9 months", "vaccine": "Measles, MR"}
    ]
    return render_template('vaccination.html', schedule=schedule)


# --- Chatbot route ---
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    text = request.form.get('message') or (request.json and request.json.get('message'))
    if not text:
        return jsonify({"error": "No message provided"}), 400

    res = predict_with_model(text)

    # Ensure keys exist and convert None → empty values
    return jsonify({
        "disease": res.get("predicted_disease") or "No match found",
        "confidence": float(res.get("confidence") or 0),
        "top3": res.get("top3") or []
    })





@app.route('/disease_form')
@login_required
def disease_form():
    return render_template('disease_form.html')


# --- Officer routes ---
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'officer':
        return redirect(url_for('public_home'))
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    return render_template('dashboard.html', alerts=alerts)


@app.route('/add_alert', methods=['POST'])
@login_required
def add_alert():
    if current_user.role != 'officer':
        return "Unauthorized", 403

    disease = request.form.get('disease')
    location = request.form.get('location')
    description = request.form.get('description')

    a = Alert(
        disease=disease,
        location=location,
        description=description,
        created_by=current_user.username
    )
    db.session.add(a)
    db.session.commit()

    flash('Alert created', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_alert/<int:alert_id>', methods=['POST'])
@login_required
def delete_alert(alert_id):
    if current_user.role != 'officer':
        return "Unauthorized", 403

    a = Alert.query.get_or_404(alert_id)
    db.session.delete(a)
    db.session.commit()

    flash('Alert deleted', 'success')
    return redirect(url_for('dashboard'))


# --- Run app ---
if __name__ == '__main__':
    app.run(debug=True)

