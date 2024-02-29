#!/bin/sh
/wait

goldy-bot setup --path ./goldy
rm ./goldy/.env

cd ./goldy
goldy-bot start