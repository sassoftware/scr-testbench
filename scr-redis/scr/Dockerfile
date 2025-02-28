FROM cr.sas.com/viya-4-x64_oci_linux_2-docker/sas-decisions-runtime-components:1.72.34-20241126.1732642899957 AS base
FROM cr.sas.com/viya-4-x64_oci_linux_2-docker/sas-decisions-runtime-base:1.92.34-20241126.1732642908961

USER root

# Python packages
#RUN pip3 install requests
#ENV LC_ALL=C

# Copy module to container
RUN chown sas:sas /modules
COPY --chown=sas:sas content/_module_definition.json /modules/

# Add Redis binaries
COPY --from=base /hiredis /

# Configure redis "sid-lists"
RUN mkdir -p /opt/scr/config/redis
RUN mkdir -p /opt/scr/secrets/redis
RUN echo '{ "host": "redis", "port": 6379 }' > /opt/scr/config/redis/sid-lists.config
RUN echo '{}' | base64 > /opt/scr/secrets/redis/sid-lists.secrets
RUN chown -R sas:sas /opt/scr/config/redis
RUN chown -R sas:sas /opt/scr/secrets/redis

USER sas
#ENV LD_LIBRARY_PATH=/opt/scr/viya/home/SASFoundation/utilities/bin:/opt/scr/viya/home/SASFoundation/sasexe
ENV SAS_SCR_APP_PATH=/scr-redis
