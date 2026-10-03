#!/usr/bin/env python3
"""Exportiert die Köln-Präsentation (index.html) als PDF – eine Folie pro Seite.

Benutzung:
    python3 export_pdf.py                  # -> koeln-praesentation.pdf
    python3 export_pdf.py -o backup.pdf    # eigener Dateiname
    python3 export_pdf.py --open           # PDF danach direkt öffnen

Gedruckt wird mit headless Chrome. Das Seitenformat (1280x720 px, Querformat,
randlos) steht in style.css in der @page-Regel – hier muss nichts eingestellt
werden.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

#: Kandidaten für den Browser – der erste gefundene wird benutzt.
BROWSERS = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "brave-browser",
    "microsoft-edge",
]


def find_browser(explicit: str | None) -> str:
    """Liefert den Pfad zu einem Chrome-artigen Browser."""
    if explicit:
        path = shutil.which(explicit) or (explicit if Path(explicit).exists() else None)
        if not path:
            sys.exit(f"Browser nicht gefunden: {explicit}")
        return path

    for name in BROWSERS:
        path = shutil.which(name)
        if path:
            return path

    sys.exit(
        "Kein Chrome/Chromium gefunden.\n"
        "Installieren (z. B. `sudo apt install chromium`) oder Pfad angeben:\n"
        "    python3 export_pdf.py --browser /pfad/zu/chrome"
    )


def count_pages(pdf: Path) -> int:
    """Zählt die Seiten im erzeugten PDF (einfache, abhängigkeitsfreie Prüfung)."""
    data = pdf.read_bytes()
    return len(re.findall(rb"/Type\s*/Page[^s]", data))


def export(html: Path, out: Path, browser: str, timeout: int, budget: int) -> None:
    if not html.is_file():
        sys.exit(f"Datei nicht gefunden: {html}")

    out.parent.mkdir(parents=True, exist_ok=True)

    # Eigenes Profilverzeichnis: sonst schlägt --print-to-pdf fehl, wenn
    # nebenher schon ein normales Chrome-Fenster offen ist.
    with tempfile.TemporaryDirectory(prefix="chrome-pdf-") as profile:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            # Zeit für Schriften, Bilder und das Layout-Skript:
            f"--virtual-time-budget={budget}",
            f"--print-to-pdf={out}",
            html.as_uri(),  # kodiert Umlaute im Pfad korrekt
        ]

        print(f"→ Browser : {browser}")
        print(f"→ Quelle  : {html}")
        print(f"→ Ziel    : {out}")

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            sys.exit(f"Abbruch: Chrome hat länger als {timeout}s gebraucht.")

    if not out.is_file() or out.stat().st_size == 0:
        sys.stderr.write(proc.stderr[-2000:] + "\n")
        sys.exit(f"Der Export ist fehlgeschlagen (Exit-Code {proc.returncode}).")

    pages = count_pages(out)
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"✓ Fertig: {pages} Seiten, {size_mb:.1f} MB")

    slides = len(re.findall(r'class="slide[ "]', html.read_text(encoding="utf-8")))
    if slides and pages != slides:
        print(
            f"! Achtung: {slides} Folien in {html.name}, aber {pages} PDF-Seiten.",
            file=sys.stderr,
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Köln-Präsentation als PDF exportieren (eine Folie pro Seite)."
    )
    parser.add_argument(
        "html",
        nargs="?",
        type=Path,
        default=HERE / "index.html",
        help="HTML-Datei der Präsentation (Standard: index.html neben diesem Skript)",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=HERE / "koeln-praesentation.pdf",
        help="Zieldatei (Standard: koeln-praesentation.pdf)",
    )
    parser.add_argument(
        "--browser",
        help="Pfad/Name des Browsers, falls er nicht automatisch gefunden wird",
    )
    parser.add_argument(
        "--budget",
        type=int,
        default=10000,
        help="Wartezeit in ms für Schriften/Bilder (Standard: 10000)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Maximale Laufzeit in Sekunden (Standard: 120)",
    )
    parser.add_argument(
        "--open", action="store_true", help="PDF nach dem Export öffnen"
    )
    args = parser.parse_args()

    export(
        html=args.html.resolve(),
        out=args.out.resolve(),
        browser=find_browser(args.browser),
        timeout=args.timeout,
        budget=args.budget,
    )

    if args.open:
        opener = shutil.which("xdg-open") or shutil.which("open")
        if opener:
            subprocess.Popen([opener, str(args.out.resolve())])


if __name__ == "__main__":
    main()
