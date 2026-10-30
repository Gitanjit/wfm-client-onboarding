Northwind demand export

- One row per queue per 30-minute interval, covering 00:00-24:00 local every day of the ISO week.
- interval_start_local is America/Chicago wall-clock. utc_offset is the offset in effect for that
  row and is authoritative: derive UTC from it rather than from the wall-clock label.
- Columns: interval_start_local, utc_offset, queue, volume, aht_sec
- Files: export_<ISO week>.csv, e.g. export_2026-W44.csv
