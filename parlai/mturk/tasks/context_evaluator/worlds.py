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
    def __init__(self, opt, mturk_agent):
        # MTurkOnboardWorld init
        self.mturk_agent = mturk_agent
        self.episodeDone = False

        self.passed_test = None
        self.cur_example_no = 1
        self.options = ['A', 'B', 'C', 'D'][:opt['num_options']]
        self.prompt_types = [opt['prompt_type']]
        self.test_questions = {
            'question': [
                {
                    'text': 'When Fred opens his pantry, he is surprised the banana is not colored _.\n\n' +
                            'A. Gray-ish blue\n' +
                            'B. Purple and pink\n' +
                            'C. Green or yellow\n' +
                            'D. Plain white',
                    'answer': 'C',
                    'qid': 'question/trial/0',
                },
                {
                    'text': 'He who considers himself to be better and more important than others is likely to _.\n\n' +
                            'A. have his head in the clouds\n' +
                            'B. be easy to deal with\n' +
                            'C. have "common sense"\n' +
                            'D. have a "big head"',
                    'answer': 'D',
                    'qid': 'question/trial/1',
                },
                {
                    'text': 'What does Alan\'s grandfather do every Sunday?\n\n' +
                            'A. He hosts crazy parties.\n' +
                            'B. He studies for the medical school entrance exam.\n' +
                            'C. He flies to Hawaii and back.\n' +
                            'D. He goes to church with his wife.',
                    'answer': 'D',
                    'qid': 'question/trial/2',
                },
            ],
            'quote and question': [
                {
                    'text': '"Wow, I never knew a banana could be that color."\n\n' +
                            'When Fred opens his pantry, he is surprised the banana is not colored _.\n\n' +
                            'A. Gray-ish blue\n' +
                            'B. Purple and pink\n' +
                            'C. Green or yellow\n' +
                            'D. Plain white',
                    'answer': 'C',
                    'qid': 'quote and question/trial/0',
                },
                {
                    'text': 'The film Schindler\'s List also takes place during World War Two.\n\n' +
                            'What\'s the similarity between Saving Private Ryan and Schindler\'s List?\n\n' +
                            'A. They are both humorous.\n' +
                            'B. They were released at the same time.\n' +
                            'C. They are both American movies.\n' +
                            'D. They both happen during World War Two.',
                    'answer': 'D',
                    'qid': 'quote and question/trial/1',
                },
                {
                    'text': 'They are like sheep being led to the slaughterhouse.\n\n'
                            'The main idea of this passage is that _ .\n\n' +
                            'A. Farm animals suffer gruesome deaths.\n' +
                            'B. In every school there is a "top" crowd that sets the pace.\n' +
                            'C. At one time or another you probably did something you knew to be wrong.\n'
                            'D. It is a mistake to follow the "top" crowd blindly.',
                    'answer': 'D',
                    'qid': 'quote and question/trial/2',
                },
            ],
        }

        for prompt_type in self.test_questions.keys():
            random.shuffle(self.test_questions[prompt_type])

    def parley(self):
        prompt_type = self.prompt_types[0]  # NB: Change self.prompt_type[0] if using multiple prompt_types
        ad = {
            'episode_done': False,
            'id': 'System',
            'text': 'Welcome onboard! We\'ll first give you ' + str(len(self.test_questions[prompt_type])) +
                    ' practice examples to help you understand the task. '
                    'To qualify for the HIT, you\'ll need to answer all practice questions correct.',
        }
        self.mturk_agent.observe(ad)

        for test_question in self.test_questions[prompt_type]:
            response = self.prompt_and_receive_response(test_question['text'], prompt_type, test_question['answer'])
            if test_question['answer'] != response:
                print(self.mturk_agent.worker_id, '| FAILED', test_question['qid'],
                      '| Answered', response, 'not', test_question['answer'])
                if response is not None:
                    print(self.mturk_agent.worker_id, '| SOFT BLOCKING')
                    self.mturk_agent.mturk_manager.soft_block_worker(self.mturk_agent.worker_id)
                    self.passed_test = False
                    ad = {
                        'episode_done': False,
                        'id': 'System',
                        'text': 'The correct answer was ' + test_question['answer'] + '.',
                    }
                    self.mturk_agent.observe(ad)
                self.episodeDone = True
                ad = {
                    'episode_done': True,
                    'id': 'System',
                    'text': 'Unfortunately, you did not qualify for our task at this time, but we hope to see you again soon!',
                }
                self.mturk_agent.observe(ad)
                self.mturk_agent.set_hit_is_abandoned()  # NB: May not be the right thing to do
                return
            ad = {
                'episode_done': False,
                'id': 'System',
                'text': 'Correct!',
            }
            self.mturk_agent.observe(ad)
            self.cur_example_no += 1

        self.passed_test = True
        self.episodeDone = True
        ad = {
            'episode_done': True,
            'id': 'System',
            'text': 'Great job! Advancing to the real task...',
        }
        self.mturk_agent.observe(ad)
        time.sleep(3)

    def prompt_and_receive_response(self, prompt_text, prompt_type, answer):
        # Clear previous answer from form. Emphasize questions are unrelated.
        ad = {
            'episode_done': False,
            'id': 'New ' + prompt_type,
            'text': None,
            'task_data': {"respond_with_form": None},
        }
        self.mturk_agent.observe(validate(ad))

        # Data collection prompt
        ad = {
            'episode_done': False,
            'id': '(#' + str(self.cur_example_no) + ')',
            'text': prompt_text,
            'task_data': {"respond_with_form": [{
                "type": "choices",
                "question": "Which option is most likely correct?",
                "choices": self.options
            }]}
        }
        self.mturk_agent.observe(validate(ad))

        # Receive response or handle disconnect
        answer = self.mturk_agent.act()
        if 'task_data' not in answer:
            print(self.mturk_agent.worker_id, '| DISCONNECT:', answer)
            self.episodeDone = True
            return None
        response = answer['task_data']['form_responses'][0]['response']

        print(self.mturk_agent.worker_id,
              '| prompt_type:', prompt_type,
              '| response:', response,
              '| debate_mode:', 'TEST', self.cur_example_no,
              '| answer:', answer,
              '| duration:', round(answer['duration'] / 1000., 1),
              '| qid:', 'TEST', self.cur_example_no)
        return response


class ContextEvaluationWorld(MTurkTaskWorld):
    """
    World for recording a turker's question and answer given a context.
    Assumes the context is a random context from a given task, e.g.
    from SQuAD, CBT, etc.
    """

    def __init__(self, opt, task, mturk_agent, evaluation_data):
        self.reward = opt['reward']
        self.is_sandbox = opt['is_sandbox']
        self.question_split_no = opt['question_split_no']
        self.option_split_no = opt['option_split_no']
        self.task = task
        self.mturk_agent = mturk_agent
        self.evaluation_data = evaluation_data
        self.episodeDone = False

        # Maintain data, counts, and stats
        self.max_collected = len(self.task.examples)
        self.cur_example_no = 1  # 1-indexed (shown to user)
        self.num_collected = 0
        self.num_tested = 0
        self.num_changed_responses = None
        self.num_debate_mode_responses = None
        self.data = []
        self.num_correct_on_labeled = {}
        self.num_collected_on_labeled = {}
        self.accuracy = {}
        self.answer_to_count_by_prompt = {}
        self.durations = {}
        self.reject_reasons = []
        self.block_reasons = []
        self.task_rating = None
        self.feedback = None
        self.hit_done = False
        self.freq_changed_responses = None

        # Prompt type differences
        self.prompt_types = [opt['prompt_type']]
        self.accuracy_bonus_threshold = {
            'quote and question': 0.5745454545454546,
            'question': .45,
        }
        self.median_sample_ms_reject_threshold = {
            'quote and question': 7000,
            'question': 6000,
        }

        if opt['num_options'] > 4:
            raise('Invalid task_config[\'num_options\'] = ' + str(opt['num_options']))
        self.options = ['A', 'B', 'C', 'D'][:opt['num_options']]
        self.debate_mode_to_option = {'Ⅰ': 'A', 'Ⅱ': 'B', 'Ⅲ': 'C', 'Ⅳ': 'D'}

        random.seed(0)
        if evaluation_data:
            self.num_changed_responses = 0
            self.num_debate_mode_responses = 0
            possible_debate_modes = list(evaluation_data.keys())
            possible_debate_modes.sort()
            self.sample_debate_modes = [possible_debate_modes[random.randint(0, len(possible_debate_modes) - 1) - self.option_split_no]
                                        for _ in range(self.max_collected)]

        self.num_test_turns = 0  # 2
        self.test_turns = []
        self.test_questions = {}
        if self.num_test_turns == 2:
            self.test_turns = [1, self.max_collected + self.num_test_turns]
            self.test_questions = {
                1: {
                    'text': '"We taught you this just last week!"\n\n' +
                            'Based on the passage, what does the student not know that the teacher expects him to know for the exam?\n\n' +
                            'A. 13 + 12 = 35\n' +
                            'B. 15 / 5 = 4\n' +
                            'C. 41 - 22 = 18\n' +
                            'D. 6 x 4 = 24',
                    'answer': 'D'
                },
                self.max_collected + self.num_test_turns: {
                    'text': '"Wow, I never knew a banana could be that color."\n\n' +
                            'When Fred opens his pantry, he is surprised the banana is not colored _.\n\n' +
                            'A. Gray-ish blue\n' +
                            'B. Purple and pink\n' +
                            'C. Green or yellow\n' +
                            'D. Plain white',
                    'answer': 'C'
                },
            }
        assert self.num_test_turns == len(self.test_turns), 'self.num_test_turns != len(self.test_turns)'

        print(self.mturk_agent.worker_id,
              "| question_split:", self.question_split_no,
              "| option_split:", self.option_split_no,
              '| assignment_id:', self.mturk_agent.assignment_id)

    def parley(self):
        self.cur_example_no = self.num_collected + self.num_tested + 1

        # Verify work quality with a test question
        if self.cur_example_no in self.test_questions.keys():
            test_question = self.test_questions[self.cur_example_no]
            response = self.prompt_and_receive_response(test_question['text'], 'quote and question', None)
            if test_question['answer'] != response:
                reason = 'Test failed: Example ' + str(self.cur_example_no) + ' - Answered ' + response + ' not ' + \
                         (test_question['answer'] if test_question['answer'] is not None else test_question['text'])
                # self.reject_reasons.append(reason)
            self.num_tested += 1
            return
        elif self.cur_example_no > (self.max_collected + self.num_test_turns):
            ad = {
                'episode_done': False,
                'id': 'System',
                'text': 'All done!',
                'task_data': {"respond_with_form": None}
            }
            for prompt_type, num_correct_for_prompt_type in self.num_correct_on_labeled.items():
                # Show accuracy
                prompt_type_accuracy = int(round((100. * num_correct_for_prompt_type) /
                                                 self.num_collected_on_labeled[prompt_type]))
                ad['text'] += ' You got ' + str(prompt_type_accuracy) + '% of questions right'
                if prompt_type == 'question':
                    ad['text'] += ' with just the questions and options!'
                elif prompt_type == 'quote and question':
                    ad['text'] += ' with just a short quote from the passage!'
                else:
                    ad['text'] += '!'

                # Congratulate if they beat random
                random_accuracy = int(round(100. / len(self.options)))
                if prompt_type_accuracy > (random_accuracy + 10):
                    ad['text'] += ' That\'s ' + str(prompt_type_accuracy - random_accuracy) + '% better than random guessing. Great work!'
            self.mturk_agent.observe(ad)

            ad = {
                'episode_done': False,
                'id': 'System',
                'text': 'How likely are you to recommend this task to a colleague?',
                'task_data': {
                    'respond_with_form': [
                        {
                            'type': 'choices',
                            'question': 'On a scale of 0-10',
                            'choices': [i for i in range(0, 11)]
                        }
                    ]
                }
            }
            self.mturk_agent.observe(ad)
            task_rating_answer = self.mturk_agent.act()  # Receive task rating
            self.task_rating = task_rating_answer['task_data']['form_responses'][0]['response']

            # Solicit free-form text feedback
            ad = {
                'episode_done': False,
                'id': 'System',
                'text': 'How can we improve this task?',
                'task_data': {"respond_with_form": None},
            }
            self.mturk_agent.observe(ad)
            feedback_answer = self.mturk_agent.act()
            self.feedback = feedback_answer['text']
            print(self.mturk_agent.worker_id, '| task_rating:', self.task_rating, '| feedback:', self.feedback)

            # Conclude HIT and send final message
            self.hit_done = True
            self.episodeDone = True
            ad = {
                'episode_done': True,
                'id': 'System',
                'text': 'Thanks for your help!',
            }
            self.mturk_agent.observe(ad)
            return
        else:
            # Get prompt text from dataset teacher agent
            sample = self.task.act()
            sample['debate_mode'] = self.sample_debate_modes[self.num_collected] if self.evaluation_data else None
            prompt_text = '\n'.join([sample['question'] + '\n'] + sample['options'])

            # Question-only evaluation
            if 'question' in self.prompt_types:
                question_response = self.prompt_and_receive_response(prompt_text, 'question', sample)
                if question_response is None:
                    return

            # Context+Question evaluation
            if 'quote and question' in self.prompt_types:
                evaluation_sample = self.evaluation_data[sample['debate_mode']][sample['qid']]
                sentences_chosen = '\n'.join([evaluation_sample['sentences_chosen'][0]])  # NB: Always picks first agent
                for punct in {'.', '?', '!', ';', ','}:
                    sentences_chosen = sentences_chosen.replace(' ' + punct, punct)
                prompt_text = sentences_chosen + '\n\n' + prompt_text
                sample['sentences_chosen'] = sentences_chosen
                quote_and_question_response = self.prompt_and_receive_response(prompt_text, 'quote and question', sample)
                if quote_and_question_response is None:
                    return
                if 'question' in self.prompt_types:
                    self.num_changed_responses += (quote_and_question_response != question_response)
                if sample['debate_mode'] is not None:
                    self.num_debate_mode_responses += (quote_and_question_response ==
                                                       self.debate_mode_to_option[sample['debate_mode']])

            # Terminate episode (if applicable)
            self.num_collected += 1
            return

    def prompt_and_receive_response(self, prompt_text, prompt_type, sample=None):
        # Clear previous answer from form. Emphasize questions are unrelated.
        ad = {
            'episode_done': False,
            'id': 'New ' + prompt_type,
            'text': None,
            'task_data': {"respond_with_form": None},
        }
        self.mturk_agent.observe(validate(ad))

        # Data collection prompt
        ad = {
            'episode_done': False,
            'id': '(#' + str(self.cur_example_no) + ')',
            'text': prompt_text,
            'task_data': {"respond_with_form": [{
                "type": "choices",
                "question": "Which option is most likely correct?",
                "choices": self.options
            }]}
        }
        self.mturk_agent.observe(validate(ad))

        # Receive response or handle disconnect
        answer = self.mturk_agent.act()
        if 'task_data' not in answer:
            print(self.mturk_agent.worker_id, '| DISCONNECT:', answer)
            self.episodeDone = True
            return None
        response = answer['task_data']['form_responses'][0]['response']

        if sample is not None:
            # Evaluate work on non-qualifying questions
            if 'eval_labels' in sample:  # NB: Check self.mturk_agent.metrics
                self.num_correct_on_labeled[prompt_type] = self.num_correct_on_labeled.get(prompt_type, 0)
                self.num_correct_on_labeled[prompt_type] += (response == sample['eval_labels'][0])
                self.num_collected_on_labeled[prompt_type] = self.num_collected_on_labeled.get(prompt_type, 0)
                self.num_collected_on_labeled[prompt_type] += 1
                self.accuracy[prompt_type] = self.num_correct_on_labeled[prompt_type] / self.num_collected_on_labeled[prompt_type]

            # Update answer stats and return
            self.durations[prompt_type] = self.durations.get(prompt_type, [])
            self.durations[prompt_type].append(answer['duration'])
            self.answer_to_count_by_prompt[prompt_type] = self.answer_to_count_by_prompt.get(prompt_type, {option: 0 for option in self.options})
            self.answer_to_count_by_prompt[prompt_type][response] += 1
            self.data.append({
                'sample': sample,
                'context': ad['text'],
                'response': response,
                'duration': answer['duration'],
            })

        print(self.mturk_agent.worker_id,
              '| prompt_type:', prompt_type,
              '| response:', response,
              '| debate_mode:', self.debate_mode_to_option[sample['debate_mode']] if sample is not None else 'TEST',
              '| answer:', sample['eval_labels'][0] if ((sample is not None) and ('eval_labels' in sample)) else 'TEST',
              '| duration:', round(answer['duration'] / 1000., 1),
              '| qid:', sample['qid'] if sample is not None else 'TEST',
              '' if (sample is None) or ('eval_labels' not in sample) else
              '| accuracy: ' + str(self.num_correct_on_labeled[prompt_type]) + '/' + str(self.num_collected_on_labeled[prompt_type]))
        return response

    def episode_done(self):
        return self.episodeDone

    def shutdown(self):
        self.task.shutdown()
        self.mturk_agent.shutdown()

    def review_work(self):
        if not self.hit_done:  # Don't review work if agent disconnected
            print(self.mturk_agent.worker_id, 'Done! (Disconnected) | num_debate_mode_responses:',
                  self.num_debate_mode_responses, '/', self.num_collected)
            return

        # Can review the work here to accept or reject it
        if (('question' in self.prompt_types) and ('quote and question' in self.prompt_types) and
                (self.num_changed_responses is not None)):
            self.freq_changed_responses = (self.num_changed_responses / self.num_collected)
            if self.freq_changed_responses <= .2:  # Not reading closely
                reason = 'freq_changed_responses = ' + str(self.freq_changed_responses)
                self.reject_reasons.append(reason)
                if self.freq_changed_responses <= .1:  # Spamming
                    self.block_reasons.append(reason)

        # Turker should be spending a minimum amount of time on each question
        median_durations = []
        for prompt_type, durations in self.durations.items():
            durations.sort()
            median_duration = durations[len(durations) // 2]
            median_durations.append(median_duration)
            if median_duration <= self.median_sample_ms_reject_threshold[prompt_type]:
                reason = 'median_duration = ' + str(median_duration)
                self.reject_reasons.append(reason)
                if median_duration <= (self.median_sample_ms_reject_threshold[prompt_type] / 2.):
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

        print(self.mturk_agent.worker_id, 'Done! | num_debate_mode_responses:', self.num_debate_mode_responses, '/', self.num_collected,
              '| block_reasons:', self.block_reasons,
              '| reject_reasons:', self.reject_reasons)
        if len(self.block_reasons) > 0:
            self.mturk_agent.reject_work('poor performance')
            if not self.is_sandbox:
                self.mturk_agent.block_worker('poor performance')
        elif len(self.reject_reasons):
            # TODO: Add soft block: mturk_manager.soft_block_worker(self.mturk_agent.worker_id) after setting --block-qualification
            self.mturk_agent.reject_work('poor performance')
        else:
            self.mturk_agent.approve_work()
            bonus_amount = round(.5 * self.reward, 2)

            if ('quote and question' in self.accuracy) and (self.accuracy['quote and question'] >= self.accuracy_bonus_threshold['quote and question']):
                self.mturk_agent.pay_bonus(bonus_amount, 'Great accuracy!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "self.accuracy['quote and question'] =", self.accuracy['quote and question'])

            if ('question' in self.accuracy) and (self.accuracy['question'] >= self.accuracy_bonus_threshold['question']):
                # Bonus if you're decently better than random, even with just question+options -only
                self.mturk_agent.pay_bonus(bonus_amount, 'Great accuracy!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "self.accuracy['question'] =", self.accuracy['question'])

            if (('question' in self.prompt_types) and ('quote and question' in self.prompt_types)
                    and (self.num_changed_responses is not None) and (self.freq_changed_responses >= .5)):
                self.mturk_agent.pay_bonus(bonus_amount, 'Great job overall!')
                print(self.mturk_agent.worker_id,
                      '| PAY_BONUS:', "freq_changed_responses =", self.freq_changed_responses)

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
            'hit_done': self.hit_done,
            'accuracy': self.accuracy,
            'question_split_no': self.question_split_no,
            'option_split_no': self.option_split_no,
            'freq_changed_responses': self.freq_changed_responses,
        }
