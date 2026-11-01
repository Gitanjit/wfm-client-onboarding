Litware demand export

- One row per queue per 20-minute interval, 00:00-24:00 local, every day of the ISO week.
- interval_end_local is Europe/London wall-clock time at which the interval ENDS: a row stamped
  09:20 covers 09:00-09:20. utc_offset is the offset in effect at that moment and is authoritative.
- Columns: interval_end_local, utc_offset, queue, volume, aht_sec
- Queues: priority, standard, email
- Files: export_<ISO week>.csv, e.g. export_2027-W11.csv
