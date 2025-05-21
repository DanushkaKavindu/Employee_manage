from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector # MySQL database connect කරගැනීමට අවශ්‍යයි

# Flask application එක ආරම්භ කරන්න
app = Flask(__name__)
# Session Secret Key එක, මෙය ඉතා රහසිගතව තබා ගත යුතුයි!
# මෙය නොමැතිව session වැඩ කරන්නේ නැත.
app.secret_key = 'your_super_secret_key_here' # මෙය වෙනස් කරන්න!

# =============================================================
# Database Configuration (XAMPP/MySQL)
# =============================================================
# මෙහිදී ඔබගේ MySQL database details ඇතුලත් කරන්න.
# XAMPP Apache සහ MySQL servers ආරම්භ කර ඇති බවට වග බලා ගන්න.
db_config = {
    'host': 'localhost',
    'user': 'root', # XAMPP වල default user එක
    'password': '', # XAMPP වල default password එක (සාමාන්‍යයෙන් හිස්)
    'database': 'employee_db' # ඔබ සාදන database නම
}

# Database connection එකක් ලබා දෙන function එක
def get_db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        # ඔබට මෙහිදී error message එකක් user ට පෙන්වීමටද පුළුවන්.
    return conn

# =============================================================
# Routes (URL Paths)
# =============================================================

# 1. මුල් පිටුව (Web App එකට මුලින්ම පිවිසෙන විට)
@app.route('/')
def index():
    return render_template('index.html')

# 2. Login Page එක
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] # login.html එකේ name="username"
        password = request.form['password'] # login.html එකේ name="password"

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True) # dictionary=True මගින් results dictionary එකක් ලෙස ලබා දෙයි
            # මෙතනදී ඔබගේ users table එකේ username (phone) සහ password check කරන්න.
            # සැබෑ application එකකදී password encrypt කර තබා ගත යුතුයි (e.g., bcrypt).
            query = "SELECT * FROM users WHERE phone = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            cursor.close()
            conn.close()

            if user:
                # Login සාර්ථක නම්, session එකක් ආරම්භ කර user ගේ තොරතුරු එහි ගබඩා කරන්න.
                session['loggedin'] = True
                session['id'] = user['id'] # user table එකේ id column එක
                session['username'] = user['phone'] # user table එකේ phone column එක
                flash('Login successful!', 'success') # සාර්ථක බවට message එකක්
                return redirect(url_for('homepage')) # Login වූ පසු homepage එකට යන්න
            else:
                flash('Incorrect username or password', 'danger') # වැරදි බවට message එකක්
        else:
            flash('Database connection error', 'danger')

    return render_template('login.html')

# 3. Register Page එක
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # මෙහිදී user details database එකට ඇතුලත් කරන්න.
                # සැබෑ application එකකදී password encrypt කර තබා ගත යුතුයි.
                query = "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (name, email, phone, password))
                conn.commit() # වෙනස්කම් database එකට save කරන්න
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('index')) # Register සාර්ථක නම් index.html (මුල් පිටුවට) යන්න
            except mysql.connector.Error as err:
                # Duplicate entries (e.g., same phone number) වැනි errors handle කරන්න.
                if err.errno == 1062: # MySQL error code for duplicate entry
                    flash('Phone number or Email already exists.', 'danger')
                else:
                    flash(f'An error occurred: {err}', 'danger')
                conn.rollback() # Error එකක් ආවොත් වෙනස්කම් අවලංගු කරන්න
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Database connection error', 'danger')

    return render_template('register.html')

# 4. Homepage (Login වූ පසු පෙනෙන පිටුව)
@app.route('/homepage')
def homepage():
    # User Login වී ඇත්දැයි පරීක්ෂා කරන්න.
    if 'loggedin' in session and session['loggedin']:
        return render_template('homepage.html', username=session['username'])
    else:
        flash('Please login to view this page.', 'info')
        return redirect(url_for('login')) # Login වී නොමැති නම් login page එකට redirect කරන්න.

# Logout Route එක
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index')) # Logout වූ පසු index.html (මුල් පිටුවට) යන්න.


# =============================================================
# Application Run
# =============================================================
if __name__ == '__main__':
    app.run(debug=False) # Development සඳහා Debug mode on. Production සඳහා False කරන්න.