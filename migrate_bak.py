#!/usr/bin/env python3
"""migrate_bak.py - Legacy-Backup-Migration (Standalone, stdlib only).

Zweck: Alte Pre-Edit-Backup-Aera-Dateien (`<projekt>/backups/*.bak`) in den
zentralen Backup-Root umziehen. Pro gefundenem Projekt werden alle .bak in
einem ZIP unter `<BACKUP_ROOT>/<projekt>/_legacy_bak/<ISO>.zip` gebuendelt.
Nach verifiziertem ZIP werden die Original-.bak entfernt und ein dann leeres
`backups/`-Verzeichnis geloescht.

Einmal-Lauf-Hinweis: Dies ist KEIN Hook und laeuft NICHT automatisch. Manuell
und einmalig ausfuehren beim Umstieg vom alten .bak-Modell auf das
Post-Run-Snapshot-Modell (restore.py). Danach obsolet.

BACKUP_ROOT-Konvention identisch zu restore.py: Env RESTORE_BACKUP_ROOT,
sonst ~/.restore_backups. Projektname = basename(projekt-dir).

MVC: eigenstaendiges Service-Tool (Migrations-Service, kein Model/View/
Controller-Bezug).
"""

import os
import sys
import zipfile
import argparse
import shutil
from datetime import datetime


def backup_root():
    """Zentraler Backup-Root, identisch zu restore.py."""
    return os.environ.get(
        "RESTORE_BACKUP_ROOT",
        os.path.join(os.path.expanduser("~"), ".restore_backups"),
    )


def find_projects(root):
    """Sucht unter root rekursiv alle backups/-Verzeichnisse mit >=1 *.bak.

    Liefert Liste von Tupeln (projekt_root, backups_dir, [bak_pfade]).
    """
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        if os.path.basename(dirpath) != "backups":
            continue
        baks = [
            os.path.join(dirpath, f)
            for f in filenames
            if f.endswith(".bak")
        ]
        if not baks:
            continue
        projekt_root = os.path.dirname(dirpath)
        found.append((projekt_root, dirpath, sorted(baks)))
    return found


def migrate_project(projekt_root, backups_dir, baks, dry_run):
    """Migriert ein Projekt. Liefert (status, zip_pfad, anzahl).

    status: "OK" | "DRY-RUN" | "FEHLER".
    """
    projektname = os.path.basename(projekt_root)
    iso = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_dir = os.path.join(backup_root(), projektname, "_legacy_bak")
    zip_pfad = os.path.join(zip_dir, iso + ".zip")

    if dry_run:
        return ("DRY-RUN", zip_pfad, len(baks))

    try:
        os.makedirs(zip_dir, exist_ok=True)
        with zipfile.ZipFile(zip_pfad, "w", zipfile.ZIP_DEFLATED) as zf:
            for bak in baks:
                arcname = os.path.relpath(bak, projekt_root).replace(os.sep, "/")
                zf.write(bak, arcname)

        # Verifikation
        with zipfile.ZipFile(zip_pfad, "r") as zf:
            if zf.testzip() is not None:
                return ("FEHLER", zip_pfad, len(baks))
            if len(zf.namelist()) != len(baks):
                return ("FEHLER", zip_pfad, len(baks))

        # Originale entfernen
        for bak in baks:
            os.remove(bak)
        # leeres backups/ loeschen
        if not os.listdir(backups_dir):
            os.rmdir(backups_dir)

        return ("OK", zip_pfad, len(baks))
    except Exception as exc:
        sys.stderr.write(
            "  FEHLER bei {}: {}\n".format(projektname, exc)
        )
        return ("FEHLER", zip_pfad, len(baks))


def main():
    parser = argparse.ArgumentParser(
        description="Legacy <projekt>/backups/*.bak als ZIP nach "
        "<BACKUP_ROOT>/<projekt>/_legacy_bak/ umziehen."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=os.getcwd(),
        help="Wurzel-Pfad fuer rekursive Suche (Default: cwd).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nur Plan ausgeben, nichts schreiben/loeschen.",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    projects = find_projects(root)

    print("migrate_bak.py - Legacy-Backup-Migration")
    print("Root:        {}".format(root))
    print("Backup-Root: {}".format(backup_root()))
    print("Modus:       {}".format("DRY-RUN" if args.dry_run else "LIVE"))
    print("Projekte:    {}".format(len(projects)))
    print("-" * 60)

    total_bak = 0
    fehler = 0
    for projekt_root, backups_dir, baks in projects:
        status, zip_pfad, anzahl = migrate_project(
            projekt_root, backups_dir, baks, args.dry_run
        )
        total_bak += anzahl
        if status == "FEHLER":
            fehler += 1
        print("Projekt: {}".format(os.path.basename(projekt_root)))
        print("  .bak:   {}".format(anzahl))
        print("  ZIP:    {}".format(zip_pfad))
        print("  Status: {}".format(status))

    print("-" * 60)
    print(
        "Summe: {} Projekte, {} .bak-Dateien, {} Fehler.".format(
            len(projects), total_bak, fehler
        )
    )

    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
