#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_config = {}


task_config['frontend_version'] = 1

"""A short and descriptive title about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT title appears in search results,
and everywhere the HIT is mentioned.
"""
task_config['hit_title'] = 'Evaluate the evidence for an answer to a question'


"""A description includes detailed information about the kind of task the HIT contains.
On the Amazon Mechanical Turk web site, the HIT description appears in the expanded
view of search results, and in the HIT and assignment screens.
"""
task_config['hit_description'] = 'Evaluate the evidence for an answer to a question.'


"""One or more words or phrases that describe the HIT, separated by commas.
On MTurk website, these words are used in searches to find HITs.
"""
task_config['hit_keywords'] = 'reading,question,answer'


"""A detailed task description that will be shown on the HIT task preview page
and on the left side of the chat page. Supports HTML formatting.
"""
task_config['task_description'] = \
'''
In this task, you will be evaluating which answer the context supports.<br><br>
Example:<br><br>
------------------- Task Begin ------------------- <br><br>
<b>Evidence</b>:<br>
"Wearing Heelys for a long time could stop young people from developing their legs."<br><br>

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
'''
