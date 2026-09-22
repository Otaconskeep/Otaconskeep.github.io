# Quiz — Virtual machines & Proxmox

**Module:** Module 1 — Infrastructure & Addressing  
**Activity type:** Quiz / retrieval practice  
**Target:** ≥80% before topic mastery unlock  
**Objective:** Given a host and a guest requirement, the learner can choose Type 1 vs Type 2 virtualization, create a working Linux guest (VirtualBox or Proxmox), and prove networking, DNS, and SSH with recorded evidence.

## Instructions

Close the reading. Write answers from memory. Then self-score.

## Questions

Active recall — write answers without rereading first. Target ≥80% before the gate.

1. In plain words, what is a virtual machine?
2. What is the difference between a host and a guest?
3. How does a Type 2 hypervisor differ from a Type 1 hypervisor?
4. Which guest type normally has its own kernel: VM or LXC?
5. What does `vmbr0` behave like on Proxmox?
6. Why is a successful ping to `1.1.1.1` but failed hostname lookup useful?
7. Why does this course put Docker in a Linux VM instead of nesting it in LXC on day one?
8. Name one benefit and one risk of bridged networking versus NAT.
9. What problem do snapshots solve that “just reinstall” is too slow for?

## After scoring

- Missed items → return to **Reading** weak sections → redo **Feynman Retry** → reattempt missed questions.
- Passing score unlocks marking this topic complete on the module hub (still need lab gate + homework).
