# Quiz: Docker Volumes and Bind Mounts

**Module:** Module 8: Docker, Storage & Permissions
**Activity type:** Quiz (Test)

## Knowledge check

1. Which storage normally survives container deletion?  
2. What makes a bind mount host-coupled?  
3. What happens to image files hidden beneath a mountpoint?  
4. When is tmpfs useful?  
5. Why is a successful archive command insufficient backup proof?  
6. Why can a raw database-directory copy be inconsistent?

## Answer key

1. Named volumes and host bind data survive, unless explicitly deleted.  
2. It names a specific host path and inherits its layout and permissions.  
3. They remain in the image but are obscured while the mount is attached.  
4. For bounded temporary or sensitive data that should disappear on stop.  
5. Recovery must be tested by restoring and verifying content/application behavior.  
6. Files can change during the copy or require database-aware consistency coordination.
