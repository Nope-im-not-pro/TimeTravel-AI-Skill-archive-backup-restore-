# Changelog

Format: SemVer + ISO-Datum.

## [1.4.0] - 2026-06-26

### Hinzugefuegt
- `restore.py -2 --auto`: Stop-Commit erfasst alle Aenderungen per Diff des
  Arbeitsbaums gegen den letzten Punkt (autoritatives Datei-Set), inkl.
  Nicht-Hook-Edits (Bash `rm`/`sed`). Leeres Delta -> kein Punkt, Exit 0.
  Summary aus `-m` ODER `summary:`-Zeile ODER Auto-Text (ISO +
  "session auto-snapshot").
- Service-Funktion `compute_auto_delta(idx)` (Diff Disk vs. Soll-Zustand)
  und Helfer `read_from_point(idx, pid, rel) -> bytes` (Byte-Leser, aus
  `extract_from_point` ausgelagert).
- Hook-Trias als globale Backup-Richtlinie (ersetzt Pre-Edit-`.bak`,
  CLAUDE.md §4):
  - `restore-stage-hook.ps1` (PreToolUse Edit|Write|MultiEdit): Editor-Edit
    haengt Datei-Pfad idempotent an `restore_FILES.md` an, kein `.bak`.
  - SessionStart-Erst-Init: Anker `<BACKUP_ROOT>/<projekt>/index.json`
    fehlt -> `restore.py`-Kopie + Baseline (`-1`) synchron (Timeout 30s).
  - `restore-commit-hook.ps1` (Stop, nach dash-normalize): `restore.py -2
    --auto`.
- `migrate_bak.py` (stdlib): Einmal-Migration alter `<projekt>/backups/*.bak`
  als ZIP nach `<BACKUP_ROOT>/<projekt>/_legacy_bak/<ISO>.zip`, Originale
  nach Verifikation entfernt. `--dry-run` aendert nichts.

### Geaendert
- Master-Deploy `~/.claude/tools/restore.py` angelegt (inhaltsgleich).
- `settings.json`: PreToolUse `backup-hook.ps1` -> `restore-stage-hook.ps1`;
  SessionStart-Timeout 10 -> 35; Stop-Array um `restore-commit-hook.ps1`
  ergaenzt (nach dash-normalize). `backup-hook.ps1` entfernt.
- KONZEPT.md §4/§5 um `--auto` ergaenzt. CLAUDE.md §4 von Pre-Edit-`.bak`
  auf Post-Run-Snapshot neugefasst, Querverweise/Konflikt-Hierarchie
  nachgezogen.

### Verifiziert
- Integrations-Round-Trip (Temp-Projekt): Erst-Init-Baseline; Staging
  idempotent; `-2 --auto` erfasst modified/created/deleted inkl. Bash-`rm`;
  leeres Delta -> kein Punkt; `-3` Time-Travel byte-genau; 2. Session
  erkennt Anker (keine Re-Init).
- `migrate_bak.py`: `.bak` -> ZIP, `testzip()` None, Originale weg,
  `--dry-run` ohne Aenderung.
- settings.json valides JSON, 3 Hooks fuehren fehlertolerant (Exit 0) durch.

## [1.3.0] - 2026-06-25

### Geaendert
- Default-Backup-Root von maschinen-festem `C:\_PROJECTS\_backups` auf
  portables `~/.restore_backups` umgestellt. Kein absoluter Pfad mehr im
  Quellcode.
- Konfiguration zusaetzlich via lokaler `.env`-Datei moeglich (stdlib-
  Loader, keine Abhaengigkeit). Shell-Env-Var hat Vorrang.

### Hinzugefuegt
- `.env.example` als Konfig-Vorlage. `LICENSE` (MIT).
- `.gitignore`: `.env` und `.restore_backups/` ausgeschlossen.

### Verifiziert
- `--status` mit Portabel-Default (`~/.restore_backups`) und mit
  `.env`-Override (`RESTORE_BACKUP_ROOT`/`RESTORE_PROJECT_NAME`).

## [1.2.0] - 2026-06-25

### Hinzugefuegt
- Hot/Cold-Archiv-Tiering: alte Wiederherstellungspunkte werden in
  Monats-Archive `_archive/<YYYY-MM>.zip` (ZIP_STORED) gebuendelt.
  Auswahl je Punkt: archiviere wenn aelter als 14 Tage ODER jenseits der
  neuesten 50; der neueste Punkt bleibt immer hot. Buendelungs-Trigger:
  Live-Anzahl > 60 ODER aeltester Live-Punkt aelter als 14 Tage.
- Zentraler Backup-Root `C:\_PROJECTS\_backups\<projekt>\` statt
  projektlokalem `.restore/`. Env-Overrides `RESTORE_BACKUP_ROOT` und
  `RESTORE_PROJECT_NAME`. Projekt-Root enthaelt vom Workflow nur
  `restore.py`.
- Automatische Migration eines alten projektlokalen `.restore/` in den
  zentralen Root beim ersten Aufruf.
- index.json-Felder `storage` (`live`/`archived`), `archive` und
  Top-Level `archived_count`. Restore liest archivierte Inhalte transparent
  aus dem Monats-Zip.
- CLI `--archive` (force-Buendelung) und `--status` (Uebersicht
  live/archiviert + Archiv-Dateien). Menue um [4] Archivieren, [5] Status
  erweitert. Interaktive Punkt-Liste markiert archivierte Punkte mit `[A]`.

### Geaendert
- Backup-Pfade von `<root>/.restore/` auf zentralen Root umgestellt.
- `extract_from_point` erhaelt `idx` und entscheidet Live-Ordner vs Archiv.

### Verifiziert
- Trigger nach Anzahl (>60) und Alter (>14d, inkl. Klein-Anzahl- und
  gemischt-Faellen), Ausnahme "neuester bleibt live", Restore aus Archiv,
  gemischtes Hot/Cold-Time-Travel byte-genau, Migration projektlokal ->
  zentral, `--status`.

## [1.1.0] - 2026-06-25

### Geaendert
- WorkDir-Relokation: aller Workflow-State nach `./.restore/` verschoben
  (`restore_FILES.md`, `.restoreignore`, `index.json`, Punkt-Ordner).
  Root enthaelt vom Workflow nur noch `restore.py`.
- `DEFAULT_IGNORE_DIRS`: `.backups` -> `.restore`. `TOOL_FILES` auf
  `{restore.py}` reduziert.
- Selektor `-3 -1` filtert strikt auf `type=="whp"` (juengster W-H-P);
  juengere Baseline wird ignoriert. Kein WHP -> Exit 2.
- `.restoreignore` Glob-Semantik eingegrenzt: Segment-Match nur fuer
  reine Namen ohne Slash/Glob-Meta gegen Verzeichnis-Segmente. Patterns
  mit Slash/Meta nur via `fnmatch(rel,pat)` + `fnmatch(rel,pat+"/*")`.
- `manifest.json` als Audit-/Recovery-Redundanz dokumentiert (KONZEPT §4);
  Normalbetrieb liest nur `index.json`.

### Behoben
- Interaktiver Restore Schritt 2: `[r] wiederherstellen` nun im
  Pagination-Nav (KONZEPT §6). Toter Doppel-Prompt entfernt. `paginate()`
  generalisiert (Parameter `extra_keys`, Rueckgabe-Vertrag
  `("item",obj)`/`("key",taste)`/`None`).

### Verifiziert
- Smoke-Tests `-1`/`-2`/`-3` (Selektor + interaktiv), Time-Travel
  vorwaerts/rueckwaerts byte-genau, Glob-Eingrenzung, Exit-Codes 2+3,
  Layout-Check (Root sauber).

## [1.0.0] - 2026-06-25

### Hinzugefuegt
- Erst-Implementierung `restore.py`: Basis-Snapshot, W-H-P-Delta,
  Time-Travel-Restore, Pagination, Menue.
