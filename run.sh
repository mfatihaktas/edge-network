#!/bin/bash
echo $1 $2 $3

PY=python3

if [ $1 = 'e' ]; then
  $PY exp.py
elif [ $1 = 'r' ]; then
  $PY rvs.py
elif [ $1 = 's' ]; then
  $PY sching_utils.py
elif [ $1 = 'ts' ]; then
  $PY test_sim.py
else
  echo "Arg did not match!"
fi
