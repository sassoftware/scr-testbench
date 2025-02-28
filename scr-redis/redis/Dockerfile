FROM redis/redis-stack:latest

COPY cars.redis /opt/scripts/
COPY --chmod=711 load-data.sh /opt/scripts/
COPY --chmod=711 start.sh /opt/scripts/

ENTRYPOINT ["/opt/scripts/start.sh"]
