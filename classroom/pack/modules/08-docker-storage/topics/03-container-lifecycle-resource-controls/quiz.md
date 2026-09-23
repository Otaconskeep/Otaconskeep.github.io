# Quiz — Container Lifecycle and Resource Controls

**Module:** Module 8 — Docker, Storage & Permissions
**Activity type:** Quiz (Test)

## Knowledge check

1. What two operations does `docker run` combine?  
2. What is the normal difference between `stop` and default `kill`?  
3. Does `running` prove the application is healthy?  
4. What does a PID limit help contain?  
5. Why reserve resources for the host?  
6. When can `restart: always` be harmful?

## Answer key

1. Create and start.  
2. `stop` requests graceful termination before forcing; default `kill` sends immediate `SIGKILL`.  
3. No. It proves only that the container's primary process is running.  
4. Runaway or malicious process creation.  
5. The kernel, storage, networking, monitoring, and recovery tools must remain functional.  
6. During a persistent configuration or dependency failure that creates a rapid restart loop.
