# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

A song recommender that matches music to your mood and taste.

---

## 2. Intended Use

VibeMatch suggests songs that fit a listener's stated taste.

- It generates a ranked list of the top songs from a small catalog.
- It assumes the user can describe what they like: a favorite genre, a favorite mood, and target values for things like energy, valence, danceability, acousticness, and tempo.
- This is built for classroom exploration, not for real users. It is a learning project, not a production music app.

---

## 3. How the Model Works

VibeMatch gives every song a score, then picks the highest-scoring ones.

- It looks at each song's **genre**, **mood**, **energy**, **valence** (how happy/positive it sounds), **danceability**, **acousticness**, and **tempo** (BPM).
- It compares those to what the user says they want.
- Some features earn points a different way:
  - **Genre** and **mood** are all-or-nothing. An exact match earns full points, otherwise zero.
  - The number features (energy, valence, danceability, acousticness, tempo) earn points based on how *close* the song is to what the user wants. Closer means more points.
- Genre is weighted the highest (3 points) so the recommender does not jump between very different styles. Energy and valence are next (2 points each). Mood, danceability, acousticness, and tempo are worth 1 point each.
- Tempo is measured in beats per minute, which is a much bigger number than the other features. So it is squished onto a 0-to-1 scale first, so it doesn't overpower everything else.
- All the points are added up and divided by the maximum possible, so every score lands between 0 and 1. That makes scores easy to compare.
- Each recommendation also comes with plain-language **reasons**, like "genre match: lofi (+3.0)", so you can see why a song was picked.

**Change from the starter logic:** The starter just returned the first few songs with no real scoring. I built the actual weighted scoring rule, the closeness math for number features, tempo normalization, and the reasons/explanations.

---

## 4. Data

The catalog is a small CSV file of songs.

- There are **18 songs** in the catalog.
- Each song has 9 pieces of info: title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.
- Lots of genres are represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, folk, edm, classical, metal, reggae, r&b, country, and drum and bass.
- Moods range from chill and happy to intense, moody, aggressive, and romantic.
- I did not add or remove songs; I used the starter catalog.
- **What's missing:** Only one or two songs per genre, so there isn't much variety within a style. There is also no info on lyrics, language, era/year, or artist popularity.

---

## 5. Strengths

- It works well for listeners with a **clear, consistent taste**, like a "chill lofi" fan whose energy and acousticness targets also point toward lofi songs. The genre match and the number features agree, so the right songs rise to the top.
- The scoring correctly captures **closeness**: a song that is almost the right energy still gets rewarded, instead of being treated as totally wrong.
- The **reasons** feature matches intuition. When I read why a song was picked, the explanation usually made sense.

---

## 6. Limitations and Bias

- **Features it ignores:** lyrics, language, year, and artist popularity are never considered.
- **Underrepresented styles:** with only about one song per genre, niche genres barely stand a chance unless the user names them exactly.
- **Genre can dominate:** because genre is worth the most points, a user who picks a genre may get pushed toward it even if the mood or energy of those songs doesn't really fit.
- **Exact-match unfairness:** genre and mood only reward *exact* text matches. A user who wants "hip-hop" gets nothing for a very similar "rap" song, so people whose taste doesn't use the exact catalog labels are penalized.
- **Overfitting to one preference:** if a user's energy and valence targets happen to line up with one song, that single song can win by a large margin.

---

## 7. Evaluation

- I tested the **"chill lofi" profile** built into `main.py` (lofi / chill, low energy, high acousticness). The top results were the lofi and ambient chill tracks, which is what I expected.
- I looked for whether the **top pick actually matched the requested genre and mood**, and whether the reasons made sense.
- **What surprised me:** ambient and jazz "chill/relaxed" songs scored close to lofi songs, because their energy and acousticness were similar. The genre weight was the main thing keeping lofi on top.
- I also ran the included **pytest tests**, which check that recommendations come back sorted by score and that explanations are non-empty strings. (Note: those tests target the OOP `Recommender` class, which is still a stub, so the working logic lives in the `recommend_songs` function.)
- No numeric metrics were created; evaluation was by inspecting the ranked lists.

---

## 8. Future Work

- **Smarter matching for text features:** treat similar genres/moods as partial matches instead of exact-only, so "rap" can match "hip-hop".
- **More data:** add many more songs per genre so results have real variety and diversity.
- **Diversity in the top results:** avoid returning five nearly identical songs; mix in some variety so the list isn't repetitive.
- **Handle more complex tastes:** let users list more than one favorite genre or mood, or weight their own preferences.
- **Finish the OOP version:** implement the `Recommender` class so the code and the tests use the same scoring logic.

---

## 9. Personal Reflection

Building this showed me that a recommender is really just a scoring rule plus a sort — there is no magic. The most interesting part was seeing how much the **weights** mattered: changing how many points genre was worth completely changed the results. It also made me realize how easy it is to accidentally build bias into a system, like the exact-match rule quietly punishing anyone whose words don't match the catalog. Now when I use a real music app, I think about what features it might be scoring on and what it's probably ignoring.
