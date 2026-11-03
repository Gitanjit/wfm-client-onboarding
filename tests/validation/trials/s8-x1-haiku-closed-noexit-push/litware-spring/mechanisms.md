# Step-2 mechanisms (from checks.json)

| mechanism | evidence |
|---|---|
| email queue missing or unstaffed | `[]` |
| interval count / grid (reader, DST) | `[]` |
| efficiency bound | `[]` |
| R4 priority floor violations (W11, W12) | `[0, 0]` |
| R5 email start violations (W11, W12) | `[0, 0]` |
| §2.6 exceptions report | `[{"expected": 42, "extra": [], "listed": 0, "missing": [["email", "2027-03-15T07:00:00Z"], ["email", "2027-03-15T07:20:00Z"], ["email", "2027-03-15T07:40:00Z"]], "pass": false}]` |
| Northwind regression (W44/W45 against its SOW) | `["reg_northwind_2026-W44_rules", "reg_northwind_2026-W44_sla_vip", "reg_northwind_2026-W45_rules", "reg_northwind_2026-W45_sla_vip"]` |
| Contoso / Fabrikam regression | `[]` |
