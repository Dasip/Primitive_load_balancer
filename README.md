# Primitive_load_balancer

# Installation:

1. git clone this repo
2. docker build -t balancer:v1 (or another version_name:version combo)
3. docker run -d balancer:v1
4. After a while docker exec -it <container_id> bash
5. All logs are in /app/logs directory
6. 8001.log to 8005.log - service logs, proxy.log - load balancer logs
7. config.yaml in /app - config file for load balancer
