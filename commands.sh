#!/usr/bin/env bash

# Run human eval
srun --pty --mem=20000 -t 1-23:58 bash
. ~/parlai.sh
export PYTHONPATH='.'
git pull
python parlai/mturk/tasks/context_evaluator/run.py  --dataset race --prompt-type "quotes and question" --live
python parlai/mturk/tasks/context_evaluator/run.py --dataset dream --prompt-type "quote and question" --live

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
