#!/bin/bash

# Wait for Oracle
while [ ! -f /mnt/shared/oracle-db-ready ]; do
  echo `date "+%Y-%m-%d %H:%M:%S.%3N"` waiting for /mnt/shared/oracle-db-ready
  sleep 1
done

# Start SCR
/usr/lib/jvm/jre/bin/java -Xrs -cp "/opt/scr/viya/home/solo:/opt/scr/viya/home/solo/lib/*" com.sas.mas.solo.Application -Djava.library.path=/opt/scr/viya/home/SASFoundation/sasexe
