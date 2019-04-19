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









 AZ8JL3QNIPY4U | prompt_type: question and answer quotes | response: A | debate_mode: TEST 1 | answer: B | duration: 99.3 | qid: TEST 1
A1HMO9XPRPUPWJ | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: B | duration: 71.9 | qid: TEST 1
 ADZHJZ078THWQ | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: B | duration: 214.3 | qid: TEST 1
A1MZ1EU82NE0PQ | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: B | duration: 68.2 | qid: TEST 1
A3GEYEPOHA33SP | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: B | duration: 93.1 | qid: TEST 1
A250HYHFGXESAC | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: B | duration: 334.6 | qid: TEST 1
A37P8UZ3SAKM7A | prompt_type: question and answer quotes | response: C | debate_mode: TEST 1 | answer: B | duration: 64.8 | qid: TEST 1
A2SKY4RRWII0BF | prompt_type: question and answer quotes | response: C | debate_mode: TEST 1 | answer: B | duration: 348.5 | qid: TEST 1
 ANKDLLQHHM2OH | prompt_type: question and answer quotes | response: D | debate_mode: TEST 1 | answer: B | duration: 26.3 | qid: TEST 1

 A9A2IX3OBORBE | prompt_type: question and answer quotes | response: A | debate_mode: TEST 1 | answer: C | duration: 542.6 | qid: TEST 1
 AVFHRN0S32V2H | prompt_type: question and answer quotes | response: A | debate_mode: TEST 1 | answer: C | duration: 88.3 | qid: TEST 1
A1HMO9XPRPUPWJ | prompt_type: question and answer quotes | response: B | debate_mode: TEST 2 | answer: C | duration: 34.4 | qid: TEST 2
A37P8UZ3SAKM7A | prompt_type: question and answer quotes | response: B | debate_mode: TEST 2 | answer: C | duration: 68.6 | qid: TEST 2
A27SMEOPKV84VI | prompt_type: question and answer quotes | response: B | debate_mode: TEST 2 | answer: C | duration: 58.3 | qid: TEST 2
A222XREQ12K58P | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: C | duration: 96.3 | qid: TEST 1
A250HYHFGXESAC | prompt_type: question and answer quotes | response: B | debate_mode: TEST 2 | answer: C | duration: 27.2 | qid: TEST 2
A1MZ1EU82NE0PQ | prompt_type: question and answer quotes | response: D | debate_mode: TEST 2 | answer: C | duration: 35.6 | qid: TEST 2
A1YIBSKY9U31X6 | prompt_type: question and answer quotes | response: D | debate_mode: TEST 1 | answer: C | duration: 122.7 | qid: TEST 1

A28AX4H70DPKKK | prompt_type: question and answer quotes | response: A | debate_mode: TEST 1 | answer: D | duration: 37.0 | qid: TEST 1
A2J9AHXZBB37XU | prompt_type: question and answer quotes | response: A | debate_mode: TEST 1 | answer: D | duration: 121.3 | qid: TEST 1
A1XBAS3AXLFB5F | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: D | duration: 15.3 | qid: TEST 1
 A4158R4Y06ZB4 | prompt_type: question and answer quotes | response: B | debate_mode: TEST 1 | answer: D | duration: 12.0 | qid: TEST 1
A1BAEFJ2OG7NJ0 | prompt_type: question and answer quotes | response: C | debate_mode: TEST 1 | answer: D | duration: 487.0 | qid: TEST 1
 ADZHJZ078THWQ | prompt_type: question and answer quotes | response: C | debate_mode: TEST 2 | answer: D | duration: 97.6 | qid: TEST 2
 AQ412GI259EPY | prompt_type: question and answer quotes | response: C | debate_mode: TEST 1 | answer: D | duration: 222.3 | qid: TEST 1
A3GEYEPOHA33SP | prompt_type: question and answer quotes | response: C | debate_mode: TEST 2 | answer: D | duration: 14.3 | qid: TEST 2
A19C6T7B0H4PAQ | prompt_type: question and answer quotes | response: C | debate_mode: TEST 1 | answer: D | duration: 61.6 | qid: TEST 1
A1U8HCXVACOGJ8 | prompt_type: question and answer quotes | response: D | debate_mode: TEST 1 | answer: D | duration: 65.7 | qid: TEST 1
A27SMEOPKV84VI | prompt_type: question and answer quotes | response: D | debate_mode: TEST 1 | answer: D | duration: 76.8 | qid: TEST 1






