import os
import sys
import csv
import time
# from dateutil import parser as date_parser
from chatterbot.conversation import Statement
from chatterbot.tagging import PosLemmaTagger
from chatterbot import utils


class Trainer(object):
    """
    Base class for all other trainer classes.

    :param boolean show_training_progress: Show progress indicators for the
           trainer. The environment variable ``CHATTERBOT_SHOW_TRAINING_PROGRESS``
           can also be set to control this. ``show_training_progress`` will override
           the environment variable if it is set.
    """

    def __init__(self, chatbot, **kwargs):
        self.chatbot = chatbot

        environment_default = os.getenv('CHATTERBOT_SHOW_TRAINING_PROGRESS', True)
        self.show_training_progress = kwargs.get(
            'show_training_progress',
            environment_default
        )

    def get_preprocessed_statement(self, input_statement):
        """
        Preprocess the input statement.
        """
        for preprocessor in self.chatbot.preprocessors:
            input_statement = preprocessor(input_statement)

        return input_statement

    def train(self, *args, **kwargs):
        """
        This method must be overridden by a child class.
        """
        raise self.TrainerInitializationException()

    class TrainerInitializationException(Exception):
        """
        Exception raised when a base class has not overridden
        the required methods on the Trainer base class.
        """

        def __init__(self, message=None):
            default = (
                'A training class must be specified before calling train(). '
                'See http://chatterbot.readthedocs.io/en/stable/training.html'
            )
            super().__init__(message or default)

    def _generate_export_data(self):
        result = []
        for statement in self.chatbot.storage.filter():
            if statement.in_response_to:
                result.append([statement.in_response_to, statement.text])

        return result

    def export_for_training(self, file_path='./export.json'):
        """
        Create a file from the database that can be used to
        train other chat bots.
        """
        import json
        export = {'conversations': self._generate_export_data()}
        with open(file_path, 'w+', encoding='utf8') as jsonfile:
            json.dump(export, jsonfile, ensure_ascii=False)


class ListTrainer(Trainer):
    """
    Allows a chat bot to be trained using a list of strings
    where the list represents a conversation.
    """

    def train(self, conversation):
        """
        Train the chat bot based on the provided list of
        statements that represents a single conversation.
        """
        previous_statement_text = None
        previous_statement_search_text = ''

        statements_to_create = []

        for conversation_count, text in enumerate(conversation):
            if self.show_training_progress:
                utils.print_progress_bar(
                    'List Trainer',
                    conversation_count + 1, len(conversation)
                )

            statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)

            statement = self.get_preprocessed_statement(
                Statement(
                    text=text,
                    search_text=statement_search_text,
                    in_response_to=previous_statement_text,
                    search_in_response_to=previous_statement_search_text,
                    conversation='training'
                )
            )

            previous_statement_text = statement.text
            previous_statement_search_text = statement_search_text

            statements_to_create.append(statement)

        self.chatbot.storage.create_many(statements_to_create)


class ChatterBotCorpusTrainer(Trainer):
    """
    Allows the chat bot to be trained using data from the
    ChatterBot dialog corpus.
    """

    def train(self, *corpus_paths):
        from chatterbot.corpus import load_corpus, list_corpus_files

        data_file_paths = []

        # Get the paths to each file the bot will be trained with
        for corpus_path in corpus_paths:
            data_file_paths.extend(list_corpus_files(corpus_path))

        for corpus, categories, file_path in load_corpus(*data_file_paths):

            statements_to_create = []

            # Train the chat bot with each statement and response pair
            for conversation_count, conversation in enumerate(corpus):

                if self.show_training_progress:
                    utils.print_progress_bar(
                        'Training ' + str(os.path.basename(file_path)),
                        conversation_count + 1,
                        len(corpus)
                    )

                previous_statement_text = None
                previous_statement_search_text = ''

                for text in conversation:

                    statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)

                    statement = Statement(
                        text=text,
                        search_text=statement_search_text,
                        in_response_to=previous_statement_text,
                        search_in_response_to=previous_statement_search_text,
                        conversation='training'
                    )

                    statement.add_tags(*categories)

                    statement = self.get_preprocessed_statement(statement)

                    previous_statement_text = statement.text
                    previous_statement_search_text = statement_search_text

                    statements_to_create.append(statement)

            if statements_to_create:
                self.chatbot.storage.create_many(statements_to_create)

