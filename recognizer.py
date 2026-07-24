import asyncio
import re
from shazamio import Shazam
from shazamio.client import HTTPClient
from aiohttp_retry import ExponentialRetry

# ==========================
# Configurare retry / timeout
# ==========================

RETRY_INCERCARI = 3
RETRY_MAX_TIMEOUT = 10
TIMEOUT_TOTAL_FRAGMENT = 40
PAUZA_INTRE_FRAGMENTE = 1.2


def _creeaza_shazam():
    return Shazam(
        http_client=HTTPClient(
            retry_options=ExponentialRetry(
                attempts=RETRY_INCERCARI,
                max_timeout=RETRY_MAX_TIMEOUT,
                statuses={429, 500, 502, 503, 504},
            ),
        ),
    )


def _normalizeaza(track):
    """
    Scoate ce e în paranteze/paranteze drepte (remix, edit, feat., etc.)
    și literele mari, ca să putem compara dacă 2 titluri sunt "aceeași piesă"
    chiar dacă Shazam le-a raportat cu detalii diferite.
    """
    fara_paranteze = re.sub(r"[\(\[].*?[\)\]]", "", track)
    return fara_paranteze.strip().lower()


async def _recognize_file(shazam, file_path):
    try:
        result = await asyncio.wait_for(
            shazam.recognize(file_path),
            timeout=TIMEOUT_TOTAL_FRAGMENT
        )
        track = result.get("track")

        if not track:
            return None

        title = track.get("title", "").strip()
        subtitle = track.get("subtitle", "").strip()

        if not title:
            return None

        return f"{subtitle} - {title}" if subtitle else title

    except Exception:
        return None


async def _recognize_all(file_list, progress_callback=None, on_track_found=None):
    shazam = _creeaza_shazam()
    cleaned = []
    last_norm = None
    total = len(file_list)

    for i, file_path in enumerate(file_list):
        track = await _recognize_file(shazam, file_path)

        if progress_callback:
            progress_callback(i + 1, total, track)

        if track is not None:
            track_norm = _normalizeaza(track)

            if track_norm != last_norm:
                # piesă nouă
                cleaned.append(track)
                last_norm = track_norm

                if on_track_found:
                    on_track_found(track, list(cleaned))

            else:
                # duplicat consecutiv (poate raportat cu titlu ușor diferit,
                # ex. cu/fără remix) -- păstrăm varianta cu mai multe detalii
                if len(track) > len(cleaned[-1]):
                    cleaned[-1] = track

                    if on_track_found:
                        on_track_found(track, list(cleaned))

        if i < total - 1:
            await asyncio.sleep(PAUZA_INTRE_FRAGMENTE)

    return cleaned


def recognize_tracks(file_list, progress_callback=None, on_track_found=None):
    """
    Rulează recunoașterea Shazam pentru o listă de fișiere audio (sincron, blocant
    -- de aceea trebuie apelată dintr-un thread separat, nu direct din UI).

    Retry-ul intern al shazamio e scurt (max ~10s/încercare, 3 încercări) + o
    plasă de siguranță de 40s per fragment, plus o pauză mică între fragmente
    ca să nu declanșăm rate-limiting.

    Eliminarea duplicatelor consecutive ignoră conținutul din paranteze
    (remix/edit/feat.), ca să nu apară aceeași piesă de mai multe ori doar
    pentru că Shazam a raportat-o cu titlu ușor diferit -- păstrează
    întotdeauna varianta cu cele mai multe detalii.

    progress_callback(index_curent, total, track_gasit_sau_None)
    on_track_found(track, lista_curenta) -- pentru autosave live.

    Returnează lista finală, curată, de piese.
    """
    return asyncio.run(_recognize_all(file_list, progress_callback, on_track_found))
