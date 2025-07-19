# from flask import Flask, render_template, request, redirect, url_for, session, flash
# import mysql.connector
# from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps
# import joblib

# app = Flask(__name__)
# app.secret_key = "your_secret_key_here"

# # MySQL Connection
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="March#22",
#     database="expense"
# )
# cursor = db.cursor(dictionary=True)

# # Load ML Model and Vectorizer
# model = joblib.load("expense_model.pkl")
# vectorizer = joblib.load("vectorizer.pkl")

# # ------------------ Helpers ------------------

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get("user_id"):
#             flash("You need to log in to access this page.", "warning")
#             return redirect(url_for("login"))
#         return f(*args, **kwargs)
#     return decorated_function

# def predict_category(title, notes):
#     text = f"{title} {notes}".lower()
#     vec = vectorizer.transform([text])
#     return model.predict(vec)[0]

# # ------------------ Routes ------------------

# @app.route("/")
# def index():
#     if "user_id" in session:
#         return render_template("index.html", username=session.get("username"))
#     return render_template("index.html")

# @app.route("/signup", methods=["GET", "POST"])
# def signup():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         if cursor.fetchone():
#             flash("Username already exists.", "danger")
#             return redirect(url_for("signup"))

#         hashed_password = generate_password_hash(password)
#         cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
#         db.commit()
#         flash("Signup successful! Please log in.", "success")
#         return redirect(url_for("login"))
#     return render_template("signup.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]
#         cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#         user = cursor.fetchone()
#         if user and check_password_hash(user["password"], password):
#             session["user_id"] = user["id"]
#             session["username"] = user["username"]
#             flash("Login successful!", "success")
#             return redirect(url_for("index"))
#         flash("Invalid credentials", "danger")
#     return render_template("login.html")

# @app.route("/logout")
# def logout():
#     session.clear()
#     flash("Logged out successfully.", "success")
#     return redirect(url_for("index"))

# @app.route("/add_expense", methods=["GET", "POST"])
# @login_required
# def add_expense():
#     if request.method == "POST":
#         try:
#             title = request.form["title"]
#             amount = float(request.form["amount"])
#             date = request.form["date"]
#             notes = request.form["notes"]

#             # Predict category using ML model
#             category = predict_category(title, notes)

#             cursor.execute("""
#                 INSERT INTO expenses (user_id, title, amount, date, category, notes)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """, (session["user_id"], title, amount, date, category, notes))
#             db.commit()
#             flash(f"Expense added under '{category}' category!", "success")
#         except Exception as e:
#             db.rollback()
#             flash(f"Error adding expense: {str(e)}", "danger")
#         return redirect(url_for("track_expense"))
#     return render_template("add_expense.html")

# @app.route("/track_expense")
# @login_required
# def track_expense():
#     cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC", (session["user_id"],))
#     expenses = cursor.fetchall()
#     return render_template("track_expense.html", expenses=expenses)


# @app.route("/summary")
# @login_required
# def summary():
#     cursor.execute("""
#         SELECT category, SUM(amount) as total
#         FROM expenses
#         WHERE user_id = %s
#         GROUP BY category
#     """, (session["user_id"],))
#     data = cursor.fetchall()
#     return render_template("summary.html", data=data)

# # ------------------ Run ------------------
# if __name__ == "__main__":
#     app.run(debug=True, port=8000)  # or any free port you prefer



from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import joblib

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ---------- MySQL Connection ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="March#22",
    database="expense"
)
cursor = db.cursor(dictionary=True)

# ---------- Load ML Model ----------
model = joblib.load("expense_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def predict_category(title, notes):
    text = f"{title} {notes}".lower()
    X = vectorizer.transform([text])
    return model.predict(X)[0]

# ---------- Auth Decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Login required.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Routes ----------

@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html", username=session.get("username"))
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))
        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        db.commit()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("index"))

@app.route("/add_expense", methods=["GET", "POST"])
@login_required
def add_expense():
    if request.method == "POST":
        title = request.form["title"]
        amount = float(request.form["amount"])
        date = request.form["date"]
        notes = request.form["notes"]
        
        # ✅ Predict category using ML
        category = predict_category(title, notes)
        print("ML Prediction:", category)


        try:
            cursor.execute("""
                INSERT INTO expenses (user_id, title, amount, date, category, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (session["user_id"], title, amount, date, category, notes))
            db.commit()
            flash(f"Expense added under category '{category}'!", "success")
        except Exception as e:
            db.rollback()
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("track_expense"))
    return render_template("add_expense.html")

@app.route("/track_expense")
@login_required
def track_expense():
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY date DESC", (session["user_id"],))
    expenses = cursor.fetchall()
    return render_template("track_expense.html", expenses=expenses)

@app.route("/view_limit", methods=["GET", "POST"])
@login_required
def view_limit():
    if request.method == "POST":
        category = request.form["category"]
        month = request.form["month"]
        year = request.form["year"]
        amount = float(request.form["amount"])
        try:
            cursor.execute("""
                INSERT INTO budgets (user_id, category, month, year, amount)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE amount = VALUES(amount)
            """, (session["user_id"], category, month, year, amount))
            db.commit()
            flash("Budget saved.", "success")
        except Exception as e:
            db.rollback()
            flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("view_limit"))
    
    cursor.execute("SELECT * FROM budgets WHERE user_id = %s ORDER BY year DESC, month DESC", (session["user_id"],))
    limits = cursor.fetchall()
    return render_template("view_limit.html", limits=limits)

@app.route("/summary")
@login_required
def summary():
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id = %s
        GROUP BY category
    """, (session["user_id"],))
    data = cursor.fetchall()
    return render_template("summary.html", data=data)

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True, port=8000)
