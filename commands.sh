#!/usr/bin/env bash

# Run human eval
srun --pty --mem=20000 -t 1-23:58 bash
. ~/parlai.sh
export PYTHONPATH='.'
python parlai/mturk/tasks/context_evaluator/run.py --live --prompt-type question
