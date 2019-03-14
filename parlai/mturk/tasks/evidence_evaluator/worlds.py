#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.worlds import validate
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld

from pprint import pprint


class EvidenceEvaluationOnboardWorld(MTurkOnboardWorld):
    '''Example onboarding world. Sends a message from the world to the
    worker and then exits as complete
    '''
    def parley(self):
        ad = {}
        ad['id'] = 'System'
        ad['text'] = 'Welcome onboard!'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act()
        self.episodeDone = True


class EvidenceEvaluationWorld(MTurkTaskWorld):
    """
    World for recording a turker's question and answer given a context.
    Assumes the context is a random context from a given task, e.g.
    from SQuAD, CBT, etc.
    """

    collector_agent_id = 'Evidence Evaluator'

    def __init__(self, opt, task, mturk_agent, evaluation_data):
        self.task = task
        self.mturk_agent = mturk_agent
        self.evaluation_data = evaluation_data
        self.episodeDone = False
        self.turn_index = -1
        self.context = None
        self.question = None
        self.answer = None
        self.max_collected = 20

    def parley(self):
        # Each turn starts from the Evidence Evaluator agent
        ad = {'episode_done': False}
        ad['id'] = self.__class__.collector_agent_id

        # At the first turn, the Evidence Evaluator agent provides the context
        # and prompts the turker to ask a question regarding the context

        # Get context from dataset teacher agent
        qa = self.task.act()
        pprint(qa)
        # evaluation_sample = evaluation_data[qa['qid']]  # TODO: Serve evaluation_sample
        self.context = '\n'.join(qa['text'].split('\n'))

        # Wrap the context with a prompt telling the turker what to do next
        ad['text'] = ('\n' + self.context +
                      '\n\nGiven the context, which answer is most likely to be correct? (A, B, C, or D)')

        if self.turn_index >= self.max_collected:
            ad['episode_done'] = True  # end of episode

        self.mturk_agent.observe(validate(ad))
        self.answer = self.mturk_agent.act()

        if self.turn_index >= self.max_collected:
            self.episodeDone = True

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.task.shutdown()
        self.mturk_agent.shutdown()

    def review_work(self):
        # Can review the work here to accept or reject it
        pass

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {
            'context': self.context,
            'acts': [self.question, self.answer],
        }
