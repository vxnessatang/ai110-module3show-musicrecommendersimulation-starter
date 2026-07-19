# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

My version, **VibeMatch 1.0**, is a content-based music recommender that runs
from the command line. It loads a catalog of 19 songs, compares each one to a
user's "taste profile" (a favorite genre and mood plus target values for energy,
valence, danceability, acousticness, and tempo), and gives every song a 0-1
score based on how closely it matches. It then sorts the catalog and prints the
top 5 recommendations, each with a plain-language explanation of why it was
picked. I test it against six built-in profiles, three realistic listeners and
three "adversarial" edge cases, to see where the scoring holds up and where it
breaks.

---

## How The System Works

Real-world recommenders like Spotify or YouTube predict what you'll love next by
blending two ideas: **collaborative filtering**, which studies the behavior of
millions of other users to find people with similar taste ("listeners like you
also loved this"), and **content-based filtering**, which studies the attributes
of the songs themselves (tempo, energy, mood) and finds new tracks that resemble
what you already enjoy. They learn from signals like likes, skips, replays, and
playlist placement, and they mix everything together in huge machine-learning
models. My version is a **simplified, content-based recommender**. It does not
use other users' data or any machine learning. Instead, it compares the measured
attributes of each song to a user's stated taste and scores how closely they
match. I prioritize **transparency and closeness**: every recommendation can be
explained by the numbers, and the system rewards songs whose features are near
the user's preference rather than songs that are simply "high" or "low" on any
feature.

### Features my objects use

**`Song`** stores:

- `title`, `artist`: labels for display (not used in scoring)
- `genre`: categorical (pop, lofi, rock, jazz, ambient, synthwave, indie pop)
- `mood`: categorical (happy, chill, intense, relaxed, moody, focused)
- `energy`: numeric 0-1
- `valence`: numeric 0-1 (musical positivity / "happiness")
- `danceability`: numeric 0-1
- `acousticness`: numeric 0-1
- `tempo_bpm`: numeric (normalized to 0-1 before scoring)

**`UserProfile`** stores the user's preferred target for each of those same
features, so a song can be compared against it:

- `preferred_genre`: categorical
- `preferred_mood`: categorical
- `target_energy`, `target_valence`, `target_danceability`,
  `target_acousticness`, `target_tempo`: numeric ideals (0-1)
- `weights`: how much each feature counts toward the final score
  (energy 3, genre 2, mood 2, valence 2, others 1)

### How scoring and ranking work

- **Scoring Rule (one song):** For each numeric feature, the score is
  `1 - |target - song_value|`, so closer values earn more points. For genre and
  mood, an exact match earns a point. Each feature is multiplied by its weight
  and the results are combined into a single 0-1 score.
- **Ranking Rule (the list):** All songs are scored, the results are sorted
  highest-first, and the top N are returned as the recommendations.

### Finalized Algorithm Recipe

**Step 1: Score each feature (0-1)**

| Feature | Rule | Weight |
|---------|------|--------|
| `energy` | `1 - abs(target - value)` | **3.0** |
| `genre` | `1` if exact match, else `0` | 2.0 |
| `mood` | `1` if exact match, else `0` | 2.0 |
| `valence` | `1 - abs(target - value)` | 2.0 |
| `danceability` | `1 - abs(target - value)` | 1.0 |
| `acousticness` | `1 - abs(target - value)` | 1.0 |
| `tempo` | normalize BPM to 0-1, then `1 - abs(target - value)` | 1.0 |

**Step 2: Combine (Scoring Rule, one song)**

```
total = Σ (weight_i × feature_score_i)
final_score = total / Σ (weight_i)      # keeps the result in 0-1
```

**Step 3: Rank (Ranking Rule, the list)**

1. Score every song against the user profile.
2. Sort by `final_score`, highest first.
3. Return the top N (e.g. top 5) as the recommendations.

Design choices baked into the recipe:

- Numeric features reward **closeness**, not high/low values (`1 - abs(diff)`).
- `tempo_bpm` is **normalized before scoring** so its large raw range doesn't
  dominate the other 0-1 features.
- **Energy is weighted highest (3.0)** because it mirrors how people actually
  pick music, they reach for a vibe first ("something chill", "something
  hype") and will cross genres freely when the feeling fits.
- **Genre and mood are strong signals (2.0), not hard gates.** Genre still
  matters (people have go-to styles) but it no longer overrides a song that
  nails the energy and mood, so cross-genre discovery can surface. `mood` is
  raised to 2.0 alongside `valence` because emotional fit matters as much as
  style. (An earlier version used genre 3.0 / energy 2.0 / mood 1.0; see
  **Experiments You Tried** for why it was retuned.)

### Potential Biases I Expect

- **Genre over-prioritization.** Because genre carries the largest weight, the
  system may over-favor same-genre songs and overlook a different-genre track
  that perfectly matches the user's mood, energy, and tempo.
- **Popularity/label bias in the data.** Genre and mood are human labels; if the
  catalog labels certain styles inconsistently, those songs are unfairly
  penalized on the categorical checks regardless of how well they actually fit.
- **"Mellow cluster" bias.** A chill profile scores all low-energy, high-acoustic
  songs highly, so mellow songs cluster at the top and more energetic-but-still-
  relevant songs are systematically pushed down.
- **Single-taste assumption.** One point-target profile can't represent a user
  who likes two different vibes (e.g. workout + study music), so it will always
  recommend toward one "average" taste and ignore the other.
- **No cultural/lyrical understanding.** The system scores only audio-style
  numbers, so it can't tell that a musically upbeat song has sad lyrics, or
  account for language. That is a real fairness gap in who gets recommended.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Produced by running `python -m src.main` against the 19-song catalog. Six
profiles are evaluated: three realistic listeners and three **adversarial /
edge-case** profiles designed to try to "trick" the scoring logic.

### Profile 1: High-Energy Pop (realistic)

```
============================================================
  PROFILE: High-Energy Pop
  pop / intense  |  energy target 0.9
============================================================

  1. Gym Hero  -  Max Pulse
     Score: 0.98   [pop / intense]
     Reasons:
       - genre match: pop (+2.0)
       - mood match: intense (+2.0)
       - energy close (0.93 vs 0.90) (+2.91)
       - valence close (0.77 vs 0.80) (+1.94)
       - danceability close (0.88 vs 0.85) (+0.97)
       - acousticness close (0.05 vs 0.05) (+1.00)
       - tempo close (0.60 vs 0.58) (+0.98)

  2. Sunrise City  -  Neon Echo
     Score: 0.78   [pop / happy]
     Reasons:
       - genre match: pop (+2.0)
       - energy close (0.82 vs 0.90) (+2.76)
       - valence close (0.84 vs 0.80) (+1.92)
       - danceability close (0.79 vs 0.85) (+0.94)
       - acousticness close (0.18 vs 0.05) (+0.87)
       - tempo close (0.48 vs 0.58) (+0.90)

  3. Storm Runner  -  Voltline
     Score: 0.74   [rock / intense]
     Reasons:
       - mood match: intense (+2.0)
       - energy close (0.91 vs 0.90) (+2.97)
       - valence close (0.48 vs 0.80) (+1.36)
       - danceability close (0.66 vs 0.85) (+0.81)
       - acousticness close (0.10 vs 0.05) (+0.95)
       - tempo close (0.77 vs 0.58) (+0.82)

  4. Neon Overdrive  -  Pixel Rush
     Score: 0.63   [edm / euphoric]
     Reasons:
       - energy close (0.95 vs 0.90) (+2.85)
       - valence close (0.88 vs 0.80) (+1.84)
       - danceability close (0.91 vs 0.85) (+0.94)
       - acousticness close (0.04 vs 0.05) (+0.99)
       - tempo close (0.57 vs 0.58) (+0.98)

  5. Rooftop Lights  -  Indigo Parade
     Score: 0.60   [indie pop / happy]
     Reasons:
       - energy close (0.76 vs 0.90) (+2.58)
       - valence close (0.81 vs 0.80) (+1.98)
       - danceability close (0.82 vs 0.85) (+0.97)
       - acousticness close (0.35 vs 0.05) (+0.70)
       - tempo close (0.53 vs 0.58) (+0.95)

============================================================
```

### Profile 2: Chill Lofi (realistic)

```
============================================================
  PROFILE: Chill Lofi
  lofi / chill  |  energy target 0.35
============================================================

  1. Library Rain  -  Paper Lanterns
     Score: 0.99   [lofi / chill]
     Reasons:
       - genre match: lofi (+2.0)
       - mood match: chill (+2.0)
       - energy close (0.35 vs 0.35) (+3.00)
       - valence close (0.60 vs 0.60) (+2.00)
       - danceability close (0.58 vs 0.55) (+0.97)
       - acousticness close (0.86 vs 0.85) (+0.99)
       - tempo close (0.10 vs 0.15) (+0.95)

  2. Midnight Coding  -  LoRoom
     Score: 0.96   [lofi / chill]
     Reasons:
       - genre match: lofi (+2.0)
       - mood match: chill (+2.0)
       - energy close (0.42 vs 0.35) (+2.79)
       - valence close (0.56 vs 0.60) (+1.92)
       - danceability close (0.62 vs 0.55) (+0.93)
       - acousticness close (0.71 vs 0.85) (+0.86)
       - tempo close (0.15 vs 0.15) (+1.00)

  3. Focus Flow  -  LoRoom
     Score: 0.81   [lofi / focused]
     Reasons:
       - genre match: lofi (+2.0)
       - energy close (0.40 vs 0.35) (+2.85)
       - valence close (0.59 vs 0.60) (+1.98)
       - danceability close (0.60 vs 0.55) (+0.95)
       - acousticness close (0.78 vs 0.85) (+0.93)
       - tempo close (0.17 vs 0.15) (+0.98)

  4. Spacewalk Thoughts  -  Orbit Bloom
     Score: 0.78   [ambient / chill]
     Reasons:
       - mood match: chill (+2.0)
       - energy close (0.28 vs 0.35) (+2.79)
       - valence close (0.65 vs 0.60) (+1.90)
       - danceability close (0.41 vs 0.55) (+0.86)
       - acousticness close (0.92 vs 0.85) (+0.93)
       - tempo close (0.00 vs 0.15) (+0.85)

  5. Coffee Shop Stories  -  Slow Stereo
     Score: 0.63   [jazz / relaxed]
     Reasons:
       - energy close (0.37 vs 0.35) (+2.94)
       - valence close (0.71 vs 0.60) (+1.78)
       - danceability close (0.54 vs 0.55) (+0.99)
       - acousticness close (0.89 vs 0.85) (+0.96)
       - tempo close (0.25 vs 0.15) (+0.90)

============================================================
```

### Profile 3: Deep Intense Rock (realistic)

```
============================================================
  PROFILE: Deep Intense Rock
  rock / intense  |  energy target 0.9
============================================================

  1. Storm Runner  -  Voltline
     Score: 0.99   [rock / intense]
     Reasons:
       - genre match: rock (+2.0)
       - mood match: intense (+2.0)
       - energy close (0.91 vs 0.90) (+2.97)
       - valence close (0.48 vs 0.45) (+1.94)
       - danceability close (0.66 vs 0.60) (+0.94)
       - acousticness close (0.10 vs 0.10) (+1.00)
       - tempo close (0.77 vs 0.75) (+0.98)

  2. Gym Hero  -  Max Pulse
     Score: 0.73   [pop / intense]
     Reasons:
       - mood match: intense (+2.0)
       - energy close (0.93 vs 0.90) (+2.91)
       - valence close (0.77 vs 0.45) (+1.36)
       - danceability close (0.88 vs 0.60) (+0.72)
       - acousticness close (0.05 vs 0.10) (+0.95)
       - tempo close (0.60 vs 0.75) (+0.85)

  3. Deep Current  -  Bass Theory
     Score: 0.63   [drum and bass / restless]
     Reasons:
       - energy close (0.88 vs 0.90) (+2.94)
       - valence close (0.45 vs 0.45) (+2.00)
       - danceability close (0.80 vs 0.60) (+0.80)
       - acousticness close (0.07 vs 0.10) (+0.97)
       - tempo close (0.95 vs 0.75) (+0.80)

  4. Iron Requiem  -  Ashfall
     Score: 0.59   [metal / aggressive]
     Reasons:
       - energy close (0.97 vs 0.90) (+2.79)
       - valence close (0.28 vs 0.45) (+1.66)
       - danceability close (0.44 vs 0.60) (+0.84)
       - acousticness close (0.06 vs 0.10) (+0.96)
       - tempo close (0.90 vs 0.75) (+0.85)

  5. Night Drive Loop  -  Neon Echo
     Score: 0.57   [synthwave / moody]
     Reasons:
       - energy close (0.75 vs 0.90) (+2.55)
       - valence close (0.49 vs 0.45) (+1.92)
       - danceability close (0.73 vs 0.60) (+0.87)
       - acousticness close (0.22 vs 0.10) (+0.88)
       - tempo close (0.42 vs 0.75) (+0.67)

============================================================
```

---

## Adversarial / Edge-Case Evaluation

I asked for profiles designed to "trick" the scoring logic. Below are the
three most interesting ones and what each revealed.

### Profile 4: Conflicting signals ("Sad but High-Energy")

Wants `melancholy` mood + `folk` genre, but also `energy 0.95`, `danceability
0.90`, and a slow `70 BPM`, signals that contradict each other. No real song
can be both a slow sad folk track and maximally energetic/danceable.

```
============================================================
  PROFILE: ADVERSARIAL: Sad but High-Energy
  folk / melancholy  |  energy target 0.95
============================================================

  1. Paper Boats  -  Willow Grey
     Score: 0.74   [folk / melancholy]
     Reasons:
       - genre match: folk (+2.0)
       - mood match: melancholy (+2.0)
       - energy close (0.30 vs 0.95) (+1.05)
       - valence close (0.34 vs 0.10) (+1.52)
       - danceability close (0.40 vs 0.90) (+0.50)
       - acousticness close (0.88 vs 0.90) (+0.98)
       - tempo close (0.20 vs 0.08) (+0.88)

  2. Iron Requiem  -  Ashfall
     Score: 0.46   [metal / aggressive]
     Reasons:
       - energy close (0.97 vs 0.95) (+2.94)
       - valence close (0.28 vs 0.10) (+1.64)
       - danceability close (0.44 vs 0.90) (+0.54)
       - acousticness close (0.06 vs 0.90) (+0.16)
       - tempo close (0.90 vs 0.08) (+0.18)

  3. Concrete Kings  -  Big Verse
     Score: 0.45   [hip-hop / confident]
     Reasons:
       - energy close (0.80 vs 0.95) (+2.55)
       - valence close (0.62 vs 0.10) (+0.96)
       - danceability close (0.85 vs 0.90) (+0.95)
       - acousticness close (0.09 vs 0.90) (+0.19)
       - tempo close (0.29 vs 0.08) (+0.79)

  4. Night Drive Loop  -  Neon Echo
     Score: 0.45   [synthwave / moody]
     Reasons:
       - energy close (0.75 vs 0.95) (+2.40)
       - valence close (0.49 vs 0.10) (+1.22)
       - danceability close (0.73 vs 0.90) (+0.83)
       - acousticness close (0.22 vs 0.90) (+0.32)
       - tempo close (0.42 vs 0.08) (+0.67)

  5. Storm Runner  -  Voltline
     Score: 0.45   [rock / intense]
     Reasons:
       - energy close (0.91 vs 0.95) (+2.88)
       - valence close (0.48 vs 0.10) (+1.24)
       - danceability close (0.66 vs 0.90) (+0.76)
       - acousticness close (0.10 vs 0.90) (+0.20)
       - tempo close (0.77 vs 0.08) (+0.32)
```

**What it revealed:** The genre+mood match (+4.0) dominates the conflicting
numeric penalties, so the top pick (0.74) is still the "correct" sad folk song
even though it scores poorly on energy and danceability. Below it, the ranking
collapses into a near-tie around 0.45-0.46. The logic can't satisfy the
contradiction, so nothing else scores well. This exposes that **categorical
matches can override strong numeric disagreement**.

### Profile 5: Genre & mood not in the catalog

Uses `genre: k-pop` and `mood: hyped`, neither of which exists in the data,
so the +3.0 and +1.0 category bonuses can **never** fire for any song.

```
============================================================
  PROFILE: ADVERSARIAL: Genre/Mood Not In Catalog
  k-pop / hyped  |  energy target 0.6
============================================================

  1. Dust and Diesel  -  Cody Lane
     Score: 0.64   [country / nostalgic]
     Reasons:
       - energy close (0.55 vs 0.60) (+2.85)
       - valence close (0.60 vs 0.60) (+2.00)
       - danceability close (0.58 vs 0.60) (+0.98)
       - acousticness close (0.55 vs 0.40) (+0.85)
       - tempo close (0.40 vs 0.42) (+0.98)

  2. Island Time  -  Sunny Coast
     Score: 0.61   [reggae / carefree]
     Reasons:
       - energy close (0.58 vs 0.60) (+2.94)
       - valence close (0.79 vs 0.60) (+1.62)
       - danceability close (0.76 vs 0.60) (+0.84)
       - acousticness close (0.42 vs 0.40) (+0.98)
       - tempo close (0.30 vs 0.42) (+0.88)

  3. Velvet Hours  -  Mara Soul
     Score: 0.59   [r&b / sensual]
     Reasons:
       - energy close (0.52 vs 0.60) (+2.76)
       - valence close (0.66 vs 0.60) (+1.88)
       - danceability close (0.70 vs 0.60) (+0.90)
       - acousticness close (0.30 vs 0.40) (+0.90)
       - tempo close (0.10 vs 0.42) (+0.68)

  4. Night Drive Loop  -  Neon Echo
     Score: 0.59   [synthwave / moody]
     Reasons:
       - energy close (0.75 vs 0.60) (+2.55)
       - valence close (0.49 vs 0.60) (+1.78)
       - danceability close (0.73 vs 0.60) (+0.87)
       - acousticness close (0.22 vs 0.40) (+0.82)
       - tempo close (0.42 vs 0.42) (+1.00)

  5. Midnight Coding  -  LoRoom
     Score: 0.57   [lofi / chill]
     Reasons:
       - energy close (0.42 vs 0.60) (+2.46)
       - valence close (0.56 vs 0.60) (+1.92)
       - danceability close (0.62 vs 0.60) (+0.98)
       - acousticness close (0.71 vs 0.40) (+0.69)
       - tempo close (0.15 vs 0.42) (+0.73)
```

**What it revealed:** The system **degrades gracefully**. With no possible
category match, it falls back to pure numeric closeness and still returns a
sensible mid-energy list. But note the ceiling: no song can exceed ~0.64
because 4 of the 12 available points (genre 2 + mood 2) are unreachable. The
scores are honest, just capped.

### Profile 6: Impossible extremes

Every numeric target is pushed to an unreachable extreme (`energy 1.0`,
`valence 0.0`, `danceability 1.0`, `acousticness 0.0`, `tempo 200`).

```
============================================================
  PROFILE: ADVERSARIAL: Impossible Extremes
  metal / aggressive  |  energy target 1.0
============================================================

  1. Iron Requiem  -  Ashfall
     Score: 0.89   [metal / aggressive]
     Reasons:
       - genre match: metal (+2.0)
       - mood match: aggressive (+2.0)
       - energy close (0.97 vs 1.00) (+2.91)
       - valence close (0.28 vs 0.00) (+1.44)
       - danceability close (0.44 vs 1.00) (+0.44)
       - acousticness close (0.06 vs 0.00) (+0.94)
       - tempo close (0.90 vs 1.00) (+0.90)

  2. Deep Current  -  Bass Theory
     Score: 0.54   [drum and bass / restless]
     Reasons:
       - energy close (0.88 vs 1.00) (+2.64)
       - valence close (0.45 vs 0.00) (+1.10)
       - danceability close (0.80 vs 1.00) (+0.80)
       - acousticness close (0.07 vs 0.00) (+0.93)
       - tempo close (0.95 vs 1.00) (+0.95)

  3. Storm Runner  -  Voltline
     Score: 0.51   [rock / intense]
     Reasons:
       - energy close (0.91 vs 1.00) (+2.73)
       - valence close (0.48 vs 0.00) (+1.04)
       - danceability close (0.66 vs 1.00) (+0.66)
       - acousticness close (0.10 vs 0.00) (+0.90)
       - tempo close (0.77 vs 1.00) (+0.77)

  4. Gym Hero  -  Max Pulse
     Score: 0.47   [pop / intense]
     Reasons:
       - energy close (0.93 vs 1.00) (+2.79)
       - valence close (0.77 vs 0.00) (+0.46)
       - danceability close (0.88 vs 1.00) (+0.88)
       - acousticness close (0.05 vs 0.00) (+0.95)
       - tempo close (0.60 vs 1.00) (+0.60)

  5. Neon Overdrive  -  Pixel Rush
     Score: 0.46   [edm / euphoric]
     Reasons:
       - energy close (0.95 vs 1.00) (+2.85)
       - valence close (0.88 vs 0.00) (+0.24)
       - danceability close (0.91 vs 1.00) (+0.91)
       - acousticness close (0.04 vs 0.00) (+0.96)
       - tempo close (0.57 vs 1.00) (+0.57)
```

**What it revealed:** Scores stay **safely bounded in 0-1** and never go
negative even with impossible targets. The `1 - abs(diff)` formula and the
normalization hold up. The genre+mood match again does the heavy lifting for
#1 (0.89), while everything else lands below 0.55 because no song can be
maximally energetic and zero-valence and maximally danceable at once.

**Screenshot or video** (optional): <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

### Experiment: Weight Shift (energy up, genre down)

**Original weights:** `genre 3.0, energy 2.0, valence 2.0, mood 1.0`, others 1.0.

To test how sensitive the rankings were to my weights, and whether genre was
over-dominating, I ran a weight-shift experiment: I **doubled energy (2.0 to 4.0)** and **halved genre (3.0 to 1.5)**, leaving everything else the same. The
math stayed valid because the final score is `total / sum(weights)`, and the
denominator simply recalculated (11.0 to 11.5), so scores stayed in 0-1.

**What happened:**

- The **#1 pick never changed** in any of the six profiles. The top song
  always matched genre and had near-exact energy, so it won under either
  weighting.
- The **tail of every list rose and compressed.** Cross-genre songs that were
  buried before became genuine contenders. For the High-Energy Pop profile,
  the rock track Storm Runner climbed from 0.63 to 0.77 and the edm track Neon
  Overdrive climbed from 0.60 to 0.74, nearly catching the pop songs.

**Conclusion: more accurate, not just different.** Making energy matter more
than a strict genre label better reflects how people actually listen (they
chase a vibe and cross genres freely). The obvious top picks were unharmed
while genuinely-fitting cross-genre songs stopped being penalized.

### Final retune

The pure experiment (energy 4.0) made energy too dominant and left `mood` at
only 1.0, so I settled on a balanced version that keeps the discovery benefit:

| | Original | Experiment | **Final (shipped)** |
|---|---|---|---|
| energy | 2.0 | 4.0 | **3.0** |
| genre | 3.0 | 1.5 | **2.0** |
| mood | 1.0 | 1.0 | **2.0** |
| valence | 2.0 | 2.0 | **2.0** |
| others | 1.0 | 1.0 | **1.0** |

Energy leads (vibe first), genre and mood are strong signals rather than hard
gates, and emotional fit (`mood` + `valence`) is weighted evenly with style.
All six profiles still return a distinct, intuitive #1, and the sample output
above was regenerated with these final weights.

### Other observations

- **No single song dominates.** Across all six profiles the #1 results are six
  different songs, so the weighting isn't stuck and the 19-song catalog has
  enough variety to respond to different tastes.

---

## Limitations and Risks

- **Tiny catalog.** With only 19 songs (and often just one per genre), there
  isn't much variety, and niche tastes get very few real options.
- **The "energy gap" favors average songs.** Because energy is the highest
  weight and the closeness score is linear, mid-energy songs match almost
  everyone, while listeners with very high or very low energy tastes are
  under-served. (See the model card for the full write-up.)
- **Exact-match only for genre and mood.** A request for "hip-hop" gets zero
  points from a "rap" song, so anyone whose words don't match the catalog
  labels is penalized.
- **No understanding of lyrics, language, era, or artist popularity.** It only
  scores audio-style numbers, so it can't tell an upbeat song has sad lyrics.
- **Single-taste assumption.** One profile can only capture one vibe, so it
  can't represent someone who likes, say, both workout and study music.

I go deeper on these in the [model card](model_card.md#6-limitations-and-bias).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

This project made recommenders feel less mysterious. My "prediction" is really
just a score I calculate for every song based on how close it is to what the
user asked for, followed by a sort. There is no machine learning involved, yet
the ranked list still feels like it understands the user's taste, which showed
me that a lot of what feels "smart" in real apps may come from fairly simple
rules applied to a lot of data.

It also made clear how easily bias slips in. My exact-match rule gives a song
zero points unless its genre or mood label matches exactly, so listeners whose
words don't line up with the catalog are quietly left out. The dataset is uneven
too, a few genres and moods appear far more often than others, so some users
get better results just because of what happens to be in the file. The unfairness
isn't intentional; it's baked into the scoring rules and the data.

(A fuller reflection is in the [model card](model_card.md#9-personal-reflection).)



