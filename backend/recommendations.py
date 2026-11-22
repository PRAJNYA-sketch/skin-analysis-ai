
HAIRSTYLE_RECOMMENDATIONS = {
    "Oval": {
        "hairstyles": [
            "Layered Haircut",
            "Curtain Bangs",
            "Long Waves",
            "Bob Cut"
        ],
        "avoid": ["Very heavy straight bangs"]
    },

    "Round": {
        "hairstyles": [
            "Long Layers",
            "Side Swept Bangs",
            "High Ponytail",
            "Long Waves"
        ],
        "avoid": ["Very short rounded bob"]
    },

    "Square": {
        "hairstyles": [
            "Soft Layers",
            "Side Part",
            "Long Waves",
            "Wispy Bangs"
        ],
        "avoid": ["Very blunt jaw-length cuts"]
    },

    "Heart": {
        "hairstyles": [
            "Side Swept Bangs",
            "Chin Length Bob",
            "Shoulder Length Layers",
            "Soft Waves"
        ],
        "avoid": ["Excessive volume at the crown"]
    },

    "Diamond": {
        "hairstyles": [
            "Chin Length Bob",
            "Curtain Bangs",
            "Side Swept Hair",
            "Shoulder Length Waves"
        ],
        "avoid": ["Very tight pulled-back hairstyles"]
    }
}


def get_hairstyle_recommendations(face_shape):
    return HAIRSTYLE_RECOMMENDATIONS.get(
        face_shape,
        {
            "hairstyles": [],
            "avoid": []
        }
    )
