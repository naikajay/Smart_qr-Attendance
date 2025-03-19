import pandas as pd
import qrcode
import os

# Load student data
df = pd.read_csv('student.csv')

# Ensure qrcodes directory exists
os.makedirs('static/qrcodes', exist_ok=True)

# Generate QR for each student
for _, row in df.iterrows():
    qr_data = f"{row['id']}|{row['name']}"
    qr = qrcode.make(qr_data)
    qr.save(f"static/qrcodes/{row['id']}.png")

print("QR Codes generated in 'static/qrcodes'")
