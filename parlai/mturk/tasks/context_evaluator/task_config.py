#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_config = {
    'frontend_version': 1,
    'hit_title': 'Guess the answer!',
    'hit_description': 'Guess the answer given some context.',
    'hit_keywords': 'reading,question,answer',
    'task_description': """
Guess a question's answer, given a context sentence that may or may not influence your answer.<br><br>

These questions are from passage-based reading comprehension exams. You\'ll answer these questions without the full passage, only a quote from it. We are trying to evaluate how helpful or unhelpful various sentences are for each question.<br><br>

<b>NOTE</b>: As a result, questions often appear nonsensical, or the answer may be outright <i>impossible</i> to determine. Here, don\'t stress - just give your best guess! The task is meant to be fun not frustrating. We\'ve also set this task\'s bonus criteria lower to account for the difficulty.<br><br>

<b>Questions in HIT</b>: 19-20<br>
<b>Time</b>: 11 minutes<br>
<b>Accuracy Bonus</b>: Up to 50% of HIT value for over 50% answering accuracy<br>
<b>Payout</b>: Immediate<br><br>

<b>------------------- EXAMPLE -------------------</b> <br><br>
<b>Context and Question</b>: "Wearing Heelys for a long time could stop young people from developing their legs."<br><br>

What does the doctor think of Heelys?<br>
A: They are too expensive to buy.<br>
B: They are too fast to go.<br>
C: They are bad for kids' health.<br>
D: They are good for training.<br><br>

Which option is most likely correct?<br>
<b>Guesser</b>: C
""",
    'evaluation_data_dir': '../allennlp/eval/fasttext.o/dev',  # , 'debate_logs.d=A_B.json', 'debate_logs.d=B.json', etc.
    'question_splits': 5,  # max num Q's per passage
    'num_options': 4,
}
