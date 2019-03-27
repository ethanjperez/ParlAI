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

Often the answer will be tough to determine. Here, just give your best guess.<br><br>

<b>Number of questions in HIT</b>: 19-20 questions<br>
<b>Estimated Time</b>: 11 minutes<br>
<b>Accuracy Bonus</b>: Up to 50% of HIT value for 70+% answering accuracy<br>
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
    'evaluation_data_dir': '../allennlp/eval/tfidf.o/dev',  # , 'debate_logs.d=A_B.json', 'debate_logs.d=B.json', etc.
    'question_splits': 5,  # max num Q's per passage
    'num_options': 4,
}

"""
Guess a question's answer in 2 settings:<br>
1. Without any of the necessary context to answer the question.<br>
2. With some context sentence(s) that may or may not cause you to change your answer.<br><br>

Often the answer will be tough to determine (especially without any context). Here, just give your best guess.<br><br>

<b>Estimated Time</b> (all questions in HIT): 11 minutes.<br>
<b>Accuracy Bonus</b>: Up to $1.5/HIT<br>
<b>Payout</b>: Immediate<br><br>

<b>------------------- EXAMPLE -------------------</b> <br><br>
<b>Question</b>:<br>
What does the doctor think of Heelys?<br>
A: They are too expensive to buy.<br>
B: They are too fast to go.<br>
C: They are bad for kids' health.<br>
D: They are good for training.<br><br>

Which option is most likely correct?<br><br>
<b>Evaluator</b>:<br>D<br><br>

<b>Context</b>: "Wearing Heelys for a long time could stop young people from developing their legs."<br><br>

What does the doctor think of Heelys?<br>
A: They are too expensive to buy.<br>
B: They are too fast to go.<br>
C: They are bad for kids' health.<br>
D: They are good for training.<br><br>

Now which option is most likely correct, given the added context?<br><br>
<b>Guesser</b>:<br>
C
"""
