from flask import Flask, render_template, send_file, redirect, url_for, flash
import pandas as pd
import os
import cv2
import qrcode
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret123'  # For flashing messages

# Paths
STUDENT_CSV = 'student.csv'
ATTENDANCE_CSV = 'attendance.csv'
QR_FOLDER = 'static/qrcodes'

# Ensure directories exist
os.makedirs(QR_FOLDER, exist_ok=True)

# Function: Generate QR codes for each student
def generate_qr_codes():
    df = pd.read_csv(STUDENT_CSV)
    for _, row in df.iterrows():
        qr_data = f"{row['id']}|{row['name']}"
        qr_img = qrcode.make(qr_data)
        qr_path = os.path.join(QR_FOLDER, f"{row['id']}.png")
        qr_img.save(qr_path)

# Function: Mark attendance
def mark_attendance(user_id, name):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Create attendance file if not exists
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'w') as f:
            f.write("ID,Name,Date,Time\n")

    # Avoid duplicate attendance on same day
    df = pd.read_csv(ATTENDANCE_CSV)
    if ((df['ID'] == int(user_id)) & (df['Date'] == date_str)).any():
        return False  # Already marked today

    # Append new attendance
    with open(ATTENDANCE_CSV, 'a') as f:
        f.write(f"{user_id},{name},{date_str},{time_str}\n")
    return True

@app.route('/')
def index():
    generate_qr_codes()  # Generate/update QR codes
    df = pd.read_csv(STUDENT_CSV)
    return render_template('index.html', students=df.to_dict(orient='records'))

@app.route('/scan')
def scan():
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    scanned = False
    while not scanned:
        _, frame = cap.read()
        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            try:
                user_id, name = data.split('|')
                marked = mark_attendance(user_id, name)
                flash(f"Attendance {'marked' if marked else 'already marked'} for {name}", 'success')
            except ValueError:
                flash("Invalid QR code format!", 'danger')
            scanned = True
        cv2.imshow("Scan QR Code - Press Q to Quit", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return redirect(url_for('index'))

@app.route('/download')
def download():
    if os.path.exists(ATTENDANCE_CSV):
        return send_file(ATTENDANCE_CSV, as_attachment=True)
    else:
        flash("No attendance recorded yet!", 'warning')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
