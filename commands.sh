#!/usr/bin/env bash

# Run human eval
srun --pty --mem=20000 -t 1-23:58 bash
. ~/parlai.sh
export PYTHONPATH='.'
python parlai/mturk/tasks/context_evaluator/run.py --live --dataset dream

python parlai/mturk/core/scripts/bonus_workers.py --hit-id

rsync -rav -e ssh --include '*/' ejp416@access.cims.nyu.edu:~/research/ParlAI/parlai/mturk/core/run_data/live/ ~/research/ParlAI/parlai/mturk/core/run_data/live
