import csv
import os
from io import StringIO
from flask import Response, Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import init_db
from markupsafe import Markup  

import json
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = 'your_secret_key'
mysql = init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # Get user details
    cur.execute("SELECT name, email FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    # Get latest feedback
    cur.execute("""
        SELECT q1, q2, q3, q4, q5, message, date_submitted
        FROM feedback
        WHERE user_id = %s
        ORDER BY date_submitted DESC
        LIMIT 1
    """, (user_id,))
    feedback = cur.fetchone()
    cur.close()

    return render_template("profile.html", user=user, feedback=feedback)

@app.route('/register', methods=['GET', 'POST'])
def register():
    session.pop('_flashes', None)  # clear stale messages

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()

        # ✅ Check if the email is already registered
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Email already registered. Please login or use a different email.', 'danger')
            cur.close()
            return redirect(url_for('register'))

       
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[4] if len(user) > 4 else 'user'
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    return render_template('dashboard.html', name=session['user_name'], role=session['user_role'])

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/book', methods=['GET', 'POST'])
def book():
    session.pop('_flashes', None)  # clear stale messages
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, city, available_batteries FROM stations")
    stations = cur.fetchall()

    if request.method == 'POST':
        station_id = request.form['station_id']
        date = request.form['date']
        time = request.form['time']
        user_id = session['user_id']

        # Check battery availability
        cur.execute("SELECT available_batteries FROM stations WHERE id = %s", (station_id,))
        available = cur.fetchone()[0]

        # Check for time slot conflict
        cur.execute("""
            SELECT COUNT(*) FROM appointments
            WHERE station_id = %s AND date = %s AND time = %s AND status IN ('approved', 'pending')
        """, (station_id, date, time))
        conflict_count = cur.fetchone()[0]

        if conflict_count > 0:
            flash("This time slot is already booked at the selected station. Please choose another.", "warning")
            cur.close()
            return redirect(url_for('book'))

        status = 'approved' if available > 0 else 'pending'

        if status == 'approved':
            cur.execute("UPDATE stations SET available_batteries = available_batteries - 1 WHERE id = %s", (station_id,))

        # Insert appointment
        cur.execute("""
            INSERT INTO appointments (user_id, station_id, date, time, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, station_id, date, time, status))

        mysql.connection.commit()
        cur.close()

        flash(f"Appointment {status}!", "success" if status == 'approved' else "warning")
        return redirect(url_for('dashboard'))

    cur.close()
    return render_template('book.html', stations=stations)

@app.route('/my_appointments')
def my_appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT a.date, a.time, a.status, s.name, s.city, a.id
        FROM appointments a
        JOIN stations s ON a.station_id = s.id
        WHERE a.user_id = %s
        ORDER BY a.date, a.time
    """, (user_id,))

    appointments = cur.fetchall()
    cur.close()
    return render_template('my_appointments.html', appointments=appointments)
@app.route('/cancel/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    cur.execute("SELECT status, station_id FROM appointments WHERE id = %s AND user_id = %s", 
                (appointment_id, session['user_id']))
    appointment = cur.fetchone()

    if appointment:
        status, station_id = appointment

        cur.execute("UPDATE appointments SET status = 'cancelled' WHERE id = %s", (appointment_id,))

        if status == 'approved':
            cur.execute("UPDATE stations SET available_batteries = available_batteries + 1 WHERE id = %s", 
                        (station_id,))

        mysql.connection.commit()
        flash("Appointment cancelled successfully.", "info")
    else:
        flash("Unauthorized or invalid appointment.", "danger")

    cur.close()
    return redirect(url_for('my_appointments'))


@app.route('/check_slot', methods=['POST'])
def check_slot():
    station_id = request.form['station_id']
    date = request.form['date']
    time = request.form['time']

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM appointments
        WHERE station_id = %s AND date = %s AND time = %s AND status IN ('approved', 'pending')
    """, (station_id, date, time))
    conflict_count = cur.fetchone()[0]
    cur.close()

    return {'available': conflict_count == 0}



@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'user_id' not in session:
        flash("Please log in to give feedback", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        q1 = int(request.form['q1'])
        q2 = int(request.form['q2'])
        q3 = int(request.form['q3'])
        q4 = int(request.form['q4'])
        q5 = int(request.form['q5'])
        message = request.form.get('message', '')

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO feedback (user_id, q1, q2, q3, q4, q5, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, q1, q2, q3, q4, q5, message))
        mysql.connection.commit()
        cur.close()

        flash("Thanks for your feedback!", "success")
        return redirect(url_for('feedback'))

    return render_template("feedback_form.html")









#admin all 
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))
    return render_template('admin_dashboard.html')




@app.route('/admin/add_station', methods=['GET', 'POST'])
def add_station():
    session.pop('_flashes', None)  # clear stale messages
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        station_id = request.form.get('station_id')
        name = request.form['name']
        address = request.form['address']
        city = request.form['city']
        zip_code = request.form['zip_code']
        total_batteries = int(request.form['total_batteries'])
        available_batteries = int(request.form['available_batteries'])

        if station_id:
            cur.execute("""
                UPDATE stations SET name=%s, address=%s, city=%s, zip_code=%s, total_batteries=%s, available_batteries=%s
                WHERE id=%s
            """, (name, address, city, zip_code, total_batteries, available_batteries, station_id))
            flash("Station updated successfully.", "success")
        else:
            cur.execute("""
                INSERT INTO stations (name, address, city, zip_code, total_batteries, available_batteries)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, address, city, zip_code, total_batteries, available_batteries))
            flash("Station added successfully.", "success")

        mysql.connection.commit()
        return redirect(url_for('add_station'))  # ✅ Corrected

    cur.execute("SELECT * FROM stations ORDER BY id DESC")
    stations = cur.fetchall()
    cur.close()

    return render_template("admin_add_station.html", stations=stations)

@app.route('/admin/delete_station/<int:station_id>')
def delete_station(station_id):
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM stations WHERE id = %s", (station_id,))
    mysql.connection.commit()
    cur.close()
    flash("Station deleted successfully.", "success")
    return redirect(url_for('add_station'))  # ✅ Corrected

@app.route('/admin/edit_station/<int:station_id>')
def edit_station(station_id):
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stations WHERE id = %s", (station_id,))
    station = cur.fetchone()
    cur.execute("SELECT * FROM stations ORDER BY id DESC")
    stations = cur.fetchall()
    cur.close()

    # Pass `station` to be used in form pre-fill
    return render_template("admin_add_station.html", station=station, stations=stations)




@app.route('/admin/view_appointments')
def view_appointments():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    selected_date = request.args.get('date')
    selected_station = request.args.get('station')

    cur = mysql.connection.cursor()

    # Load all station names for dropdown (optional: future enhancement)
    cur.execute("SELECT id, name FROM stations")
    station_list = cur.fetchall()

    # Fetch appointment list with optional filters
    query = """
        SELECT a.id, u.name, s.name, s.city, a.date, a.time, a.status
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN stations s ON a.station_id = s.id
        WHERE 1=1
    """
    params = []

    if selected_date:
        query += " AND a.date = %s"
        params.append(selected_date)

    if selected_station:
        query += " AND s.id = %s"
        params.append(selected_station)

    query += " ORDER BY a.date, a.time"

    cur.execute(query, tuple(params))
    appointments = cur.fetchall()
    cur.close()

    return render_template(
        "admin_view_appointments.html",
        appointments=appointments,
        station_list=station_list,
        selected_date=selected_date,
        selected_station=selected_station
    )
@app.route('/admin/update_status/<int:appointment_id>/<status>')
def update_status(appointment_id, status):
    if session.get('user_role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("UPDATE appointments SET status = %s WHERE id = %s", (status.lower(), appointment_id))
    mysql.connection.commit()
    cur.close()

    flash(f"Appointment status updated to {status}.", "success")
    return redirect(url_for('view_appointments'))  # ← redirect here to view page


@app.route('/admin/delete/<int:appointment_id>')
def delete_appointment(appointment_id):
    if session.get('user_role') != 'admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT status, station_id FROM appointments WHERE id = %s", (appointment_id,))
    appointment = cur.fetchone()

    if appointment:
        status, station_id = appointment

        if status == 'approved':
            cur.execute("UPDATE stations SET available_batteries = available_batteries + 1 WHERE id = %s", (station_id,))

        cur.execute("DELETE FROM appointments WHERE id = %s", (appointment_id,))
        mysql.connection.commit()
        flash("Appointment deleted successfully.", "success")
    else:
        flash("Appointment not found.", "warning")

    cur.close()
    return redirect(url_for('view_appointments'))

@app.route('/admin/view_users')
def view_users():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, role FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template("admin_view_users.html", users=users)

@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()

    # Optional: Check if the user exists and is not an admin
    cur.execute("SELECT role FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    if user:
        if user[0] == 'admin':
            flash("Cannot delete another admin.", "warning")
        else:
            # Delete appointments first (if foreign key constraint exists)
            cur.execute("DELETE FROM appointments WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            mysql.connection.commit()
            flash("User deleted successfully.", "success")
    else:
        flash("User not found.", "danger")

    cur.close()
    return redirect(url_for('view_users'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form.get('subject')
        message = request.form['message']
        # Save or process the feedback as needed
        return redirect(url_for('index'))
    return render_template('contact.html')

@app.route('/admin/feedback')
def admin_feedback():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()

    # Get all individual feedback
    cur.execute("""
        SELECT f.id, u.name, f.q1_rating, f.q2_rating, f.q3_rating, f.q4_rating, f.q5_rating, f.message, f.created_at
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    all_feedback = cur.fetchall()

    # Get average ratings for chart
    cur.execute("""
        SELECT 
            AVG(q1_rating), AVG(q2_rating), AVG(q3_rating), 
            AVG(q4_rating), AVG(q5_rating)
        FROM feedback
    """)
    avg_ratings = cur.fetchone()

    
    cur.close()

    

    


    return render_template("admin_feedback.html", feedback=all_feedback, avg_ratings=avg_ratings)



@app.route('/admin/view_feedbacks')
def view_feedbacks():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()

    # Fetch all feedback
    cur.execute("""
        SELECT f.id, u.name, f.q1, f.q2, f.q3, f.q4, f.q5, f.message, f.date_submitted
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.date_submitted DESC
    """)
    feedback = cur.fetchall()

    # Get average of each question
    cur.execute("""
        SELECT 
            ROUND(AVG(q1), 2), 
            ROUND(AVG(q2), 2), 
            ROUND(AVG(q3), 2), 
            ROUND(AVG(q4), 2), 
            ROUND(AVG(q5), 2)
        FROM feedback
    """)
    avg_ratings = cur.fetchone()
    cur.close()

    return render_template("admin_view_feedbacks.html", feedback=feedback, avg_ratings=avg_ratings or [0, 0, 0, 0, 0])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
