#!/bin/bash

# wait for redis
until redis-cli ping
do
  sleep 0.5
done

# load cars data
sleep 0.5
redis-cli < /opt/scripts/cars.redis
