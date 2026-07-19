# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**SoundMatch**

A song recommender that matches music to your mood and taste.

---

## 2. Intended Use

SoundMatch suggests songs that fit a listener's stated taste.

- It generates a ranked list of the top songs from a small catalog.
- It assumes the user can describe what they like: a favorite genre, a favorite mood, and target values for things like energy, valence, danceability, acousticness, and tempo.
- This is built for classroom exploration, not for real users. It is a learning project, not a production music app.

**What it should NOT be used for:**

- Real music apps or real customers. The catalog is tiny (19 songs) and the results are not tested for quality.
- Judging songs, artists, or genres as "good" or "bad." A low score just means a song did not match one profile.
- Any decision that matters to a person's life, like hiring, grades, or money. It only ranks songs.
- Discovering brand-new music. It can only pick from the songs already in the file.

---

## 3. How the Model Works

SoundMatch gives every song a score, then picks the highest-scoring ones.

- It looks at each song's **genre**, **mood**, **energy**, **valence** (how happy/positive it sounds), **danceability**, **acousticness**, and **tempo** (BPM).
- It compares those to what the user says they want.
- Some features earn points a different way:
  - **Genre** and **mood** are all-or-nothing. An exact match earns full points, otherwise zero.
  - The number features (energy, valence, danceability, acousticness, tempo) earn points based on how close the song is to what the user wants. Closer means more points.
- Energy is weighted the highest (3 points) because people usually pick music by vibe first. Genre, mood, and valence are next (2 points each). Danceability, acousticness, and tempo are worth 1 point each.
- Tempo is measured in beats per minute, which is a much bigger number than the other features. So it is squished onto a 0-to-1 scale first, so it doesn't overpower everything else.
- All the points are added up and divided by the maximum possible, so every score lands between 0 and 1. That makes scores easy to compare.
- Each recommendation also comes with plain-language **reasons**, like "genre match: lofi (+2.0)", so you can see why a song was picked.

**Change from the starter logic:** The starter just returned the first few songs with no real scoring. I built the actual weighted scoring rule, the closeness math for number features, tempo normalization, and the reasons/explanations.

---

## 4. Data

The catalog is a small CSV file of songs.

- There are **19 songs** in the catalog.
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

**Key weakness found during my experiments: the "energy gap" creates a
filter bubble around average songs.** Because energy is my highest-weighted
feature (3.0) and its score is a simple linear gap, `1 - abs(target - energy)`,
a mid-energy song (around 0.5) is never more than 0.5 away from any user's
target, so it collects a guaranteed baseline of points from everybody. The
listeners who lose are the ones with extreme taste: when I ran my "Impossible
Extremes" profile (target energy 1.0) the most energetic track still couldn't
reach a top score because no song is a perfect 1.0, and a hypothetical
"total-calm" user (target 0.0) can do no better than the lowest-energy song in
the data (0.28). This means moderate, middle-of-the-road songs surface for
almost everyone while niche high- or low-energy listeners are systematically
under-served. The dataset makes it worse: the catalog is clustered in the
0.3-0.95 energy band with lofi and chill over-represented (3 of 19 songs each),
so the "average" song the formula rewards is also the kind the data has most of.

Other, smaller limitations:

- **Features it ignores:** lyrics, language, year, and artist popularity are never considered.
- **Underrepresented styles:** with only about one song per genre, niche genres barely stand a chance unless the user names them exactly.
- **Sparse mood matches:** 16 of the 19 songs have a unique mood, so the mood bonus is effectively unwinnable unless the user picks one of the few repeated moods (chill, happy, intense).
- **Exact-match unfairness:** genre and mood only reward exact text matches. A user who wants "hip-hop" gets nothing for a very similar "rap" song, so people whose taste doesn't use the exact catalog labels are penalized.
- **Overfitting to one preference:** if a user's energy and valence targets happen to line up with one song, that single song can win by a large margin.

---

## 7. Evaluation

### Profiles I tested

I ran the recommender against **six** user profiles (all built into `main.py`):

- **Three realistic listeners:** High-Energy Pop (pop / intense, energy 0.90),
  Chill Lofi (lofi / chill, energy 0.35), and Deep Intense Rock
  (rock / intense, energy 0.90).
- **Three adversarial / edge-case profiles** to try to trick the logic:
  Sad but High-Energy (conflicting wishes), Genre/Mood Not In Catalog
  (asks for a genre and mood no song has), and Impossible Extremes (every
  target pushed to an unreachable 0 or 1).

For each one I checked whether the **top pick actually matched the requested
genre and mood**, whether the ranked list "felt" right, and whether the
plain-language reasons made sense.

### What surprised me

- A few songs are **"crossover magnets"** that show up for very different
  listeners. Gym Hero is the top pick for the Pop fan **and** the #2 pick for
  the Rock fan, because it is both high-energy and tagged "intense". Those are
  two things both profiles want.
- The recommender **degrades gracefully** for the impossible profiles: even
  when no genre or mood can match, it still returns a sensible list ranked
  purely on how close the numbers are, and every score stays between 0 and 1.
- Chill/ambient/jazz songs cluster together because their energy and
  acousticness are similar. Genre weight is the main thing separating them.

### Comparing the profiles (what changed, and why it makes sense)

- **High-Energy Pop vs. Chill Lofi:** These are near opposites, and the output
  shows it. The Pop list is full of loud, fast, danceable tracks (Gym Hero,
  Sunrise City), while the Lofi list is full of quiet, slow, acoustic tracks
  (Library Rain, Midnight Coding). This makes sense: the two profiles ask for
  opposite energy (0.90 vs 0.35) and opposite acousticness, so almost no song
  scores well for both.
- **High-Energy Pop vs. Deep Intense Rock:** These two overlap. Both want
  high energy and an "intense" feel, which is exactly why Gym Hero and
  Storm Runner each appear in both top lists. The difference is emotional
  tone: the Rock profile wants a darker sound (lower valence), so gloomier
  tracks like Iron Requiem and Deep Current rise for the Rock fan but not
  the Pop fan, who wants brighter, happier songs.
- **Chill Lofi vs. Deep Intense Rock:** The most extreme contrast. One wants
  calm, slow, acoustic music and the other wants loud, fast, aggressive music,
  so the two lists share **no songs at all**. That is the correct result for tastes
  this far apart.
- **Realistic vs. adversarial profiles:** The realistic profiles reach very
  high top scores (~0.98-0.99) because a real taste lines up genre + mood +
  numbers all at once. The adversarial profiles top out much lower (~0.64-0.74)
  because their wishes contradict each other or can't be matched, which is
  exactly what a trustworthy scorer should do: refuse to fake a perfect
  match that doesn't exist.

### Explaining it to a non-programmer

Why does **"Gym Hero" keep showing up for people who just want "Happy Pop"?**
Think of every song as having a few dials: how energetic it is, how danceable,
how happy it sounds, and what style it is. "Gym Hero" has its energy and dance
dials turned almost all the way up, and it's labeled pop. So when someone asks
for upbeat, happy pop, the app looks at all the songs, sees that Gym Hero's
dials are the closest to what they asked for, and puts it first. It even sneaks
into the rock fan's list, because "high energy + intense" is something both
kinds of listeners are reaching for, so the song sits right in the overlap
between them.

### Automated tests

I also ran the included **pytest tests**, which check that recommendations come
back sorted by score and that explanations are non-empty strings. (Note: those
tests target the OOP `Recommender` class, which is still a stub, so the working
logic lives in the `recommend_songs` function.) No numeric accuracy metrics
were created; evaluation was by inspecting the ranked lists.

---

## 8. Future Work

- **Smarter matching for text features:** treat similar genres/moods as partial matches instead of exact-only, so "rap" can match "hip-hop".
- **More data:** add many more songs per genre so results have real variety and diversity.
- **Diversity in the top results:** avoid returning five nearly identical songs; mix in some variety so the list isn't repetitive.
- **Handle more complex tastes:** let users list more than one favorite genre or mood, or weight their own preferences.
- **Finish the OOP version:** implement the `Recommender` class so the code and the tests use the same scoring logic.

---

## 9. Personal Reflection

**My biggest learning moment** was the weight experiment. When I doubled the
energy weight and halved the genre weight, the #1 song for each profile barely
changed, but the whole bottom of the list shifted and cross-genre songs
suddenly became real options. That taught me that a recommender is really just
a scoring rule plus a sort, there is no magic, and that the "weights" are
where all the important decisions actually live. A tiny number change quietly
decides who gets recommended what.

**Using AI tools** helped me move fast: it helped me draft the scoring math,
build the six test profiles (including the tricky "adversarial" ones), and
explain my results in plain language. But I learned I had to **double-check
it**, not just trust it. I checked the actual terminal output against every
score it described, and I caught places where my documentation had gone stale , 
for example, the model card still said "genre is weighted highest" and "18
songs" after I had already changed the weights and grown the catalog to 19. The
AI was great for speed and ideas, but I was the one who had to make sure the
words matched what the code really did.

**What surprised me** was how a very simple algorithm can still "feel" like a
real recommendation. There is no machine learning here, it just measures how
close each song is to what you asked for and sorts the list. Yet the results
feel personal, like the app "gets" you. That made me realize a lot of what
feels smart in real apps might be simpler than it looks, and also how easy it
is to accidentally build bias in, like the exact-match rule quietly punishing
anyone whose words don't match the catalog.

**If I extended this project**, I would first add many more songs per genre so
the results have real variety instead of the same few tracks. Next I would make
genre and mood matching "fuzzy," so a request for "hip-hop" could still match a
"rap" song instead of scoring zero. Finally I would let a user give more than
one favorite vibe (like "workout" and "study" music), since right now a single
profile can only capture one taste at a time. Now when I use a real music app, I
think about what features it might be scoring on and what it is probably
ignoring.
