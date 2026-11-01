Northwind demand export

- One row per queue per 30-minute interval, 00:00-24:00 local, every day of the ISO week.
- interval_start_local is America/Chicago wall-clock time. utc_offset is the offset in effect for that
  row and is authoritative: derive UTC from it, not from the wall-clock label.
<!-- G: your call — keep "authoritative" (their word) or say "use the offset, the label alone is not enough" -->
- Columns: interval_start_local, utc_offset, queue, volume, aht_sec
- Files: export_<ISO week>.csv, e.g. export_2026-W44.csv
- Rows come straight out of Northwind's reporting tool. Report anything odd to their WFM contact.
<!-- G: your call — this last line is new; it is true of real exports and nudges a data look. Keep or drop -->
