import datetime as _dt
DEPRECATION_TS = _dt.date(2025, 8, 15)

if _dt.date.today() >= DEPRECATION_TS:
  raise RuntimeError(
    "byterat package is deprecated as of 2025-08-15 due to an upstream API removal. Refer to ohm-ai at https://pypi.org/project/ohm-ai/ for the new API.",
    "Please uninstall this package."
  )