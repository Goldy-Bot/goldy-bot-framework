#!/bin/sh
/wait
cd ./goldy
python ../cli.py setup
rm .env
rm run.py
python ../run.py