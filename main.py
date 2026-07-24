import customtkinter as ctk
from tkinter import filedialog, Canvas
import threading
import queue
import random
import math

COLOR_BG = "#0a0d0a"
COLOR_CARD = "#141814"
COLOR_CARD_BORDER = "#25302a"
COLOR_ACCENT = "#2d6a4f"
COLOR_ACCENT_HOVER = "#245640"
COLOR_ACCENT2 = "#52796f"
COLOR_TEXT = "#f4f4f5"
COLOR_TEXT_MUTED = "#8a988f"
COLOR_ERROR = "#f87171"
COLOR_ROW_ALT = "#181e19"

FONT_TITLU = ("Segoe UI", 30, "bold")
FONT_SUBTITLU = ("Segoe UI", 13)
FONT_BUTON = ("Segoe UI", 14, "bold")
FONT_LABEL = ("Segoe UI", 12)
FONT_LABEL_MIC = ("Segoe UI", 11)
FONT_TRACK = ("Segoe UI", 13)
FONT_TRACK_INDEX = ("Segoe UI", 12, "bold")

NUM_PARTICULE = 36
RAZA_PARTICULA = 2
RAZA_MOUSE = 130
FORTA_MOUSE = 0.6
VITEZA_MAXIMA = 1.4
DISTANTA_LINIE = 130

TEXTE = {
    "titlu": {"ro": "DJ Track Finder", "en": "DJ Track Finder"},
    "subtitlu": {"ro": "Recunoaște automat piesele din orice mix DJ", "en": "Automatically recognize tracks from any DJ mix"},
    "alege_fisier": {"ro": "Alege fișier", "en": "Choose file"},
    "niciun_fisier": {"ro": "Niciun fișier ales", "en": "No file chosen"},
    "start": {"ro": "START ANALIZĂ", "en": "START ANALYSIS"},
    "procesare": {"ro": "Se procesează...", "en": "Processing..."},
    "astept_fisier": {"ro": "Aștept să alegi un fișier...", "en": "Waiting for a file..."},
    "fisier_selectat": {"ro": "Fișier selectat. Apasă START.", "en": "File selected. Press START."},
    "eroare_fara_fisier": {"ro": "Nu ai ales niciun fișier!", "en": "You haven't chosen a file!"},
    "citesc": {"ro": "Citesc fișierul...", "en": "Reading file..."},
    "impart": {"ro": "Împart fișierul în fragmente...", "en": "Splitting file into chunks..."},
    "incep_recunoasterea": {"ro": "Încep recunoașterea pieselor...", "en": "Starting track recognition..."},
    "recunosc_fragment": {"ro": "Recunosc fragmentul {i}/{n}...", "en": "Recognizing chunk {i}/{n}..."},
    "gata": {"ro": "Gata! {n} piese găsite. Salvate în /output", "en": "Done! {n} tracks found. Saved to /output"},
    "eroare": {"ro": "Eroare: {msg}", "en": "Error: {msg}"},
    "durata_gol": {"ro": "DURATĂ  --", "en": "DURATION  --"},
    "durata": {"ro": "DURATĂ  {s:.0f}s", "en": "DURATION  {s:.0f}s"},
    "fragmente_gol": {"ro": "FRAGMENTE  --", "en": "CHUNKS  --"},
    "fragmente": {"ro": "FRAGMENTE  {n}", "en": "CHUNKS  {n}"},
    "piese_gasite": {"ro": "Piese găsite", "en": "Tracks found"},
    "dialog_titlu": {"ro": "Alege un set DJ", "en": "Choose a DJ set"},
    "dialog_audio": {"ro": "Fișiere audio", "en": "Audio files"},
    "dialog_toate": {"ro": "Toate fișierele", "en": "All files"},
}

LATIME_FEREASTRA = 640
INALTIME_FEREASTRA = 820

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

import os

app = ctk.CTk()
app.title("DJ Track Finder")
app.geometry(f"{LATIME_FEREASTRA}x{INALTIME_FEREASTRA}")
app.resizable(False, False)
app.configure(fg_color=COLOR_BG)

icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
if os.path.exists(icon_path):
    app.iconbitmap(icon_path)

try:
    import pywinstyles
    pywinstyles.apply_style(app, "acrylic")
except Exception:
    pass

selected_file = ""
is_running = False
work_queue = queue.Queue()
particule = []
linii_pool = []
mouse_pos = {"x": -9999, "y": -9999}
limba_curenta = "ro"

stare = {
    "status_key": "astept_fisier",
    "status_kwargs": {},
    "durata": None,
    "fragmente": None,
    "fisier_ales": False,
    "nume_fisier": "",
}


def t(cheie, **kwargs):
    text = TEXTE[cheie][limba_curenta]
    return text.format(**kwargs) if kwargs else text


bg_canvas = Canvas(app, bg=COLOR_BG, highlightthickness=0, bd=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)


def initializeaza_particule(event=None):
    if particule:
        return

    w = bg_canvas.winfo_width()
    h = bg_canvas.winfo_height()
    if w < 10 or h < 10:
        return

    for _ in range(NUM_PARTICULE):
        x = random.uniform(0, w)
        y = random.uniform(0, h)
        pid = bg_canvas.create_oval(
            x - RAZA_PARTICULA, y - RAZA_PARTICULA,
            x + RAZA_PARTICULA, y + RAZA_PARTICULA,
            fill=COLOR_ACCENT2, outline=""
        )
        particule.append({
            "x": x, "y": y,
            "vx": random.uniform(-0.3, 0.3),
            "vy": random.uniform(-0.3, 0.3),
            "id": pid
        })

    n = len(particule)
    for i in range(n):
        for j in range(i + 1, n):
            lid = bg_canvas.create_line(0, 0, 0, 0, fill=COLOR_CARD_BORDER, width=1, state="hidden", tags="linie")
            linii_pool.append({"id": lid, "i": i, "j": j})

    bg_canvas.tag_lower("linie")


def urmareste_mouse(event):
    mouse_pos["x"] = event.x_root - app.winfo_rootx()
    mouse_pos["y"] = event.y_root - app.winfo_rooty()


def animeaza_particule():
    if not particule:
        app.after(50, animeaza_particule)
        return

    w = bg_canvas.winfo_width()
    h = bg_canvas.winfo_height()
    mx, my = mouse_pos["x"], mouse_pos["y"]

    for p in particule:
        dx = p["x"] - mx
        dy = p["y"] - my
        dist = math.hypot(dx, dy)

        if 0.01 < dist < RAZA_MOUSE:
            forta = (1 - dist / RAZA_MOUSE) * FORTA_MOUSE
            p["vx"] += (dx / dist) * forta
            p["vy"] += (dy / dist) * forta

        p["vx"] = (p["vx"] + random.uniform(-0.02, 0.02)) * 0.96
        p["vy"] = (p["vy"] + random.uniform(-0.02, 0.02)) * 0.96

        viteza = math.hypot(p["vx"], p["vy"])
        if viteza > VITEZA_MAXIMA:
            p["vx"] = (p["vx"] / viteza) * VITEZA_MAXIMA
            p["vy"] = (p["vy"] / viteza) * VITEZA_MAXIMA

        p["x"] += p["vx"]
        p["y"] += p["vy"]

        if p["x"] < 0: p["x"] = w
        if p["x"] > w: p["x"] = 0
        if p["y"] < 0: p["y"] = h
        if p["y"] > h: p["y"] = 0

        bg_canvas.coords(p["id"], p["x"] - RAZA_PARTICULA, p["y"] - RAZA_PARTICULA, p["x"] + RAZA_PARTICULA, p["y"] + RAZA_PARTICULA)

    for linie in linii_pool:
        p1 = particule[linie["i"]]
        p2 = particule[linie["j"]]
        d = math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])

        if d < DISTANTA_LINIE:
            culoare = COLOR_ACCENT if d < DISTANTA_LINIE * 0.5 else COLOR_CARD_BORDER
            bg_canvas.coords(linie["id"], p1["x"], p1["y"], p2["x"], p2["y"])
            bg_canvas.itemconfigure(linie["id"], state="normal", fill=culoare)
        else:
            bg_canvas.itemconfigure(linie["id"], state="hidden")

    app.after(16, animeaza_particule)


bg_canvas.bind("<Configure>", initializeaza_particule)
app.bind_all("<Motion>", urmareste_mouse)


def seteaza_status(cheie, **kwargs):
    stare["status_key"] = cheie
    stare["status_kwargs"] = kwargs
    culoare = COLOR_ERROR if cheie == "eroare" else (COLOR_ACCENT2 if cheie == "gata" else COLOR_TEXT_MUTED)
    status_label.configure(text=t(cheie, **kwargs), text_color=culoare)


def aplica_traduceri():
    titlu_label.configure(text=t("titlu"))
    subtitlu_label.configure(text=t("subtitlu"))
    lang_button.configure(text="EN" if limba_curenta == "ro" else "RO")
    select_button.configure(text=t("alege_fisier"))
    start_button.configure(text=t("procesare") if is_running else t("start"))
    piese_gasite_label.configure(text=t("piese_gasite"))

    file_label.configure(
        text=stare["nume_fisier"] if stare["fisier_ales"] else t("niciun_fisier")
    )

    seteaza_status(stare["status_key"], **stare["status_kwargs"])

    durata_label.configure(text=t("durata", s=stare["durata"]) if stare["durata"] is not None else t("durata_gol"))
    fragmente_label.configure(text=t("fragmente", n=stare["fragmente"]) if stare["fragmente"] is not None else t("fragmente_gol"))


def comuta_limba():
    global limba_curenta
    limba_curenta = "en" if limba_curenta == "ro" else "ro"
    aplica_traduceri()


def alege_fisier():
    global selected_file

    if is_running:
        return

    fisier = filedialog.askopenfilename(
        title=t("dialog_titlu"),
        filetypes=[(t("dialog_audio"), "*.mp3 *.wav *.flac *.m4a"), (t("dialog_toate"), "*.*")]
    )

    if fisier:
        selected_file = fisier
        stare["fisier_ales"] = True
        stare["nume_fisier"] = fisier.split("/")[-1].split("\\")[-1]

        file_label.configure(text=stare["nume_fisier"], text_color=COLOR_TEXT)
        seteaza_status("fisier_selectat")


def worker_thread(file_path):
    from analyzer import get_audio_duration, split_audio
    from recognizer import recognize_tracks
    from exporter import export_txt, export_csv

    try:
        work_queue.put(("status", "citesc"))
        durata = get_audio_duration(file_path)
        work_queue.put(("duration", durata))

        work_queue.put(("status", "impart"))
        fisiere = split_audio(file_path)
        work_queue.put(("split_done", len(fisiere)))

        def raporteaza_progres(index, total, track):
            work_queue.put(("progress", index, total))

        def track_gasit(track, lista_curenta):
            export_txt(lista_curenta)
            export_csv(lista_curenta)
            work_queue.put(("track_found", track, len(lista_curenta)))

        work_queue.put(("status", "incep_recunoasterea"))

        tracklist = recognize_tracks(fisiere, progress_callback=raporteaza_progres, on_track_found=track_gasit)
        work_queue.put(("done", tracklist))

    except Exception as e:
        work_queue.put(("error", str(e)))


def start_analiza():
    global is_running

    if is_running:
        return

    if selected_file == "":
        seteaza_status("eroare_fara_fisier")
        return

    is_running = True
    start_button.configure(state="disabled", text=t("procesare"))
    select_button.configure(state="disabled")

    for widget in lista_frame.winfo_children():
        widget.destroy()

    badge_label.configure(text="0")
    stare["durata"] = None
    stare["fragmente"] = None
    durata_label.configure(text=t("durata_gol"))
    fragmente_label.configure(text=t("fragmente_gol"))
    progress.set(0)
    percent_label.configure(text="0%")

    threading.Thread(target=worker_thread, args=(selected_file,), daemon=True).start()
    app.after(100, verifica_coada)


def adauga_rand_track(index, nume_track):
    fundal = COLOR_ROW_ALT if index % 2 == 0 else "transparent"
    rand = ctk.CTkFrame(lista_frame, fg_color=fundal, corner_radius=8, cursor="hand2")
    rand.pack(fill="x", pady=2, padx=2)

    index_label = ctk.CTkLabel(rand, text=f"{index:02d}", font=FONT_TRACK_INDEX, text_color=COLOR_ACCENT2, width=36, anchor="w")
    index_label.pack(side="left", padx=(10, 4), pady=8)

    track_label = ctk.CTkLabel(rand, text=nume_track, font=FONT_TRACK, text_color=COLOR_TEXT, anchor="w", justify="left", wraplength=440)
    track_label.pack(side="left", padx=(4, 10), pady=8, fill="x", expand=True)

    def la_intrare(event):
        rand.configure(fg_color=COLOR_CARD_BORDER)

    def la_iesire(event):
        rand.configure(fg_color=fundal)

    for widget in (rand, index_label, track_label):
        widget.bind("<Enter>", la_intrare)
        widget.bind("<Leave>", la_iesire)


def verifica_coada():
    global is_running

    try:
        while True:
            mesaj = work_queue.get_nowait()
            tip = mesaj[0]

            if tip == "status":
                seteaza_status(mesaj[1])

            elif tip == "duration":
                stare["durata"] = mesaj[1]
                durata_label.configure(text=t("durata", s=mesaj[1]))

            elif tip == "split_done":
                stare["fragmente"] = mesaj[1]
                fragmente_label.configure(text=t("fragmente", n=mesaj[1]))
                progress.set(0.1)
                percent_label.configure(text="10%")

            elif tip == "progress":
                index, total = mesaj[1], mesaj[2]
                procent = 0.1 + (index / total) * 0.85
                progress.set(procent)
                percent_label.configure(text=f"{int(procent * 100)}%")
                seteaza_status("recunosc_fragment", i=index, n=total)

            elif tip == "track_found":
                track, numar_curent = mesaj[1], mesaj[2]
                adauga_rand_track(numar_curent, track)
                badge_label.configure(text=str(numar_curent))

            elif tip == "done":
                progress.set(1)
                percent_label.configure(text="100%")
                seteaza_status("gata", n=len(mesaj[1]))
                start_button.configure(state="normal", text=t("start"))
                select_button.configure(state="normal")
                is_running = False
                return

            elif tip == "error":
                seteaza_status("eroare", msg=mesaj[1])
                start_button.configure(state="normal", text=t("start"))
                select_button.configure(state="normal")
                is_running = False
                return

    except queue.Empty:
        pass

    if is_running:
        app.after(100, verifica_coada)


container = ctk.CTkFrame(app, fg_color=COLOR_BG, width=LATIME_FEREASTRA - 56, height=INALTIME_FEREASTRA - 48)
container.place(x=28, y=24)
container.pack_propagate(False)

header = ctk.CTkFrame(container, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
header.pack(fill="x", pady=(0, 16))

header_top = ctk.CTkFrame(header, fg_color="transparent")
header_top.pack(fill="x", padx=20, pady=(18, 4))

titlu_label = ctk.CTkLabel(header_top, text=t("titlu"), font=FONT_TITLU, text_color=COLOR_TEXT)
titlu_label.pack(side="left")

lang_button = ctk.CTkButton(
    header_top, text="EN", command=comuta_limba, font=FONT_LABEL_MIC,
    fg_color="transparent", hover_color=COLOR_ACCENT, border_width=1,
    border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MUTED,
    corner_radius=8, width=44, height=30, cursor="hand2"
)
lang_button.pack(side="right", anchor="n", pady=(6, 0))

subtitlu_label = ctk.CTkLabel(header, text=t("subtitlu"), font=FONT_SUBTITLU, text_color=COLOR_TEXT_MUTED)
subtitlu_label.pack(anchor="w", padx=20, pady=(2, 18))

card_fisier = ctk.CTkFrame(container, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
card_fisier.pack(fill="x", pady=(0, 16))

select_button = ctk.CTkButton(
    card_fisier, text=t("alege_fisier"), command=alege_fisier, font=FONT_BUTON,
    fg_color="transparent", hover_color=COLOR_ACCENT, border_width=1,
    border_color=COLOR_ACCENT2, text_color=COLOR_ACCENT2, corner_radius=12, height=44,
    cursor="hand2"
)
select_button.pack(fill="x", padx=20, pady=(20, 8))

file_label = ctk.CTkLabel(card_fisier, text=t("niciun_fisier"), font=FONT_LABEL_MIC, text_color=COLOR_TEXT_MUTED, wraplength=520, justify="left")
file_label.pack(fill="x", padx=20, pady=(0, 12), anchor="w")

start_button = ctk.CTkButton(
    card_fisier, text=t("start"), command=start_analiza, font=FONT_BUTON,
    fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, text_color="#ffffff", corner_radius=12, height=48,
    cursor="hand2"
)
start_button.pack(fill="x", padx=20, pady=(0, 20))

card_progres = ctk.CTkFrame(container, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
card_progres.pack(fill="x", pady=(0, 16))

info_row = ctk.CTkFrame(card_progres, fg_color="transparent")
info_row.pack(fill="x", padx=20, pady=(18, 6))

durata_label = ctk.CTkLabel(info_row, text=t("durata_gol"), font=FONT_LABEL, text_color=COLOR_TEXT_MUTED)
durata_label.pack(side="left")

fragmente_label = ctk.CTkLabel(info_row, text=t("fragmente_gol"), font=FONT_LABEL, text_color=COLOR_TEXT_MUTED)
fragmente_label.pack(side="right")

progress_row = ctk.CTkFrame(card_progres, fg_color="transparent")
progress_row.pack(fill="x", padx=20, pady=(4, 6))

progress = ctk.CTkProgressBar(progress_row, height=10, corner_radius=8, fg_color=COLOR_CARD_BORDER, progress_color=COLOR_ACCENT2)
progress.pack(side="left", fill="x", expand=True)
progress.set(0)

percent_label = ctk.CTkLabel(progress_row, text="0%", font=FONT_LABEL, text_color=COLOR_ACCENT2, width=42)
percent_label.pack(side="left", padx=(10, 0))

status_label = ctk.CTkLabel(card_progres, text=t("astept_fisier"), font=FONT_LABEL_MIC, text_color=COLOR_TEXT_MUTED)
status_label.pack(anchor="w", padx=20, pady=(0, 18))

card_tracklist = ctk.CTkFrame(container, fg_color=COLOR_CARD, corner_radius=16, border_width=1, border_color=COLOR_CARD_BORDER)
card_tracklist.pack(fill="both", expand=True)

tracklist_header = ctk.CTkFrame(card_tracklist, fg_color="transparent")
tracklist_header.pack(fill="x", padx=20, pady=(18, 8))

piese_gasite_label = ctk.CTkLabel(tracklist_header, text=t("piese_gasite"), font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT)
piese_gasite_label.pack(side="left")

badge_label = ctk.CTkLabel(tracklist_header, text="0", font=("Segoe UI", 12, "bold"), text_color="#ffffff", fg_color=COLOR_ACCENT, corner_radius=10, width=28, height=22)
badge_label.pack(side="right")

lista_frame = ctk.CTkScrollableFrame(card_tracklist, fg_color="transparent")
lista_frame.pack(fill="both", expand=True, padx=14, pady=(0, 16))

app.after(200, animeaza_particule)
app.mainloop()
