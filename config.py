# System configurations and Labels Mapping

EXPECTED_FEATURES = 42
STABILIZATION_BUFFER_SIZE = 30
REGISTRATION_THRESHOLD = 25
REGISTRATION_DELAY_SEC = 1.5

# Uzbek Latin Alphabet
UZBEK_LABELS = {
    0: 'A', 1: 'B', 2: 'Ch', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: "G'", 8: 'H', 9: 'I',
    10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: "O'", 17: 'P', 18: 'Q', 19: 'R',
    20: 'S', 21: 'Sh', 22: 'T', 23: 'U', 24: 'V', 25: 'X', 26: 'Y', 27: 'Z', 28: 'Ng',
    29: '0', 30: '1', 31: '2', 32: '3', 33: '4', 34: '5', 35: '6', 36: '7', 37: '8', 38: '9',
    39: ' ',
    40: '.'
}

# American Sign Language (Standard A-Z, 0-9, space, dot)
AMERICAN_LABELS = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 
    10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 
    20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z',
    26: '0', 27: '1', 28: '2', 29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9',
    36: ' ', 37: '.'
}

# Russian Sign Language (А-Я, space, dot)
RUSSIAN_LABELS = {
    0: 'А', 1: 'Б', 2: 'В', 3: 'Г', 4: 'Д', 5: 'Е', 6: 'Ё', 7: 'Ж', 8: 'З', 9: 'И', 
    10: 'Й', 11: 'К', 12: 'Л', 13: 'М', 14: 'Н', 15: 'О', 16: 'П', 17: 'Р', 18: 'С', 19: 'Т', 
    20: 'У', 21: 'Ф', 22: 'Х', 23: 'Ц', 24: 'Ч', 25: 'Ш', 26: 'Щ', 27: 'Ъ', 28: 'Ы', 29: 'Ь', 
    30: 'Э', 31: 'Ю', 32: 'Я', 
    33: ' ', 34: '.'
}

SUPPORTED_LANGUAGES = {
    "Uzbek (O'zbek)": {
        "model_path": "./model.p",  # Based on currently existing model.p
        "labels": UZBEK_LABELS,
        "voice_lang": "uz" 
    },
    "American (ASL)": {
        "model_path": "./model_asl.p",
        "labels": AMERICAN_LABELS,
        "voice_lang": "en"
    },
    "Russian (Русский)": {
        "model_path": "./model_russian.p",
        "labels": RUSSIAN_LABELS,
        "voice_lang": "ru"
    }
}

DEFAULT_LANG = "Uzbek (O'zbek)"

# Hand Connections for drawing
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]
