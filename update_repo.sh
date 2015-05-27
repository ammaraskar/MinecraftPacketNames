#!/bin/sh

git pull origin master
python scrape.py
git add -A
git commit -m "Updated files on `date +'%Y-%m-%d %H:%M:%S'`"
git push origin master