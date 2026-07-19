import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by score for the given user (OOP stub)."""
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation for why a song was recommended (OOP stub)."""
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py

    Returns a list of dictionaries, one per song. Numeric columns are
    converted from strings so they can be used in math later:
      - id and tempo_bpm  -> int
      - energy, valence, danceability, acousticness -> float
    """
    # Columns that should be parsed as numbers rather than left as strings.
    int_fields = {"id", "tempo_bpm"}
    float_fields = {"energy", "valence", "danceability", "acousticness"}

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = dict(row)
            for field in int_fields:
                song[field] = int(song[field])
            for field in float_fields:
                song[field] = float(song[field])
            songs.append(song)

    return songs

# --- Algorithm Recipe configuration (matches README) ---

# How much each feature is worth. Genre is weighted highest as a guardrail
# against jarring cross-genre picks; mood is lower because it overlaps with
# energy/valence.
WEIGHTS = {
    # Tuned to mirror how people actually listen: they reach for a *vibe*
    # (energy) first and cross genres freely when the feeling fits, so energy
    # leads and genre is a strong signal rather than a hard gate. Mood is
    # raised alongside valence because emotional fit matters as much as style.
    "energy": 3.0,
    "genre": 2.0,
    "mood": 2.0,
    "valence": 2.0,
    "danceability": 1.0,
    "acousticness": 1.0,
    "tempo": 1.0,
}

# Fixed bounds used to normalize tempo (BPM) onto a 0-1 scale so its large raw
# range does not dominate the other already-0-1 features.
TEMPO_MIN = 60.0
TEMPO_MAX = 180.0


def _normalize_tempo(bpm: float) -> float:
    """Map a BPM value onto 0-1 using fixed catalog bounds (clamped)."""
    scaled = (float(bpm) - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)
    return max(0.0, min(1.0, scaled))


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences (the "Scoring Rule").

    Scoring recipe (see WEIGHTS above):
      - Genre match:  +2.0 points (exact match only)
      - Mood match:   +2.0 points (exact match only)
      - Each numeric feature (energy 3.0, valence 2.0, danceability 1.0,
        acousticness 1.0, tempo 1.0) awards its weight scaled by closeness,
        `weight * (1 - abs(target - value))`. Tempo is normalized to 0-1
        first. The weighted total is divided by the sum of weights so the
        final score always lands in 0-1.

    Returns a tuple of (score, reasons), where `reasons` is a list of
    human-readable strings explaining where the points came from,
    e.g. "genre match: lofi (+2.0)".
    """
    total = 0.0
    reasons: List[str] = []

    # --- Categorical features: full points for an exact match ---
    if song.get("genre") == user_prefs.get("favorite_genre"):
        points = WEIGHTS["genre"]
        total += points
        reasons.append(f"genre match: {song['genre']} (+{points:.1f})")

    if song.get("mood") == user_prefs.get("favorite_mood"):
        points = WEIGHTS["mood"]
        total += points
        reasons.append(f"mood match: {song['mood']} (+{points:.1f})")

    # --- Numeric features: reward closeness, 1 - abs(target - value) ---
    # (label, pref_key, song_field, weight_key, optional value transform)
    numeric_features = [
        ("energy", "target_energy", "energy", "energy", None),
        ("valence", "target_valence", "valence", "valence", None),
        ("danceability", "target_danceability", "danceability", "danceability", None),
        ("acousticness", "target_acousticness", "acousticness", "acousticness", None),
        ("tempo", "target_tempo", "tempo_bpm", "tempo", _normalize_tempo),
    ]

    for label, pref_key, field, weight_key, transform in numeric_features:
        if pref_key not in user_prefs or song.get(field) in (None, ""):
            continue

        target = float(user_prefs[pref_key])
        value = float(song[field])
        if transform is not None:
            target = transform(target)
            value = transform(value)

        closeness = 1.0 - abs(target - value)  # 1.0 = identical, 0.0 = opposite
        points = WEIGHTS[weight_key] * closeness
        total += points
        reasons.append(f"{label} close ({value:.2f} vs {target:.2f}) (+{points:.2f})")

    # --- Normalize to 0-1 so the score is comparable across profiles ---
    max_possible = sum(WEIGHTS.values())
    score = total / max_possible if max_possible else 0.0

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Ranks the whole catalog and returns the top-k recommendations
    (the "Ranking Rule").

    Uses score_song() as a judge for every song, then sorts all songs from
    highest score to lowest and keeps the best k.

    Returns a list of (song, score, explanation) tuples, where `explanation`
    joins the scoring reasons into a single readable string.
    """
    # Score every song in the catalog (the "judge" step).
    scored = [(song, *score_song(user_prefs, song)) for song in songs]

    # Sort highest score first. sorted() returns a NEW list and leaves the
    # original `songs` untouched. key uses index 1 = the numeric score.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)

    # Keep the top k and turn each reasons-list into one explanation string.
    return [
        (song, score, "; ".join(reasons))
        for song, score, reasons in ranked[:k]
    ]
