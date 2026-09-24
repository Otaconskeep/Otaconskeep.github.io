# Module project: Linux Foundations

**Module:** Module 06: Linux Foundations  
**Activity type:** Project (integrated Apply/Create)  
**Classes covered:** 16, 17, 18, 19, 20, 21  
**Lab risk:** medium (disposable paths + optional user systemd + ssh lab VM only)

## Objective

Deliver a single evidence pack proving you can navigate, pipe, permission, supervise, log, and SSH-harden a disposable lab without touching production `/data`.

## Deliverables

1. **Lab tree** under `/opt/lab-classroom/module06-project/` with `configs/`, `logs/`, `bin/`.
2. **Pipeline** that filters ERROR lines from a sample log into `logs/errors.txt` using grep|tee and reports a count.
3. **Identity**: a lab group and two lab users; shared directory mode proving group-read without world-write (no 777).
4. **Service**: a user-level oneshot systemd unit that appends a heartbeat line to `logs/heartbeat.log`.
5. **Journal evidence**: redacted `journalctl --user` excerpt for that unit.
6. **SSH notes**: screenshot or command transcript of key auth on a lab VM *or* a clearly labeled simulation documenting hardening order and break-glass console plan if no second VM is available.

## Verification checklist

- [ ] `realpath` shows all artifacts under `/opt/lab-classroom/module06-project`
- [ ] Pipeline evidence file exists and count matches ERROR lines
- [ ] `namei -l` shows non-777 shared directory ownership
- [ ] `systemctl --user status` shows oneshot success
- [ ] Journal excerpt redacted
- [ ] SSH section either proven or labeled simulation with recovery plan

## Rollback

```bash
systemctl --user disable --now module06-heartbeat.service 2>/dev/null || true
rm -f ~/.config/systemd/user/module06-heartbeat.service
systemctl --user daemon-reload
rm -rf /opt/lab-classroom/module06-project
# remove any lab-only users/groups you created for this project
```

## Security

No production paths. No `chmod 777`. No private keys committed. No sshd changes without console.
