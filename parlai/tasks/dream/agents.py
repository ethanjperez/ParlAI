#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from parlai.core.teachers import FixedDialogTeacher
from .build import build

import json
import os


class IndexTeacher(FixedDialogTeacher):
    """Hand-written dataset teacher, which loads the json squad data and
    implements its own `act()` method for interacting with student agent,
    rather than inheriting from the core Dialog Teacher. This code is here as
    an example of rolling your own without inheritance.

    This teacher also provides access to the "answer_start" indices that
    specify the location of the answer in the context.
    """

    def __init__(self, opt, shared=None):
        build(opt)
        super().__init__(opt, shared)
        self.id = 'dream'
        self._letter_to_answer_idx = {'A': 0, 'B': 1, 'C': 2}
        self._answer_idx_to_letter = {0: 'A', 1: 'B', 2: 'C'}

        self.split = 'dev'  # TFIDF, FastText. TODO: Once DREAM JSONs fixed, revert to auto-detecting split
        # for split in ['test', 'dev', 'train']:
        #     if split in self.datatype:
        #         self.split = split
        #         break

        datapath = os.path.join(
            opt['datapath'],
            'DREAM',
            self.datatype + '.json'
        )
        self.data = self._setup_data(datapath, opt['question_split_no'], opt['question_splits'])

        self.reset()

    def num_examples(self):
        return len(self.examples)

    def num_episodes(self):
        return self.num_examples()

    def get(self, episode_idx, entry_idx=None):
        return self.examples[episode_idx]

    def _setup_data(self, file_path, split_no=0, num_splits=1):
        self.examples = []

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Iterate through Dialogues
        for diag in data:
            passage, qas, diag_id = diag

            # Concatenate Passage Turns
            passage_text = " ".join(passage)

            # Iterate through QAs
            for idx, qa in enumerate(qas):
                question_text, options_text, answer_text, question_type_labels = qa['question'], qa['choice'], qa['answer'], qa['types']
                answer_index = options_text.index(answer_text)
                for option_no in range(len(options_text)):
                    options_text[option_no] = self._answer_idx_to_letter[option_no] + ': ' + options_text[option_no]

                # Generate a Question ID by adding to diag_id
                qid = self.split + '/' + diag_id + '/' + str(idx)  # TFIDF, FastText
                # qid = diag_id + '-q' + str(idx)

                # Add example
                self.examples.append({
                    'id': self.id,
                    'text': '\n'.join([passage_text + '\n', question_text + '\n'] + options_text),
                    'labels': options_text[answer_index],
                    'episode_done': True,
                    'answer_starts': answer_index,
                    'qid': qid,
                    'passage': passage_text,
                    'question': question_text,
                    'options': options_text,
                    'question_type_labels': question_type_labels,
                })

        self.examples = self.examples[split_no::num_splits]
