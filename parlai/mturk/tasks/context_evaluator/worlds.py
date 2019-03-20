#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.worlds import validate
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld

from pprint import pprint


class ContextEvaluationOnboardWorld(MTurkOnboardWorld):
    """Example onboarding world. Sends a message from the world to the
    worker and then exits as complete
    """
    def parley(self):
        ad = {}
        ad['id'] = 'System'
        ad['text'] = 'Welcome onboard! We would like to have you answer 9 questions given some (partial) context. ' \
                     'We will be evaluating your answers to check you understand the task ' \
                     '(we won\'t be able to use your work otherwise). ' \
                     'We\'ll also give you a bonus if you do well! ' \
                     '\n\nType anything to continue.'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act()
        self.episodeDone = True


class ContextEvaluationWorld(MTurkTaskWorld):
    """
    World for recording a turker's question and answer given a context.
    Assumes the context is a random context from a given task, e.g.
    from SQuAD, CBT, etc.
    """

    collector_agent_id = 'Context'

    def __init__(self, opt, task, mturk_agent, evaluation_data):
        self.task = task
        self.mturk_agent = mturk_agent
        self.evaluation_data = evaluation_data
        self.episodeDone = False
        self.context = None
        self.question = None
        self.answer = None
        self.num_correct_on_labeled = 0
        self.num_collected_on_labeled = 0
        self.accuracy = 0.
        self.num_collected = 0
        self.max_collected = 9

    def parley(self):
        # Each turn starts from the Context Evaluator agent
        ad = {'episode_done': False}
        ad['id'] = self.__class__.collector_agent_id

        # At the first turn, the Context Evaluator agent provides the context
        # and prompts the turker to ask a question regarding the context

        # Get context from dataset teacher agent
        qa = self.task.act()
        pprint(qa)
        print(qa['eval_labels'])
        evaluation_sample = self.evaluation_data[qa['qid']]
        sentences_chosen = '\n'.join([evaluation_sample['sentences_chosen'][0]])
        for punct in {'.', '?', '!', ';', ','}:
            sentences_chosen = sentences_chosen.replace(' ' + punct, punct)
        self.context = '\n'.join([sentences_chosen, '\n', qa['question']] + qa['options'])

        # Wrap the context with a prompt telling the turker what to do next
        ad['text'] = (self.context +
                      '\nWhich option is most likely correct, given this context and question? ("A", "B", "C", or "D")')

        self.mturk_agent.observe(validate(ad))
        self.answer = self.mturk_agent.act()

        while self.answer['text'] not in {'A', 'B', 'C', 'D'}:
            ad['text'] = 'Please respond with "A", "B", "C", or "D"'
            self.mturk_agent.observe(validate(ad))
            self.answer = self.mturk_agent.act()

        # Evaluate work
        labeled_answer_key = 'eval_labels'
        if labeled_answer_key in qa:  # NB: Check self.mturk_agent.metrics
            self.num_collected_on_labeled += 1
            self.num_correct_on_labeled += (self.answer['text'] == qa[labeled_answer_key][0])
            self.accuracy = self.num_correct_on_labeled / self.num_collected_on_labeled
            print('Accuracy:', self.accuracy)

        # Terminate episode (if applicable)
        self.num_collected += 1
        if self.num_collected >= self.max_collected:
            ad['episode_done'] = True
            self.episodeDone = True
            ad['text'] = 'You have completed our task!'
            self.mturk_agent.observe(validate(ad))

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.task.shutdown()
        self.mturk_agent.shutdown()

    def review_work(self):
        # Can review the work here to accept or reject it
        # NB: Use self.mturk_agent.metrics
        if self.accuracy < .35:
            self.mturk_agent.reject_work('poor_performance')
            self.mturk_agent.block_worker('poor_performance')
        elif self.accuracy < .75:
            self.mturk_agent.reject_work('poor_performance')
        else:
            self.mturk_agent.approve_work()
            if self.accuracy >= .85:
                self.mturk_agent.pay_bonus(.25, 'strong_performance')

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {
            'context': self.context,
            'acts': [self.question, self.answer],
        }
