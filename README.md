# DJ Track Finder

🇬🇧 [English](#english) | 🇷🇴 [Română](#română)

---

## English

I got tired of every online mix-identifier site capping file size or mix length unless you pay, so I built this instead. You give it a DJ mix (any length, doesn't matter), it chops it into pieces, runs each piece through Shazam, and spits out a tracklist. Runs locally, no upload limits, no subscription.

**What it actually does:**

Drop in an mp3/wav/flac/m4a, hit start. It splits the file into ~90 second chunks, sends each one to Shazam (using `shazamio`, an unofficial free wrapper, no API key nonsense), and builds a tracklist as it goes. Results save themselves to `output/` after every track found, so if you close the app halfway through a 2-hour set, you still keep whatever it already found.

**Running it:**

You'll need Python 3.10+ and ffmpeg (`winget install ffmpeg` if you're on Windows and don't have it).

```bash
pip install -r requirements.txt
python main.py
```

**What's in here:**

- `main.py`: the actual app / UI
- `analyzer.py`: splits the audio into chunks
- `recognizer.py`: talks to Shazam
- `exporter.py`: writes the .txt / .csv

**Heads up:**

90-second chunks keep things fast, but if your mix has really quick transitions (under a minute), it can miss a track here and there. Drop `chunk_seconds` in `analyzer.py` if you'd rather trade speed for accuracy. Also, since this hits Shazam's unofficial API, don't be shocked if it slows down or throws a hiccup if you hammer it with back-to-back long mixes.

Built with a lot of help from Claude. I steered, tested on my own mixes, and yelled at it when things broke, but a good chunk of the code came out of that back-and-forth. Figured I'd say that upfront instead of pretending otherwise.

No license attached, do whatever you want with it.

- The .exe version doesn't output a .txt/.csv file.

---

## Română

M-am săturat să caut prin site-uri care recunosc piese din mixuri și toate aveau vreo limită: fie la mărimea fișierului, fie la durată, fie trebuia să plătești după 2 încercări. Așa că mi-am făcut unul. Bagi un mix (orice lungime), îl taie în bucăți, trece fiecare bucată prin Shazam, și-ți dă tracklist-ul. Rulează local pe calculatorul tău, fără limite, fără abonament.

**Ce face mai exact:**

Alegi un mp3/wav/flac/m4a, apeși start. Taie fișierul în fragmente de ~90 secunde, trimite fiecare fragment la Shazam (prin `shazamio`, o bibliotecă neoficială gratuită, fără cheie API), și construiește tracklist-ul pe măsură ce găsește piese. Salvează automat în `output/` după fiecare piesă găsită, deci dacă închizi aplicația la jumătatea unui mix de 2 ore, tot rămâi cu ce a apucat să găsească.

**Cum îl rulezi:**

Ai nevoie de Python 3.10+ și ffmpeg (`winget install ffmpeg` dacă ești pe Windows și nu-l ai).

```bash
pip install -r requirements.txt
python main.py
```

**Ce conține:**

- `main.py`: aplicația / interfața
- `analyzer.py`: taie audio-ul în fragmente
- `recognizer.py`: vorbește cu Shazam
- `exporter.py`: scrie .txt / .csv

**De reținut:**

Fragmentele de 90 secunde țin lucrurile rapide, dar dacă mixul tău are tranziții foarte rapide (sub un minut), poate rata câte o piesă pe ici pe colo. Poți scădea `chunk_seconds` din `analyzer.py` dacă preferi acuratețe în locul vitezei. Și pentru că folosește API-ul neoficial al Shazam, nu te mira dacă se mai poticnește dacă îl bombardezi cu mixuri lungi, una după alta. 

Făcut cu mult ajutor de la Claude. Eu am condus treaba, am testat pe mixurile mele, m-am enervat pe el când s-a stricat ceva, dar o bună parte din cod a ieșit din tot du-te-vino-ul ăsta. Am zis să spun direct, nu să mă prefac altfel.

Fără licență, fă ce vrei cu el.

- Versiunea .exe nu iti da .txt/.csv
