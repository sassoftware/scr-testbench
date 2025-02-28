#FROM container-registry.oracle.com/database/free:latest
FROM container-registry.oracle.com/database/free:23.6.0.0-lite

USER root

# Add build scripts
COPY --chown=oracle:orcale scripts/startup/01_build.sh /opt/oracle/scripts/startup/01_build.sh
COPY --chown=oracle:orcale scripts/build /opt/oracle/scripts/build

USER oracle
ENV ORACLE_PWD=tiger

# Start Oracle and run build scripts
RUN /opt/oracle/runOracle_slim.sh --nowait

# Remove build scripts
RUN rm /opt/oracle/scripts/startup/01_build.sh
RUN rm -rf /opt/oracle/scripts/startup/build

#CMD [ "sleep", "50000" ]