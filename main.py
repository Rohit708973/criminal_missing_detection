import cv2, os, threading
from datetime import datetime
import face_recognition
from recognizer import match_criminal_face, match_missing_face
from alert import send_alert, delete_old_alerts
from maskdetector import is_face_covered # updated landmark-based version

def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < threshold

def upscale_image(img, scale=2):
    height, width = img.shape[:2]
    return cv2.resize(img, (width * scale, height * scale), interpolation=cv2.INTER_CUBIC)

if not os.path.exists("alerts"):
    os.makedirs("alerts")

cameras = {
    0: "Front Gate, Hyderabad",
    # Add more cameras as needed
}

def process_camera(cam_source, cam_location):
    cap = cv2.VideoCapture(cam_source)
    print(f"[INFO] Camera started at {cam_location}")
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"[ERROR] Cannot read from camera at {cam_location}")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            # 1. Blur check
            if is_blurry(face_img):
                print("[INFO] Face image blurry. Enhancing to HD...")
                face_img = upscale_image(face_img)
            rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            encs = face_recognition.face_encodings(rgb)
            criminal_name = missing_name = None
            if encs:
                face_encoding = encs[0]
                criminal_name = match_criminal_face(face_encoding)
                missing_name = match_missing_face(face_encoding)
            masked = is_face_covered(face_img)
            if criminal_name and missing_name:
                label = f"Criminal & Missing: {criminal_name}"
                color = (0,0,255)
            elif criminal_name:
                label = f"Criminal: {criminal_name}"
                color = (0,0,255)
            elif missing_name:
                label = f"Missing: {missing_name}"
                color = (0,165,255)
            elif masked:
                label = "Masked"
                color = (128,0,128)
            else:
                label = "Normal"
                color = (0,255,0)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = f"alerts/alert_{timestamp}_{cam_location.replace(' ','_')}.jpg"
            cv2.imwrite(img_path, face_img)
            send_alert(masked, criminal_name, missing_name, cam_location, [img_path])
        frame_count += 1
        if frame_count % 100 == 0:
            delete_old_alerts(12)
        cv2.imshow(f"{cam_location}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    threads = []
    for source, location in cameras.items():
        t = threading.Thread(target=process_camera, args=(source, location))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
