FROM cr.sas.com/viya-4-x64_oci_linux_2-docker/sas-decisions-runtime-base:1.92.34-20241126.1732642908961

USER root

# Python packages
#RUN pip3 install requests
#ENV LC_ALL=C

# Copy module to container
RUN chown sas:sas /modules
COPY --chown=sas:sas content/_module_definition.json /modules/

USER sas
ENV SAS_SCR_APP_PATH=/scr-solo
