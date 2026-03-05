from config import EXPECTED_FEATURES

def extract_hand_features(hand_landmarks):
    """
    Extracts normalized x and y coordinates from Mediapipe hand landmarks.
    Ensures the length of features is exactly EXPECTED_FEATURES.
    """
    x_ = [landmark.x for landmark in hand_landmarks]
    y_ = [landmark.y for landmark in hand_landmarks]

    min_x = min(x_)
    min_y = min(y_)
    
    # Calculate scale factor (max span across either axis)
    max_x = max(x_)
    max_y = max(y_)
    scale = max(max_x - min_x, max_y - min_y)
    
    # Avoid division by zero
    if scale == 0:
        scale = 1.0

    data_aux = []
    # Normalize relative to minimum x and y, and scale
    for landmark in hand_landmarks:
        data_aux.append((landmark.x - min_x) / scale)
        data_aux.append((landmark.y - min_y) / scale)

    # Pad or truncate to the expected number of features
    if len(data_aux) < EXPECTED_FEATURES:
        data_aux.extend([0] * (EXPECTED_FEATURES - len(data_aux)))
    elif len(data_aux) > EXPECTED_FEATURES:
        data_aux = data_aux[:EXPECTED_FEATURES]

    return data_aux
