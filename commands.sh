#!/usr/bin/env bash

# Run human eval
srun --pty --mem=20000 -t 1-23:58 bash
. ~/parlai.sh
export PYTHONPATH='.'
git pull
python parlai/mturk/tasks/context_evaluator/run.py --live --dataset dream --prompt-type "question and answer quotes"

# Delete HITs
python parlai/mturk/core/scripts/delete_hits.py

# Bonus workers (local)
conda activate parlai2
python parlai/mturk/core/scripts/bonus_workers.py --hit-id

# Reverse rejections
conda activate parlai2
python
from parlai.mturk.core.mturk_manager import MTurkManager
manager = MTurkManager.make_taskless_instance()
manager.approve_work('', override_rejection=True)
manager.approve_assignments_for_hit('', override_rejection=True)

# Copy remote -> local eval files
rsync -rav -e ssh --include '*/' ejp416@access.cims.nyu.edu:~/research/ParlAI/parlai/mturk/core/run_data/live/ ~/research/ParlAI/parlai/mturk/core/run_data/live

A
A
A
A11UBOE8N877JJ | FAILED question and answer quotes/trial/0 | Answered B not A
A1F9KLZGHE9DTA | FAILED question and answer quotes/trial/0 | Answered C not A
A3SWT9MJCQTORQ | FAILED question and answer quotes/trial/0 | Answered C not A
A2YUCJ28XANFOX | FAILED question and answer quotes/trial/0 | Answered C not A
A3LJ2FHESYV9QQ | FAILED question and answer quotes/trial/0 | Answered D not A
ACTBJYB46CJO3  | FAILED question and answer quotes/trial/0 | Answered D not A
AKZ8SFOAI4RZN  | FAILED question and answer quotes/trial/0 | Answered D not A

D
A1D2K63U3LCO3F | FAILED question and answer quotes/trial/1 | Answered A not D
AOWW3URQNRJ6U  | FAILED question and answer quotes/trial/1 | Answered A not D
A2MQ6VUSKCQ9FH | FAILED question and answer quotes/trial/1 | Answered C not D

B
A3LJ2FHESYV9QQ | FAILED question and answer quotes/trial/2 | Answered D not B
AAJ1ZQECDZBEE  | FAILED question and answer quotes/trial/2 | Answered D not B
A1XMTO1NDPOUJ0 | FAILED question and answer quotes/trial/2 | Answered D not B

C
A150GMV1YQWWB3 | FAILED question and answer quotes/trial/3 | Answered A not C
A23YQ8J1DNM084 | FAILED question and answer quotes/trial/3 | Answered A not C
A2YVC1U50H2B4R | FAILED question and answer quotes/trial/3 | Answered B not C
A29RRZYB15066A | FAILED question and answer quotes/trial/3 | Answered B not C
A19ZWBQT8A3LIR | FAILED question and answer quotes/trial/3 | Answered D not C
