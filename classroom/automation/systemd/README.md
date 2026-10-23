# systemd units

Service units are rendered by `install.sh` from `*.service.tmpl` with `@PYTHON@`
set to the dedicated venv interpreter under `/var/lib/otaconskeep-classroom/venv`.

Timer files (`*.timer`) are installed as-is. Timers stay disabled until
`ACTIVATION_APPROVED` exists and `install.sh --activate` is used.
