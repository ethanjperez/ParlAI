#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_config = {
    'frontend_version': 1,
    'hit_title': 'Guess the answer!',
    'hit_description': 'Guess the answer given some context.',
    'hit_keywords': 'reading,question,answer',
    #     'task_description': """
    # In this task, you will guess the answer to a question, given some related context.<br><br>
    # Sometimes, the context may directly answer the question.
    # Other times, it may be unhelpful or vaguely suggest a few answers.
    # In this case, just give your best guess.<br><br>
    # Example:<br><br>
    # ------------------- Task Begin ------------------- <br><br>
    # <b>Context</b>:<br>
    # "Wearing Heelys for a long time could stop young people from developing their legs."<br><br>
    #
    # What does the doctor think of Heelys?<br>
    # A: They are too expensive to buy.<br>
    # B: They are too fast to go.<br>
    # C: They are bad for kids' health.<br>
    # D: They are good for training.<br><br>
    #
    # Which answer does the evidence support? (A, B, C, or D)
    # <br><br>
    # <b>Evaluator</b>:<br>
    # C<br><br>
    # ------------------- Task Done ------------------- <br><br>
    # If you are ready, please click "Accept HIT" to start this task.
    # """,
    'task_description': """
In this task, you will guess the answer to a question.<br><br>
Often the answer will be inherently difficult to determine. In this case, just give your best guess.<br><br>
Example:<br><br>
------------------- Task Begin ------------------- <br><br>
<b>Question</b>:<br>

What does the doctor think of Heelys?<br>
A: They are too expensive to buy.<br>
B: They are too fast to go.<br>
C: They are bad for kids' health.<br>
D: They are good for training.<br><br>

Which answer does the evidence support? (A, B, C, or D)
<br><br>
<b>Evaluator</b>:<br>
C<br><br>
------------------- Task Done ------------------- <br><br>
If you are ready, please click "Accept HIT" to start this task.
""",
    'evaluation_data_filename': None,  # 'debate_logs.d=A_B.json', 'debate_logs.d=B.json', etc.
    'num_splits': 5,
    'split_no': 0,
}
