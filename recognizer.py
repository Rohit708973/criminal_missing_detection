import os
import face_recognition
import json

CRIMINALS_DIR = "criminal_faces"
MISSING_DIR = "missing_faces"
CRIMINALS_JSON = "criminals.json"
MISSING_JSON = "missing.json"

criminal_encodings = []
criminal_names = []
criminal_image_map = {} # ID -> reference image
criminal_id_map = {} # name -> ID
criminal_data = [] # JSON data
missing_encodings = []
missing_names = []
missing_image_map = {} # ID -> reference image
missing_id_map = {} # name -> ID
missing_data = [] # JSON data

def load_criminal_faces():
    global criminal_encodings, criminal_names, criminal_image_map, criminal_id_map, criminal_data
    criminal_encodings.clear()
    criminal_names.clear()
    criminal_image_map.clear()
    criminal_id_map.clear()
    criminal_data.clear()
    if os.path.exists(CRIMINALS_JSON):
        with open(CRIMINALS_JSON, "r") as f:
            criminal_data = json.load(f)
        for entry in criminal_data:
            criminal_id_map[entry["name"]] = entry["id"]
    if not os.path.exists(CRIMINALS_DIR):
        os.makedirs(CRIMINALS_DIR)
        return
    for folder_id in os.listdir(CRIMINALS_DIR):
        folder_path = os.path.join(CRIMINALS_DIR, folder_id)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.lower().endswith((".jpg",".png",".jpeg")):
                    img_path = os.path.join(folder_path, file)
                    try:
                        image = face_recognition.load_image_file(img_path)
                        encs = face_recognition.face_encodings(image)
                        if encs:
                            name = None
                            for n, cid in criminal_id_map.items():
                                if cid == folder_id:
                                    name = n
                                    break
                            if name:
                                criminal_encodings.append(encs[0])
                                criminal_names.append(name)
                                criminal_image_map[folder_id] = img_path
                    except:
                        pass

def load_missing_faces():
    global missing_encodings, missing_names, missing_image_map, missing_id_map, missing_data
    missing_encodings.clear()
    missing_names.clear()
    missing_image_map.clear()
    missing_id_map.clear()
    missing_data.clear()
    if os.path.exists(MISSING_JSON):
        with open(MISSING_JSON,"r") as f:
            missing_data = json.load(f)
        for entry in missing_data:
            missing_id_map[entry["name"]] = entry["id"]
    if not os.path.exists(MISSING_DIR):
        os.makedirs(MISSING_DIR)
        return
    for folder_id in os.listdir(MISSING_DIR):
        folder_path = os.path.join(MISSING_DIR, folder_id)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.lower().endswith((".jpg",".png",".jpeg")):
                    img_path = os.path.join(folder_path, file)
                    try:
                        image = face_recognition.load_image_file(img_path)
                        encs = face_recognition.face_encodings(image)
                        if encs:
                            name = None
                            for n, cid in missing_id_map.items():
                                if cid == folder_id:
                                    name = n
                                    break
                            if name:
                                missing_encodings.append(encs[0])
                                missing_names.append(name)
                                missing_image_map[folder_id] = img_path
                    except:
                        pass

def match_criminal_face(face_encoding, tol=0.5):
    if not criminal_encodings:
        return None
    matches = face_recognition.compare_faces(criminal_encodings, face_encoding, tolerance=tol)
    if True in matches:
        return criminal_names[matches.index(True)]
    return None

def match_missing_face(face_encoding, tol=0.5):
    if not missing_encodings:
        return None
    matches = face_recognition.compare_faces(missing_encodings, face_encoding, tolerance=tol)
    if True in matches:
        return missing_names[matches.index(True)]
    return None

def get_criminal_details(name):
    for entry in criminal_data:
        if entry["name"] == name:
            return entry
    return None

def get_missing_details(name):
    for entry in missing_data:
        if entry["name"] == name:
            return entry
    return None

def get_criminal_image_by_name(name):
    cid = criminal_id_map.get(name)
    if cid:
        return criminal_image_map.get(cid)
    return None

def get_missing_image_by_name(name):
    mid = missing_id_map.get(name)
    if mid:
        return missing_image_map.get(mid)
    return None

load_criminal_faces()
load_missing_faces()
