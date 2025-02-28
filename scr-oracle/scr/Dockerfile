FROM cr.sas.com/viya-4-x64_oci_linux_2-docker/sas-decisions-runtime-components:1.72.34-20241126.1732642899957 AS base
FROM cr.sas.com/viya-4-x64_oci_linux_2-docker/sas-decisions-runtime-base:1.92.34-20241126.1732642908961

USER root

# Python packages
#RUN pip3 install requests
#ENV LC_ALL=C

# Copy module to container
RUN chown sas:sas /modules
COPY --chown=sas:sas content/_module_definition.json /modules/

# Add Oracle binaries
COPY --from=base /oracle /

# Copy oracle config + connection string
COPY --chown=sas:sas content/db.config /opt/scr/config/db/
COPY --chown=sas:sas content/conn.str /opt/scr/secrets/db/
COPY --chown=sas:sas --chmod=777 content/startup.sh /opt/scr/startup.sh

USER sas
# Base 64 encode connection string
RUN base64 -w 0 /opt/scr/secrets/db/conn.str > /opt/scr/secrets/db/db.secrets

ENV ORACLE_HOME=/usr/lib/oracle/19.13/client64 ORAENV_ASK=NO SASORA=V9 TWO_TASK=ORACLE_SID
ENV LD_LIBRARY_PATH=/opt/scr/viya/home/SASFoundation/utilities/bin:/opt/scr/viya/home/SASFoundation/sasexe:/usr/lib64:/usr/lib/oracle/19.13/client64/lib
ENV SAS_SCR_APP_PATH=/scr-oracle
