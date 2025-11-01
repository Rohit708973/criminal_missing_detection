import face_recognition

def is_face_covered(face_img):
    """
    Checks if a given face image is partially covered using facial landmarks.
    Returns True if likely covered, False if normal.
    """
    # Detect landmarks in the face image
    landmarks_list = face_recognition.face_landmarks(face_img)
    
    if not landmarks_list:
        # No face detected → assume covered
        return True
    
    landmarks = landmarks_list[0]

    # Check essential landmarks: nose, mouth, and eyes
    essential_features = ["nose_tip", "top_lip", "bottom_lip", "left_eye", "right_eye"]
    
    for feature in essential_features:
        if feature not in landmarks or not landmarks[feature]:
            # Missing key facial feature → likely covered
            return True
    
    # All essential features are visible → normal
    return False
