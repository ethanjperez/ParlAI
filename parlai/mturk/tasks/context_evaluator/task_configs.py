#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

task_configs = {
    'general': {
        'block_qualification': 'poor performance',
        'count_complete': True,
        'max_time': 7200,
        'max_time_qual': 'max time',
        'frontend_version': 1,
        'hit_title': 'Guess the answer!',  # Passage comprehension [with just quotes / without the passage]
        'hit_keywords': 'reading,question,answer',
        'mturk_agent_id': 'Guesser',
        'question_splits': 5,  # max Q's/passage in 'datatype' field directory
    },
    'race': {
        'datatype': 'dev.num_passages=13',
        'num_conversations': 100,
        'num_options': 4,
        'unique_qual_name': 'tfidf4',
    },
    'dream': {
        'datatype': 'test.num_questions=100',
        'num_conversations': 75,
        'num_options': 3,
        'unique_qual_name': 'dream',
    },
    'live': {
        'allowed_conversations': 1,
        # 'disconnect_qualification': 'disconnect_tfidf',
        'hobby': True,
        'max_hits_per_worker': 1,
        'unique_worker': True,
    },
    'sandbox': {
        'allowed_conversations': 100,
        'hobby': False,
        'max_hits_per_worker': 100,
    },
    'quote and question': {
        'evaluation_data_dir': '../allennlp/eval/dream/sl-sents/test',
        'reward': 1.12,  # RACE: 1.5, 11m, .75 bonus
        'hit_description': 'Can you answer passage comprehension questions using just a quote?',
        'task_description': """
            <b>Your Goal</b>: See how well you can guess the answers to passage-comprehension exam questions, given just a quote from the passage.
            You\'ll get a bonus if you do well!<br><br>
            
            <b>Our Goal</b>: We\'re trying to evaluate how important various passage sentences are for answering each question.<br><br>
            
            <font color="blue"><b>IMPORTANT</b></font>: Our setup inherently makes many questions nonsensical or impossible to answer. For these questions, just give your best guess! The task is meant to be fun.<br><br>
            
            <b>Questions in HIT</b>: 20<br>
            <b>Time</b>: 8 minutes<br>
            <b>Bonus</b>: $0.56 for exceeding average worker accuracy<br>
            <b>Payout</b>: Immediate<br>
            <b>Qualifying</b>: Must pass 3 trial questions first. We have the right to reject work for workers who pass the qualifier but provide spam on the real HIT.<br><br>
            
            <b>------------------- EXAMPLE -------------------</b> <br><br>
            <b>Passage quote and question</b>:<br>
            "Wearing Heelys for a long time could stop young people from developing their legs."<br><br>
            
            What does the doctor think of Heelys?<br><br>
            
            A: They are too expensive to buy.<br>
            B: They are too fast to go.<br>
            C: They are bad for kids' health.<br>
            D: They are good for training.<br><br>
            
            Which option is most likely correct?<br>
            <b>Guesser</b>: C
        """
    },
    'question': {
        'evaluation_data_dir': None,
        'num_conversations': 25,
        'reward': 1.0,  # DREAM: .76, 5 min, .37 bonus
        'hit_description': 'Can you answer passage comprehension questions without the passage?',
        'task_description': """
            <b>Your Goal</b>: See how well you can answer passage-comprehension exam questions, without the passage - just the question and answer options.
            You\'ll get a bonus if you do well!<br><br>
            
            <b>Our Goal</b>: We\'re trying to evaluate how well people can do on reading comprehension exams without reading the passage. Options can often be eliminated by common sense, general knowledge, or the question/option phrasing; if you read closely, you should do notably better than random guessing.<br><br>
            
            <font color="blue"><b>IMPORTANT</b></font>: Our setup inherently makes some questions nonsensical or impossible to answer. For these questions, just give your best guess! The task is meant to be fun.<br><br>
            
            <b>Questions in HIT</b>: 20<br>
            <b>Time</b>: 7 minutes<br>
            <b>Bonus</b>: $0.50 for exceeding average worker accuracy<br>
            <b>Payout</b>: Immediate<br>
            <b>Qualifying</b>: Must pass 3 trial questions first. We have the right to reject work for workers who pass the qualifier but provide spam on the real HIT.<br><br>
            
            <b>------------------- EXAMPLE -------------------</b> <br><br>
            <b>Question</b>:<br>
            What does the doctor think of Heelys?<br><br>
            
            A: They are too expensive to buy.<br>
            B: They are too fast to go.<br>
            C: They are bad for kids' health.<br>
            D: They are good for training.<br><br>
            
            Which option is most likely correct?<br>
            <b>Guesser</b>: D
        """
    },
}
