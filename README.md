# ⚡ EV Battery Booking System

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-blue?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.0-blue?logo=tailwind-css&logoColor=white)
![Railway](https://img.shields.io/badge/DB%20Hosted%20on-Railway-4B5563?logo=railway)
![Render](https://img.shields.io/badge/Deployed%20on-Render-00c896?logo=render&logoColor=white)
![MIT License](https://img.shields.io/badge/License-MIT-green)

A full-stack web application that allows users to book EV battery appointments and provides an admin panel to manage stations, appointments, users, and feedback.

🔗 **Live Demo:** [View Project on Render](https://ev-battery-booking.onrender.com/)  
🛠️ **GitHub Repo:** [EV-Battery-Booking](https://github.com/vedantjadhav07/EV-Battery-Booking)

---

## 🚀 Features

### 👤 User Features
- Register/Login with secure authentication
- Book EV battery swap appointments by selecting:
  - Station
  - Date & Time (with real-time availability check)
- View upcoming & past appointments
- Submit feedback after service
- View profile & recent feedback

### 🛠️ Admin Features
- Admin Dashboard with metrics
- Add, Edit, Delete EV Stations
- Approve, Cancel, or Delete Appointments
- View all Users
- View feedback with analytics (written + rating)

---

## 🧰 Tech Stack

| Technology       | Use Case                  |
|------------------|---------------------------|
| **Python + Flask** | Backend + Routing        |
| **MySQL (via Railway)** | Database (Cloud)    |
| **Jinja2**        | Templating                |
| **Tailwind CSS**  | Frontend Styling          |
| **Render**        | Web App Hosting           |
| **Railway**       | Cloud MySQL DB Hosting    |

---

## 🖥️ Installation (Run Locally)

### 📦 Clone the repo
```bash
git clone https://github.com/vedantjadhav07/EV-Battery-Booking.git
cd EV-Battery-Booking
📁 Install Python dependencies
bash
Copy
Edit
pip install -r requirements.txt
⚙️ Set up environment variables
Create a .env file in the project root and add:

env
Copy
Edit
MYSQL_HOST=turntable.proxy.rlwy.net
MYSQL_USER=root
MYSQL_PASSWORD=your-password-here
MYSQL_DB=railway
MYSQL_PORT=45859
Make sure your Railway DB is active.

▶️ Run the Flask App
bash
Copy
Edit
python app.py
Open your browser: http://localhost:5000

🌐 Hosted Live
The app is deployed and live using:

✅ Render (Web Server)

✅ Railway (Cloud MySQL Database)

🔗 Live App Link

📸 Screenshots
Add screenshots here:

✅ User Dashboard

✅ Admin Panel

✅ Booking Form

✅ Feedback Form

✅ Profile Page

📁 Folder Structure
bash
Copy
Edit
EV-Battery-Booking/
│
├── static/                  # CSS, JS, icons
├── templates/               # HTML pages (Jinja2)
├── app.py                   # Main Flask backend
├── db_config.py             # DB connection setup
├── .env                     # Environment secrets
├── requirements.txt         # Python packages
└── README.md                # This file
📌 Future Enhancements
📊 Graphs and analytics for admin

📧 Email confirmations

🌍 Map integration for stations

🔐 OTP-based login

👨‍💻 Author
Vedant Jadhav

GitHub: @vedantjadhav07
