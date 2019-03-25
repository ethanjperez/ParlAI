#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.worlds import validate
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld

import math
from pprint import pprint
import random


class ContextEvaluationOnboardWorld(MTurkOnboardWorld):
    """Example onboarding world. Sends a message from the world to the
    worker and then exits as complete
    """
    def parley(self):
        ad = {}
        ad['id'] = 'System'
        ad['text'] = 'Welcome onboard! We would like to have you answer several questions given some context. ' \
                     'Note that each question you answer is independent from other questions.'
        self.mturk_agent.observe(ad)
        ad['text'] = 'We will be evaluating your answers throughout to check you understand the task ' \
                     '(we won\'t be able to use your work otherwise). ' \
                     'We\'ll also give you a bonus if you do well!'
        self.mturk_agent.observe(ad)
        ad['text'] = 'Type anything to continue.'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act()
        self.episodeDone = True


class ContextEvaluationWorld(MTurkTaskWorld):
    """
    World for recording a turker's question and answer given a context.
    Assumes the context is a random context from a given task, e.g.
    from SQuAD, CBT, etc.
    """

    def __init__(self, opt, task, mturk_agent, evaluation_data):
        self.reward = opt['reward']
        self.task = task
        self.mturk_agent = mturk_agent
        self.evaluation_data = evaluation_data
        self.episodeDone = False
        self.context = None
        self.question = None
        self.answer = None
        self.num_correct_on_labeled = {}
        self.num_collected_on_labeled = {}
        self.accuracy = {}
        self.num_collected = 0
        self.max_collected = len(self.task.examples)
        self.labeled_answer_key = 'eval_labels'
        self.num_changed_responses = None
        self.options = ['A', 'B', 'C', 'D']  # NB: Remove 'D' for DREAM!
        self.options_str = '"A", "B", "C", or "D"'  # NB: Remove 'D' for DREAM!
        self.answer_to_count_by_prompt = {}
        self.durations = {}
        self.reject_work = False
        self.block_worker = False

        random.seed(0)
        if evaluation_data:
            self.num_changed_responses = 0
            debate_modes = list(evaluation_data.keys())
            debate_modes.sort()
            self.example_no_to_debate_mode = [debate_modes[random.randint(0, len(debate_modes) - 1) - opt['option_split_no']] for _ in range(self.max_collected)]
            print(self.example_no_to_debate_mode)

        print(self.mturk_agent.worker_id, "| opt['question_split_no']:", opt['question_split_no'], "| opt['option_split_no']:", opt['option_split_no'])

        # Initial instructions
        ad = {'id': 'System'}
        ad['text'] = 'Welcome! You\'ll be answering ' + str(self.max_collected) + \
                     ' short questions' + (', once without any context and once with some context' if self.evaluation_data else '') + '. ' \
                     '\n\nType anything to continue.'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act()  # Receive acknowledgement

        ad['text'] = 'Bonuses for the following!\n' \
                     '1. Beating random guessing for questions without context.\n' \
                     '2. Beating random guessing noticeably for questions with context.' \
                     '\n\n(Type to continue.)'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act()  # Receive acknowledgement

        ad['text'] = 'Note: Distinct questions are unrelated.' \
                     '\n\n(Type to continue.)'
        self.mturk_agent.observe(ad)
        self.mturk_agent.act()  # Receive acknowledgement

    def parley(self):
        debate_mode = self.example_no_to_debate_mode[self.num_collected] if self.evaluation_data else None

        # Get context from dataset teacher agent
        sample = self.task.act()
        print(self.mturk_agent.worker_id,
              '| qid:', sample['qid'],
              '| debate_mode:', debate_mode,
              '| eval_label:', sample[self.labeled_answer_key])  # Manually add or load eval labels
        self.context = '\n'.join([sample['question']] + sample['options'])

        # Wrap the context with a prompt telling the turker what to do next
        ad = {'episode_done': False, 'id': 'Question ' + str(self.num_collected + 1), 'debate_mode': debate_mode, 'qid': sample['qid']}
        ad['text'] = (self.context + '\n\nWhich option is most likely correct? (' + self.options_str + ')')

        # Question-only evaluation
        question_response = self.prompt_until_valid_response(ad, sample, 'question')

        # Context+Question evaluation
        if self.evaluation_data:
            evaluation_sample = self.evaluation_data[debate_mode][sample['qid']]
            sentences_chosen = '\n'.join([evaluation_sample['sentences_chosen'][0]])  # NB: Always picks first agent
            for punct in {'.', '?', '!', ';', ','}:
                sentences_chosen = sentences_chosen.replace(' ' + punct, punct)
            self.context = sentences_chosen + '\n\n' + self.context
            ad['text'] = (self.context +
                          '\n\nNow which option is most likely correct, given the added context? (' + self.options_str + ')')
            ad['id'] = 'Context ' + str(self.num_collected + 1)
            context_question_response = self.prompt_until_valid_response(ad, sample, 'context_question')
            self.num_changed_responses += (context_question_response != question_response)

        # Terminate episode (if applicable)
        self.num_collected += 1
        if self.num_collected >= self.max_collected:
            ad['id'] = 'System'
            ad['text'] = 'All done!'
            self.mturk_agent.observe(ad)

            ad['text'] = 'How likely are you to recommend this task to a colleague, on a scale of 0-10?'
            self.mturk_agent.observe(ad)
            feedback = self.mturk_agent.act()  # Receive feedback
            if feedback['text'] in self.options:  # Turker is being lazy and just hitting answer options without reading
                self.reject_work = True
                print(self.mturk_agent.worker_id, '| REJECT_WORK:', "feedback['text'] =", feedback['text'])
                self.block_worker = True
                print(self.mturk_agent.worker_id, '| BLOCK_WORKER:', "feedback['text'] =", feedback['text'])

            ad['text'] = 'We\'d love to improve this task for you going forward. '  \
                         'Do you have any feedback or suggestions?'
            self.mturk_agent.observe(ad)
            self.mturk_agent.act()  # Receive feedback

            ad['episode_done'] = True
            self.episodeDone = True

            ad['text'] = 'Thanks for your help!'
            self.mturk_agent.observe(ad)

    def prompt_until_valid_response(self, ad, sample, prompt):
        # Initial prompt
        self.mturk_agent.observe(validate(ad))
        self.answer = self.mturk_agent.act()
        self.answer['text'] = self.answer['text'].upper()

        # Check for improper response
        while self.answer['text'] not in self.options:
            ad['id'] = 'System'
            ad['text'] = 'Please respond with ' + self.options_str
            self.mturk_agent.observe(validate(ad))
            self.answer = self.mturk_agent.act()
            self.answer['text'] = self.answer['text'].upper()

        # Evaluate work
        if self.labeled_answer_key in sample:  # NB: Check self.mturk_agent.metrics
            self.num_correct_on_labeled[prompt] = self.num_correct_on_labeled.get(prompt, 0)
            self.num_correct_on_labeled[prompt] += (self.answer['text'] == sample[self.labeled_answer_key][0])
            self.num_collected_on_labeled[prompt] = self.num_collected_on_labeled.get(prompt, 0)
            self.num_collected_on_labeled[prompt] += 1
            self.accuracy[prompt] = self.num_correct_on_labeled[prompt] / self.num_collected_on_labeled[prompt]
            print(self.mturk_agent.worker_id,
                  prompt.upper(), 'Acc:',
                  self.num_correct_on_labeled[prompt], '/', self.num_collected_on_labeled[prompt])

        # Update answer stats and return
        self.durations[prompt] = self.durations.get(prompt, [])
        self.durations[prompt].append(self.answer['duration'])
        self.answer_to_count_by_prompt[prompt] = self.answer_to_count_by_prompt.get(prompt, {option: 0 for option in self.options})
        self.answer_to_count_by_prompt[prompt][self.answer['text']] += 1
        return self.answer['text']

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.task.shutdown()
        self.mturk_agent.shutdown()

    def review_work(self):
        # Can review the work here to accept or reject it
        # NB: Use self.mturk_agent.metrics?
        if self.num_changed_responses is not None:
            freq_changed_responses = (self.num_changed_responses / self.num_collected)
            if freq_changed_responses <= .2:
                # If you're not updating your response often, you're probably not reading closely
                self.reject_work = True
                print(self.mturk_agent.worker_id, '| REJECT_WORK:', "freq_changed_responses =", freq_changed_responses)
                # If you're really not changing your answer, you're probably spamming
                if freq_changed_responses <= .1:
                    self.block_worker = True
                    print(self.mturk_agent.worker_id, '| BLOCK_WORKER:', "freq_changed_responses =", freq_changed_responses)

        # Turker answer distribution shouldn't be too peaky
        for answer_to_count in self.answer_to_count_by_prompt.values():
            for answer, count in answer_to_count.items():
                freq = count / self.num_collected
                if freq >= .65:
                    self.reject_work = True
                    print(self.mturk_agent.worker_id, '| REJECT_WORK:', answer, "freq =", freq)
                    if freq >= .8:
                        self.block_worker = True
                        print(self.mturk_agent.worker_id, '| BLOCK_WORKER:', answer, "freq =", freq)
                if freq <= 0:
                    self.reject_work = True
                    print(self.mturk_agent.worker_id, '| REJECT_WORK:', answer, "freq =", freq)
                    self.block_worker = True
                    print(self.mturk_agent.worker_id, '| BLOCK_WORKER:', answer, "freq =", freq)

        # Turker should be spending a minimum amount of time on each question
        for prompt, durations in self.durations.items():
            durations.sort()
            median_duration = durations[len(durations) // 2]
            if median_duration <= 3000:
                print(self.mturk_agent.worker_id, '| REJECT_WORK:', "median_duration =", median_duration)
                if median_duration <= 2000:
                    print(self.mturk_agent.worker_id, '| BLOCK_WORKER:', "median_duration =", median_duration)

        print(self.mturk_agent.worker_id, 'Done! | block_worker:', self.block_worker, '| reject_work:', self.reject_work)
        if self.block_worker:
            self.mturk_agent.reject_work('Accuracy')
            self.mturk_agent.block_worker('Accuracy')
        elif self.reject_work:
            self.mturk_agent.reject_work('Accuracy')
        else:
            self.mturk_agent.approve_work()
            if self.accuracy['question'] >= .35:
                # Bonus if you're decently better than random, even with just question+options -only
                self.mturk_agent.pay_bonus(.25 * self.reward, 'Great question-only accuracy!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "self.accuracy['question'] =", self.accuracy['question'])

            if self.accuracy['context_question'] >= .7:
                self.mturk_agent.pay_bonus(.25 * self.reward, 'Great question+context accuracy!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "self.accuracy['context_question'] =", self.accuracy['context_question'])

            if (self.num_changed_responses is not None) and (freq_changed_responses >= .5):
                self.mturk_agent.pay_bonus(.25 * self.reward, 'Great job!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "freq_changed_responses =", freq_changed_responses)

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {
            'context': self.context,
            'acts': [self.question, self.answer],
        }
