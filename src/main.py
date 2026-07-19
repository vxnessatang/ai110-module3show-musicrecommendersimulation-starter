"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

It defines several user "taste profiles" (both realistic and adversarial
edge cases), then runs the recommender for each one and prints the top 5.

The functions themselves live in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# User preference profiles
#
# Each profile is a dict of target values for every feature the recommender
# scores on. The first three are "realistic" listeners; the rest are
# adversarial / edge-case profiles designed to stress-test the scoring logic
# (conflicting signals, an unknown genre, and impossible extreme targets).
# ---------------------------------------------------------------------------

PROFILES = [
    # --- 1. Realistic: High-Energy Pop ---
    {
        "name": "High-Energy Pop",
        "prefs": {
            "favorite_genre": "pop",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "target_valence": 0.80,
            "target_danceability": 0.85,
            "target_acousticness": 0.05,
            "target_tempo": 130,
        },
    },
    # --- 2. Realistic: Chill Lofi ---
    {
        "name": "Chill Lofi",
        "prefs": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.35,
            "target_valence": 0.60,
            "target_danceability": 0.55,
            "target_acousticness": 0.85,
            "target_tempo": 78,
        },
    },
    # --- 3. Realistic: Deep Intense Rock ---
    {
        "name": "Deep Intense Rock",
        "prefs": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "target_valence": 0.45,
            "target_danceability": 0.60,
            "target_acousticness": 0.10,
            "target_tempo": 150,
        },
    },
    # --- 4. Adversarial: Conflicting signals ---
    # Wants maximum energy AND a sad/melancholy mood at a slow tempo. Almost
    # no real song is both "0.95 energy" and "melancholy at 70 BPM", so this
    # probes whether the numeric closeness score fights the mood match.
    {
        "name": "ADVERSARIAL: Sad but High-Energy",
        "prefs": {
            "favorite_genre": "folk",
            "favorite_mood": "melancholy",
            "target_energy": 0.95,
            "target_valence": 0.10,
            "target_danceability": 0.90,
            "target_acousticness": 0.90,
            "target_tempo": 70,
        },
    },
    # --- 5. Adversarial: Unknown genre & mood ---
    # Neither "k-pop" nor "hyped" exist in the catalog, so the categorical
    # checks can NEVER fire. This tests whether ranking degrades gracefully
    # to a pure numeric-closeness ranking instead of breaking.
    {
        "name": "ADVERSARIAL: Genre/Mood Not In Catalog",
        "prefs": {
            "favorite_genre": "k-pop",
            "favorite_mood": "hyped",
            "target_energy": 0.60,
            "target_valence": 0.60,
            "target_danceability": 0.60,
            "target_acousticness": 0.40,
            "target_tempo": 110,
        },
    },
    # --- 6. Adversarial: Impossible extremes ---
    # Every numeric target is pushed to an unreachable extreme (max energy,
    # zero valence, max danceability, zero acousticness, off-the-chart tempo).
    # This checks that scores stay bounded in 0-1 and nothing goes negative.
    {
        "name": "ADVERSARIAL: Impossible Extremes",
        "prefs": {
            "favorite_genre": "metal",
            "favorite_mood": "aggressive",
            "target_energy": 1.0,
            "target_valence": 0.0,
            "target_danceability": 1.0,
            "target_acousticness": 0.0,
            "target_tempo": 200,
        },
    },
]


def print_recommendations(profile: dict, songs: list) -> None:
    """Run the recommender for one profile and print its top 5 nicely."""
    prefs = profile["prefs"]
    recommendations = recommend_songs(prefs, songs, k=5)

    print()
    print("=" * 60)
    print(f"  PROFILE: {profile['name']}")
    print(f"  {prefs['favorite_genre']} / {prefs['favorite_mood']}  |  "
          f"energy target {prefs['target_energy']}")
    print("=" * 60)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  {rank}. {song['title']}  -  {song['artist']}")
        print(f"     Score: {score:.2f}   [{song['genre']} / {song['mood']}]")
        print("     Reasons:")
        for reason in explanation.split("; "):
            print(f"       - {reason}")

    print("\n" + "=" * 60)


def main() -> None:
    """Load the catalog and print top-5 recommendations for every profile."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for profile in PROFILES:
        print_recommendations(profile, songs)


if __name__ == "__main__":
    main()
