import os, smtplib, time
from datetime import datetime
from email.message import EmailMessage
from recognizer import (
    get_criminal_image_by_name, get_missing_image_by_name,
    get_criminal_details, get_missing_details
)

EMAIL_ADDRESS = "rohit121889@gmail.com"
EMAIL_PASSWORD = "tndk irjy vsew vgdi"

MASKED_RECIPIENTS = ["rohit708973@gmail.com"]
CRIMINAL_RECIPIENTS = ["rohit708973@gmail.com","master617615063@gmail.com"]

ALERTS_DIR = "alerts"
if not os.path.exists(ALERTS_DIR):
    os.makedirs(ALERTS_DIR)

last_alert_times = {}
ALERT_COOLDOWN = 120  # 2 minutes

def send_email(subject, body, recipients, attachments=None):
    msg = EmailMessage()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.set_content(body)
    if attachments:
        for path in attachments:
            if os.path.exists(path):
                with open(path,"rb") as f:
                    msg.add_attachment(f.read(), maintype="image", subtype="jpeg", filename=os.path.basename(path))
    try:
        with smtplib.SMTP("smtp.gmail.com",587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[EMAIL] Sent to: {recipients}")
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")

def send_alert(masked, criminal_name=None, missing_name=None, cam_location="Unknown", images=[]):
    global last_alert_times
    now = time.time()
    attachments = images.copy()

    if criminal_name or missing_name:
        identity = f"{criminal_name or missing_name}_{cam_location}"
        last_time = last_alert_times.get(identity)
        if not last_time or now-last_time>ALERT_COOLDOWN:
            last_alert_times[identity]=now

            body = f"Person detected at {cam_location}\nTime: {datetime.now()}\n\n"
            if criminal_name:
                c_details = get_criminal_details(criminal_name)
                if c_details:
                    body += f"CRIMINAL DETAILS:\nID: {c_details['id']}\nName: {c_details['name']}\nCrime: {c_details['crime']}\nLocation: {c_details['location']}\n\n"
                attachments.append(get_criminal_image_by_name(criminal_name))
            if missing_name:
                m_details = get_missing_details(missing_name)
                if m_details:
                    body += f"MISSING DETAILS:\nID: {m_details['id']}\nName: {m_details['name']}\nDescription: {m_details.get('description','N/A')}\n\n"
                attachments.append(get_missing_image_by_name(missing_name))

            subject = f"🚨 Alert: {criminal_name or missing_name} detected at {cam_location}"
            send_email(subject, body, CRIMINAL_RECIPIENTS, attachments)
        return

    if masked:
        identity = f"masked_cam_{cam_location}"
        last_time = last_alert_times.get(identity)
        if not last_time or now-last_time>ALERT_COOLDOWN:
            last_alert_times[identity]=now
            subject = f"🟣 Masked Person Detected at {cam_location}"
            body = f"Masked person detected at {cam_location}\nTime: {datetime.now()}"
            send_email(subject, body, MASKED_RECIPIENTS, attachments)

def delete_old_alerts(hours=12):
    cutoff = time.time() - hours*3600
    for f in os.listdir(ALERTS_DIR):
        path = os.path.join(ALERTS_DIR,f)
        if os.path.isfile(path) and os.path.getmtime(path)<cutoff:
            try:
                os.remove(path)
                print(f"[CLEANUP] Deleted {f}")
            except Exception as e:
                print(f"[ERROR] Failed to delete {f}: {e}")
