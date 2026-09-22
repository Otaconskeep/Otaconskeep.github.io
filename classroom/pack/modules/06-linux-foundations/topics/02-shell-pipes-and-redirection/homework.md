# Homework — Shell Pipes and Redirection

**Module:** Linux Foundations
**Activity type:** Homework / independent application
**Objective:** Identify file descriptors 0, 1, and 2 as standard input, standard output, and standard error

## Requirements

Within /opt/lab-classroom/class17/, create homework-services.csv containing at least eight records with name, state, and port fields.
Build a pipeline that extracts the state field, sorts it, counts repeated values, and writes the report to homework-state-counts.txt.
Build a second pipeline using tee that saves all active records to homework-active.csv while writing their count to homework-active-count.txt.
Create a command group that emits one normal message and one diagnostic message, then save the streams in separate homework files.
Write a short text file named homework-explanation.txt explaining why 2>&1 > file behaves differently from > file 2>&1.
Verify every homework result with test, grep, awk, wc, or diff without creating files outside /opt/lab-classroom/class17/.

## Submit / record

- [ ] Evidence artifacts (secrets redacted)
- [ ] Spiral connections written
- [ ] Ready for topic quiz
