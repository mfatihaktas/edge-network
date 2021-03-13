#!/bin/bash
echo $1 $2 $3

PY=python3

if [ $1 = 'e' ]; then
  $PY exp.py
elif [ $1 = 'r' ]; then
  $PY rvs.py
else
  echo "Arg did not match!"
fi
