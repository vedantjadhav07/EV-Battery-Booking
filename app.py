import csv
import os
from io import StringIO
from flask import Response
from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import init_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'
mysql = init_db(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()
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
    else:
        return render_template('dashboard.html', name=session['user_name'], role=session['user_role'])


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/book', methods=['GET', 'POST'])
def book():
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

        
        cur.execute("SELECT available_batteries FROM stations WHERE id = %s", (station_id,))
        available = cur.fetchone()[0]

        if available > 0:
            status = 'approved'
            
            cur.execute("UPDATE stations SET available_batteries = available_batteries - 1 WHERE id = %s", (station_id,))
        else:
            status = 'pending'

      
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

# -- Show User's Appointments --
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

# -- Admin Dashboard View --
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    selected_date = request.args.get('date')
    selected_station = request.args.get('station')

    cur = mysql.connection.cursor()

    # Load all station names for dropdown
    cur.execute("SELECT id, name FROM stations")
    station_list = cur.fetchall()

    # Build appointment query based on filters
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
        'admin_dashboard.html',
        appointments=appointments,
        station_list=station_list,
        selected_date=selected_date,
        selected_station=selected_station
    )

# -- Admin Can Update Appointment Status --
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
    return redirect(url_for('admin_dashboard'))

# -- Export Appointments to CSV --
@app.route('/admin/export_csv')
def export_csv():
    if session.get('user_role') != 'admin':
        flash("Access denied", "danger")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.name, u.email, s.name, s.city, a.date, a.time, a.status
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN stations s ON a.station_id = s.id
        ORDER BY a.date, a.time
    """)
    data = cur.fetchall()
    cur.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['User', 'Email', 'Station', 'City', 'Date', 'Time', 'Status'])
    writer.writerows(data)

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=appointments.csv"}
    )

# -- Cancel Appointment (User) --
@app.route('/cancel/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    # Check ownership and get status
    cur.execute("SELECT status, station_id FROM appointments WHERE id = %s AND user_id = %s", 
                (appointment_id, session['user_id']))
    appointment = cur.fetchone()

    if appointment:
        status, station_id = appointment

        # Mark as cancelled
        cur.execute("UPDATE appointments SET status = 'cancelled' WHERE id = %s", (appointment_id,))

        # If already approved, return one battery
        if status == 'approved':
            cur.execute("UPDATE stations SET available_batteries = available_batteries + 1 WHERE id = %s", 
                        (station_id,))

        mysql.connection.commit()
        flash("Appointment cancelled successfully.", "info")
    else:
        flash("Unauthorized or invalid appointment.", "danger")

    cur.close()
    return redirect(url_for('my_appointments'))

# -- Delete Appointment (Admin Only) --
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
    return redirect(url_for('admin_dashboard'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form.get('subject')
        message = request.form['message']

        # Future: save to DB or send via email
        flash("Thanks for reaching out. We’ll get back to you soon.", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

# -- Run App --
#if __name__ == '__main__':
   # app.run(debug=True)



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


