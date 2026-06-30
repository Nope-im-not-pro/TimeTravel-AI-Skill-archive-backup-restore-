# restore.py - Restore-Point System

> **Language:** English below. Eine deutsche Fassung folgt darunter -> [Deutsch](#deutsch).

Standalone tool, project-agnostic. Post-run snapshot instead of pre-edit backup.
Real time-travel to any earlier project state. Hot/cold archive tiering for old
backups. Central backup root.

## Purpose

Instead of a `.bak` per file before every edit: one restore point (W-H-P) at
run end. Full snapshot as baseline, then deltas only per run. Restore via
replay of all points up to the target. Old points move into monthly archives
automatically.

## Backup root (central)

State lives **not** in the project but centrally:

```
<BACKUP_ROOT>/<project-name>/        # Default: ~/.restore_backups/<project-name>/
  restore_FILES.md      # staging list for next W-H-P
  .restoreignore        # optional, glob like .gitignore
  index.json            # DB of all points (+ storage flags, archived_count)
  <id>/manifest.json    # file list of a live point (audit redundancy)
  <id>/files.zip        # contents (DEFLATE)
  _archive/<YYYY-MM>.zip # archived points (ZIP_STORED)
```

The project root holds only `restore.py` from the workflow.

### Configuration (env / .env)
Machine-specific paths do not belong in the repo. Configure via shell env var
**or** a local `.env` file (not committed). Template: copy `.env.example` to
`.env` and adjust. Set shell env vars take precedence over `.env`.

| Variable | Default | Effect |
|---|---|---|
| `RESTORE_BACKUP_ROOT` | `~/.restore_backups` | backup root (portability) |
| `RESTORE_PROJECT_NAME` | `basename(cwd)` | project subfolder (collisions) |

An old project-local `.restore/` is migrated into the central root
automatically on first call.

## Usage

| Command | Effect |
|---|---|
| `python restore.py` | interactive menu [1]-[5]/[q] |
| `python restore.py -1` | baseline snapshot (full tree minus ignore) |
| `python restore.py -2 [-m "summary"]` | W-H-P from `restore_FILES.md` |
| `python restore.py -3 -1` | restore last W-H-P (`type=whp`) |
| `python restore.py -3 --2026-06-21` | youngest point of the date |
| `python restore.py -3 --2026-06-21_15-32-05` | exact ID |
| `python restore.py -3` | interactive selection (step 1 -> 2 -> `[r]`) |
| `python restore.py --archive` | bundle old points now (force) |
| `python restore.py --status` | overview live/archived + archives |

`-1` and `-2` trigger an archive check automatically after writing (only on
trigger).

## Archive tiering (hot/cold)

- **Hot:** points as single folders. Fast restore.
- **Cold:** monthly archive `_archive/<YYYY-MM>.zip`.
- **Trigger** (bundling run): live count > 60 OR oldest live point older than
  14 days.
- **Selection:** archive a point if older than 14 days OR beyond the newest 50.
  The **newest** point always stays hot.
- **Restore** reads archived contents transparently from the monthly zip.

## Staging (restore_FILES.md)

```
summary: FixPlan phase 3-6 done

modified  src/auth/jwt.py
created   src/new.py
deleted   src/old.py
```

Action prefix optional -> auto-detection. `summary:` line or CLI `-m`
(precedence). Cleared after `-2`.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 1 | general error |
| 2 | no W-H-P for selector/`-1` |
| 3 | staging empty/missing on `-2` |

## Setup

Python 3 (stdlib only, no dependencies). Copy `restore.py` into the project
root. Optionally copy `.env.example` to `.env` and adjust paths. The backup
root is created automatically.

## License

MIT - see [LICENSE](LICENSE).

## Recovery

`index.json` is the aggregated DB. On loss, reconstructable from the
`manifest.json` files (live folders) or the monthly archives.

---

<a id="deutsch"></a>
# restore.py - Wiederherstellungspunkt-System

Standalone-Tool, projektunabhängig. Post-Run-Snapshot statt Pre-Edit-Backup.
Echtes Time-Travel auf jeden früheren Projektstand. Hot/Cold-Archiv-Tiering
für alte Backups. Zentraler Backup-Root.

## Zweck

Statt `.bak` pro Datei vor jedem Edit: ein Wiederherstellungspunkt (W-H-P)
am Run-Ende. Voller Snapshot als Baseline, danach nur Deltas je Run.
Restore via Replay aller Punkte bis zum Ziel. Alte Punkte wandern
automatisch in Monats-Archive.

## Backup-Root (zentral)

State liegt **nicht** im Projekt, sondern zentral:

```
<BACKUP_ROOT>/<projekt-name>/        # Default: ~/.restore_backups/<projekt-name>/
  restore_FILES.md      # Staging-Liste für nächsten W-H-P
  .restoreignore        # optional, Glob wie .gitignore
  index.json            # DB aller Punkte (+ storage-Flags, archived_count)
  <id>/manifest.json    # Datei-Liste eines Live-Punkts (Audit-Redundanz)
  <id>/files.zip        # Inhalte (DEFLATE)
  _archive/<YYYY-MM>.zip # archivierte Punkte (ZIP_STORED)
```

Projekt-Root enthält vom Workflow nur `restore.py`.

### Konfiguration (Env / .env)
Maschinen-spezifische Pfade gehören nicht ins Repo. Konfiguration via
Shell-Env-Var **oder** lokaler `.env`-Datei (nicht committet). Vorlage:
`.env.example` nach `.env` kopieren und anpassen. Gesetzte Shell-Env-Vars
haben Vorrang vor `.env`.

| Variable | Default | Wirkung |
|---|---|---|
| `RESTORE_BACKUP_ROOT` | `~/.restore_backups` | Backup-Wurzel (Portabilität) |
| `RESTORE_PROJECT_NAME` | `basename(cwd)` | Projekt-Unterordner (Kollisionen) |

Ein altes projektlokales `.restore/` wird beim ersten Aufruf automatisch
in den zentralen Root migriert.

## Aufruf

| Befehl | Wirkung |
|---|---|
| `python restore.py` | interaktives Menü [1]-[5]/[q] |
| `python restore.py -1` | Basis-Snapshot (voller Baum minus Ignore) |
| `python restore.py -2 [-m "summary"]` | W-H-P aus `restore_FILES.md` |
| `python restore.py -3 -1` | letzten W-H-P (`type=whp`) wiederherstellen |
| `python restore.py -3 --2026-06-21` | jüngsten Punkt des Datums |
| `python restore.py -3 --2026-06-21_15-32-05` | exakte ID |
| `python restore.py -3` | interaktive Auswahl (Schritt 1 -> 2 -> `[r]`) |
| `python restore.py --archive` | alte Punkte sofort bündeln (force) |
| `python restore.py --status` | Übersicht live/archiviert + Archive |

`-1` und `-2` lösen nach dem Schreiben automatisch einen
Archivierungs-Check aus (nur bei Trigger).

## Archiv-Tiering (Hot/Cold)

- **Hot:** Punkte als Einzel-Ordner. Schneller Restore.
- **Cold:** Monats-Archiv `_archive/<YYYY-MM>.zip`.
- **Trigger** (Bündelungslauf): Live-Anzahl > 60 ODER ältester
  Live-Punkt älter als 14 Tage.
- **Auswahl:** archiviere Punkt wenn älter als 14 Tage ODER jenseits der
  neuesten 50. Der **neueste** Punkt bleibt immer hot.
- **Restore** liest archivierte Inhalte transparent aus dem Monats-Zip.

## Staging (restore_FILES.md)

```
summary: FixPlan Phase 3-6 umgesetzt

modified  src/auth/jwt.py
created   src/new.py
deleted   src/old.py
```

Action-Prefix optional -> Auto-Erkennung. `summary:`-Zeile oder CLI `-m`
(Vorrang). Nach `-2` geleert.

## Exit-Codes

| Code | Bedeutung |
|---|---|
| 0 | ok |
| 1 | Fehler allgemein |
| 2 | kein W-H-P für Selektor/`-1` |
| 3 | Staging leer/fehlt bei `-2` |

## Setup

Python 3 (stdlib only, keine Abhängigkeiten). `restore.py` in Projekt-Root
kopieren. Optional `.env.example` nach `.env` kopieren und Pfade anpassen.
Backup-Root wird automatisch angelegt.

## Lizenz

MIT - siehe [LICENSE](LICENSE).

## Recovery

`index.json` ist aggregierte DB. Bei Verlust aus den `manifest.json`
(Live-Ordner) bzw. den Monats-Archiven rekonstruierbar.
