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
        self._letter_to_answer_idx = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        self._answer_idx_to_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}

        datapath = os.path.join(
            opt['datapath'],
            'RACE',
            self.datatype
        )
        self.data = self._setup_data(datapath)

        self.id = 'race'
        self.reset()

    def num_examples(self):
        return len(self.examples)

    def num_episodes(self):
        return self.num_examples()

    def get(self, episode_idx, entry_idx=None):
        return self.examples[episode_idx]

    # def setup_data(self):
    #     for example in self.examples:
    #         yield example

    def _setup_data(self, file_path):
        self.examples = []
        for level in ['high', 'middle']:
            # Get all articles
            file_level_path = os.path.join(file_path, level)
            if not os.path.exists(file_level_path):
                continue
            articles = os.listdir(file_level_path)
            for article in articles:
                art_file = os.path.join(file_level_path, article)
                with open(art_file, 'rb') as f:
                    art_data = json.load(f)

                # Article-level info
                title = art_data["id"]
                passage_text = art_data["article"]

                # Iterate through questions
                # NB: Can reduce memory by not repeating passages. Add art_data to a list,
                # storing indices into self.examples and question indices in self.examples
                for q in range(len(art_data["questions"])):
                    question_text = art_data["questions"][q].strip().replace("\n", "")
                    options_text = art_data["options"][q]
                    for option_no in range(len(options_text)):
                        options_text[option_no] = self._answer_idx_to_letter[option_no] + ': ' + options_text[option_no]
                    answer_index = self._letter_to_answer_idx[art_data["answers"][q]]
                    qid = self._filepath_to_id(art_file, q)
                    self.examples.append({
                        'id': 'race',
                        'text': '\n'.join([passage_text + '\n', question_text] + options_text),
                        'labels': options_text[answer_index],
                        'episode_done': True,
                        'answer_starts': answer_index,
                        'title': title,
                        'qid': qid,
                        'passage': passage_text,
                        'question': question_text,
                        'options': options_text
                    })

    @staticmethod
    def _filepath_to_id(filepath: str, q_no: int) -> str:
        file_parts = os.path.join(filepath, str(q_no)).split('/')[-4:]
        for split in ['train', 'dev', 'test']:
            if split in file_parts[0]:
                file_parts[0] = split
            elif file_parts[0] in {'A', 'B', 'C', 'D', 'E'}:
                file_parts[0] = 'test'  # Question-type datasets come from test
        return '/'.join(file_parts)
