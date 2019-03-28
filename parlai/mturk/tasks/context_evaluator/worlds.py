#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.core.worlds import validate
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld

import random
import time


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
        self.question_split_no = opt['question_split_no']
        self.option_split_no = opt['option_split_no']
        self.task = task
        self.mturk_agent = mturk_agent
        self.evaluation_data = evaluation_data
        self.episodeDone = False
        self.contexts = []
        self.responses = []
        self.qids = []
        self.data = []
        self.num_correct_on_labeled = {}
        self.num_collected_on_labeled = {}
        self.accuracy = {}
        self.num_collected = 0
        self.num_tested = 0
        self.max_collected = len(self.task.examples)
        self.num_changed_responses = None
        self.num_debate_mode_responses = None
        self.options = ['A', 'B', 'C', 'D']  # NB: Remove 'D' for DREAM!
        self.answer_to_count_by_prompt = {}
        self.durations = {}
        self.reject_reasons = []
        self.block_reasons = []
        self.task_rating = None
        self.feedback = None
        self.include_q_only_eval = False
        self.bonus_acc_threshold = {
            'context_question': .5,
            'question': .35,
        }
        self.debate_mode_to_option = {'Ⅰ': 'A', 'Ⅱ': 'B', 'Ⅲ': 'C', 'Ⅳ': 'D'}

        random.seed(0)
        if evaluation_data:
            self.num_changed_responses = 0
            self.num_debate_mode_responses = 0
            possible_debate_modes = list(evaluation_data.keys())
            possible_debate_modes.sort()
            self.sample_debate_modes = [possible_debate_modes[random.randint(0, len(possible_debate_modes) - 1) - opt['option_split_no']] for _ in range(self.max_collected)]
            print(self.sample_debate_modes)

        self.num_test_turns = 0  # 2
        self.test_turns = []
        self.test_questions = {}
        if self.num_test_turns == 2:
            self.test_turns = [1, self.max_collected + self.num_test_turns]
            self.test_questions = {
                1: {
                    'text': '"We taught you this just last week!"\n\n' +
                            'Based on the passage, what does the student not know that the teacher expects him to know for the exam?\n' +
                            'A. 13 + 12 = 35\n' +
                            'B. 15 / 5 = 4\n' +
                            'C. 41 - 22 = 18\n' +
                            'D. 6 x 4 = 24',
                    'answer': 'D'
                },
                self.max_collected + self.num_test_turns: {
                    'text': '"Wow, I never knew a banana could be that color."\n\n' +
                            'When Fred opens his pantry, he is surprised the banana is not colored _.\n' +
                            'A. Gray-ish blue\n' +
                            'B. Purple and pink\n' +
                            'C. Green or yellow\n' +
                            'D. Plain white',
                    'answer': 'C'
                },
            }
        for example_no in self.test_questions.keys():
            self.test_questions[example_no]['id'] = 'New Context and Question (#' + str(example_no) + ')'
        assert self.num_test_turns == len(self.test_turns), 'self.num_test_turns != len(self.test_turns)'

        print(self.mturk_agent.worker_id,
              "| question_split:", opt['question_split_no'],
              "| option_split:", opt['option_split_no'],
              '| assignment_id:', self.mturk_agent.assignment_id)

    def parley(self):
        example_no = self.num_collected + self.num_tested + 1

        # Verify work quality with a test question
        if example_no in self.test_questions.keys():
            ad = self.test_questions[example_no]
            response = self.prompt_and_receive_response(ad, 'context_question', None)
            if ad['answer'] != response:
                reason = 'Test failed: Example ' + str(example_no) + ' - Answered ' + response + ' not ' + (ad['answer'] if ad['answer'] is not None else ad['text'])
                # self.reject_reasons.append(reason)
            self.num_tested += 1
            return
        elif example_no > (self.max_collected + self.num_test_turns):
            ad = {}
            ad['id'] = 'System'
            ad['text'] = 'All done!'
            self.mturk_agent.observe(ad)

            ad['text'] = 'How likely are you to recommend this task to a colleague?'
            ad["task_data"] = {
                "respond_with_form": [
                    {
                        "type": "choices",
                        "question": "On a scale of 0-10",
                        "choices": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
                    }
                ]
            }
            self.mturk_agent.observe(ad)
            time.sleep(.5)
            task_rating_answer = self.mturk_agent.act()  # Receive task rating
            task_rating = task_rating_answer['task_data']['form_responses'][0]['response']
            # if task_rating in self.options:  # Turker is just hitting answer options without reading
            #     self.reject_reasons.append('task_rating = ' + str(task_rating))

            ad['text'] = 'How can we improve this task?'
            ad["task_data"] = {"respond_with_form": None}
            self.mturk_agent.observe(ad)
            feedback_answer = self.mturk_agent.act()  # Receive general text feedback
            self.feedback = feedback_answer['text']
            print(self.mturk_agent.worker_id, '| task_rating:', task_rating, '| feedback:', self.feedback)

            ad['episode_done'] = True
            self.episodeDone = True

            ad['text'] = 'Thanks for your help!'
            self.mturk_agent.observe(ad)
            return
        else:
            # Get context from dataset teacher agent
            sample = self.task.act()
            debate_mode = self.sample_debate_modes[self.num_collected] if self.evaluation_data else None
            sample['debate_mode'] = debate_mode
            context = '\n'.join([sample['question']] + sample['options'])

            ad = {'episode_done': False}

            # Question-only evaluation
            if self.include_q_only_eval:
                ad['id'] = 'New Question (#' + str(example_no) + ')'
                ad['text'] = context
                question_response = self.prompt_and_receive_response(ad, 'question', sample)
                if question_response is None:
                    return

            # Context+Question evaluation
            if self.evaluation_data:
                evaluation_sample = self.evaluation_data[debate_mode][sample['qid']]
                sentences_chosen = '\n'.join([evaluation_sample['sentences_chosen'][0]])  # NB: Always picks first agent
                for punct in {'.', '?', '!', ';', ','}:
                    sentences_chosen = sentences_chosen.replace(' ' + punct, punct)
                context = sentences_chosen + '\n\n' + context
                sample['sentences_chosen'] = sentences_chosen
                ad['text'] = context
                ad['id'] = 'New Context and Question (#' + str(example_no) + ')'
                context_question_response = self.prompt_and_receive_response(ad, 'context_question', sample)
                if context_question_response is None:
                    return
                if self.include_q_only_eval:
                    self.num_changed_responses += (context_question_response != question_response)
                if debate_mode is not None:
                    self.num_debate_mode_responses += (context_question_response == self.debate_mode_to_option[debate_mode])

            # Terminate episode (if applicable)
            self.num_collected += 1
            return

    def prompt_and_receive_response(self, ad, prompt, sample=None):
        ad["task_data"] = {"respond_with_form": [{
            "type": "choices",
            "question": "Which option is most likely correct?",
            "choices": ["A", "B", "C", "D"]
        }]}
        self.mturk_agent.observe(validate(ad))

        time.sleep(.5)
        answer = self.mturk_agent.act()
        if 'task_data' not in answer:
            print(self.mturk_agent.worker_id, '| DISCONNECT:', answer)
            self.episodeDone = True
            return None
        response = answer['task_data']['form_responses'][0]['response']

        if sample is not None:
            self.responses.append(response)
            # Evaluate work on non-qualifying questions
            if 'eval_labels' in sample:  # NB: Check self.mturk_agent.metrics
                self.num_correct_on_labeled[prompt] = self.num_correct_on_labeled.get(prompt, 0)
                self.num_correct_on_labeled[prompt] += (response == sample['eval_labels'][0])
                self.num_collected_on_labeled[prompt] = self.num_collected_on_labeled.get(prompt, 0)
                self.num_collected_on_labeled[prompt] += 1
                self.accuracy[prompt] = self.num_correct_on_labeled[prompt] / self.num_collected_on_labeled[prompt]

            # Update answer stats and return
            self.durations[prompt] = self.durations.get(prompt, [])
            self.durations[prompt].append(answer['duration'])
            self.answer_to_count_by_prompt[prompt] = self.answer_to_count_by_prompt.get(prompt, {option: 0 for option in self.options})
            self.answer_to_count_by_prompt[prompt][response] += 1
            self.data.append({
                'sample': sample,
                'context': ad['text'],
                'response': response,
                'duration': answer['duration'],
            })

        print(self.mturk_agent.worker_id,
              '| prompt:', prompt,
              '| response:', response,
              '| debate_mode:', sample['debate_mode'] if sample is not None else 'TEST',
              '| duration:', round(answer['duration'] / 1000., 1),
              '| qid:', sample['qid'] if sample is not None else 'TEST',
              '' if (sample is None) or ('eval_labels' not in sample) else
              '| accuracy: ' + str(self.num_correct_on_labeled[prompt]) + '/' + str(self.num_collected_on_labeled[prompt]))
        return response

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.task.shutdown()
        self.mturk_agent.shutdown()

    def review_work(self):
        # Can review the work here to accept or reject it
        if self.include_q_only_eval and (self.num_changed_responses is not None):
            freq_changed_responses = (self.num_changed_responses / self.num_collected)
            if freq_changed_responses <= .2:  # Not reading closely
                reason = 'freq_changed_responses = ' + str(freq_changed_responses)
                self.reject_reasons.append(reason)
                if freq_changed_responses <= .1:  # Spamming
                    self.block_reasons.append(reason)

        # Turker should be spending a minimum amount of time on each question
        median_durations = []
        for prompt, durations in self.durations.items():
            durations.sort()
            median_duration = durations[len(durations) // 2]
            median_durations.append(median_duration)
            if median_duration <= 5000:
                reason = 'median_duration = ' + str(median_duration)
                self.reject_reasons.append(reason)
                if median_duration <= 2500:
                    self.block_reasons.append(reason)

        # Turker answer distribution shouldn't be too peaky
        for answer_to_count in self.answer_to_count_by_prompt.values():
            for answer, count in answer_to_count.items():
                freq = count / self.num_collected
                reason = answer + ' freq = ' + str(freq)
                if freq >= .7:
                    self.reject_reasons.append(reason)
                    if freq >= .85:
                        self.block_reasons.append(reason)
                # if (freq <= 0) and (min(median_durations) <= 10000):
                #     self.reject_reasons.append(reason)

        print(self.mturk_agent.worker_id, 'Done! | num_debate_mode_responses:', self.num_debate_mode_responses, '/', self.num_collected,
              '| block_reasons:', self.block_reasons,
              '| reject_reasons:', self.reject_reasons)
        if len(self.block_reasons) > 0:
            self.mturk_agent.reject_work('Accuracy')
            self.mturk_agent.block_worker('Accuracy')
        elif len(self.reject_reasons):
            # TODO: Add soft block: mturk_manager.soft_block_worker(self.mturk_agent.worker_id) after setting --block-qualification
            self.mturk_agent.reject_work('Accuracy')
        else:
            self.mturk_agent.approve_work()
            bonus_amount = round(.5 * self.reward, 2)

            if ('context_question' in self.accuracy) and (self.accuracy['context_question'] >= self.bonus_acc_threshold['context_question']):
                self.mturk_agent.pay_bonus(bonus_amount, 'Great accuracy!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "self.accuracy['context_question'] =", self.accuracy['context_question'])

            if ('question' in self.accuracy) and (self.accuracy['question'] >= self.bonus_acc_threshold['question']):
                # Bonus if you're decently better than random, even with just question+options -only
                self.mturk_agent.pay_bonus(bonus_amount, 'Great accuracy!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "self.accuracy['question'] =", self.accuracy['question'])

            if self.include_q_only_eval and (self.num_changed_responses is not None) and (freq_changed_responses >= .5):
                self.mturk_agent.pay_bonus(bonus_amount, 'Great job overall!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "freq_changed_responses =", freq_changed_responses)

    def get_custom_task_data(self):
        # brings important data together for the task, to later be used for
        # creating the dataset. If data requires pickling, put it in a field
        # called 'needs-pickle'.
        return {
            'data': self.data,
            'worker_id': self.mturk_agent.worker_id,
            'assignment_id': self.mturk_agent.assignment_id,
            'task_rating': self.task_rating,
            'feedback': self.feedback,
            'reject_reasons': self.reject_reasons,
            'block_reasons': self.block_reasons,
            'accuracy': self.accuracy,
            'question_split_no': self.question_split_no,
            'option_split_no': self.option_split_no,
        }
