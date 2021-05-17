import logging

from chatRobot import utils




class ChatBot(object):
    """
    A conversational dialog chat bot.
    """

    def __init__(self, name, **kwargs):
        self.name = name


        # processors
        preprocessors = kwargs.get(
            'preprocessors', ['chatRobot.PreProcessing.clean_whitespace']
        )

        self.preprocessors = []

        for preprocessor in preprocessors:
            self.preprocessors.append(utils.import_module(preprocessor))


