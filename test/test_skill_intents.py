# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import yaml
import logging

from os import getenv
from mock import Mock, patch
from mycroft_bus_client import Message
from ovos_utils.messagebus import FakeBus
from ovos_plugin_manager.skills import load_skill_plugins
from ovos_utils.log import LOG
from mycroft.skills.intent_services.padatious_service import PadatiousMatcher

regex_only = getenv("INTENT_ENGINE") == "padacioso"
LOG.level = logging.DEBUG


class MockPadatiousMatcher(PadatiousMatcher):
    include_med = True
    include_low = False

    def __init__(self, *args, **kwargs):
        PadatiousMatcher.__init__(self, *args, **kwargs)
        LOG.debug("Creating test Padatious Matcher")

    def match_medium(self, utterances, lang=None, __=None):
        if not self.include_med:
            LOG.info(f"Skipping medium confidence check for {utterances}")
            return None
        PadatiousMatcher.match_medium(self, utterances, lang=lang)

    def match_low(self, utterances, lang=None, __=None):
        if not self.include_low:
            LOG.info(f"Skipping low confidence check for {utterances}")
            return None
        PadatiousMatcher.match_low(self, utterances, lang=lang)


class TestSkillIntentMatching(unittest.TestCase):
    skills = load_skill_plugins()
    assert len(skills) == 1
    skill = skills[0]

    test_intents = getenv("INTENT_TEST_FILE")
    with open(test_intents) as f:
        valid_intents = yaml.safe_load(f)
    negative_intents = valid_intents.pop('unmatched intents', dict())
    common_query = valid_intents.pop("common query", dict())
    from mycroft.skills.intent_service import IntentService
    bus = FakeBus()
    intent_service = IntentService(bus)
    intent_service.padatious_service.padatious_config['regex_only'] = regex_only
    assert intent_service.padatious_service.is_regex_only == regex_only
    test_skill_id = 'test_skill.test'
    last_message = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.skill.config_core["secondary_langs"] = list(cls.valid_intents.keys())
        cls.skill._startup(cls.bus, cls.test_skill_id)

        def _on_message(msg):
            cls.last_message = msg

        cls.bus.on("message", _on_message)

    def test_intents(self):
        for lang in self.valid_intents.keys():
            self.assertIsInstance(lang.split('-')[0], str)
            self.assertIsInstance(lang.split('-')[1], str)
            for intent, examples in self.valid_intents[lang].items():
                intent_event = f'{self.test_skill_id}:{intent}'
                self.skill.events.remove(intent_event)
                intent_handler = Mock()
                self.skill.events.add(intent_event, intent_handler)
                for utt in examples:
                    if isinstance(utt, dict):
                        data = list(utt.values())[0]
                        utt = list(utt.keys())[0]
                    else:
                        data = list()
                    message = Message('test_utterance',
                                      {"utterances": [utt], "lang": lang})
                    self.intent_service.handle_utterance(message)
                    try:
                        intent_handler.assert_called_once()
                    except AssertionError as e:
                        LOG.error(self.last_message)
                        raise AssertionError(utt) from e
                    intent_message = intent_handler.call_args[0][0]
                    self.assertIsInstance(intent_message, Message, utt)
                    self.assertEqual(intent_message.msg_type, intent_event, utt)
                    for datum in data:
                        if isinstance(datum, dict):
                            name = list(datum.keys())[0]
                            value = list(datum.values())[0]
                        else:
                            name = datum
                            value = None
                        if name in intent_message.data:
                            # This is an entity
                            voc_id = name
                        else:
                            # We mocked the handler, data is munged
                            voc_id = f'{self.test_skill_id.replace(".", "_")}' \
                                     f'{name}'
                        self.assertIsInstance(intent_message.data.get(voc_id),
                                              str, intent_message.data)
                        if value:
                            self.assertEqual(intent_message.data.get(voc_id),
                                             value, utt)
                    intent_handler.reset_mock()

    @patch("mycroft.skills.intent_service.PadatiousMatcher",
           new=MockPadatiousMatcher)
    def test_negative_intents(self):
        test_config = self.negative_intents.pop('config', None)
        if test_config:
            MockPadatiousMatcher.include_med = test_config.get('include_med',
                                                               True)
            MockPadatiousMatcher.include_low = test_config.get('include_low',
                                                               False)
        intent_failure = Mock()
        self.intent_service.send_complete_intent_failure = intent_failure

        for lang in self.negative_intents.keys():
            for utt in self.negative_intents[lang]:
                message = Message('test_utterance',
                                  {"utterances": [utt], "lang": lang})
                self.intent_service.handle_utterance(message)
                try:
                    intent_failure.assert_called_once_with(message)
                    intent_failure.reset_mock()
                except AssertionError as e:
                    LOG.error(self.last_message)
                    raise AssertionError(utt) from e

    def test_common_query(self):
        qa_callback = Mock()
        qa_response = Mock()
        self.skill.events.add('question:action', qa_callback)
        self.skill.events.add('question:query.response', qa_response)
        for lang in self.common_query.keys():
            for utt in self.common_query[lang]:
                if isinstance(utt, dict):
                    data = list(utt.values())[0]
                    utt = list(utt.keys())[0]
                else:
                    data = dict()
                message = Message('test_utterance',
                                  {"utterances": [utt], "lang": lang})
                self.intent_service.handle_utterance(message)
                response = qa_response.call_args[0][0]
                callback = qa_response.call_args[0][0]
                self.assertIsInstance(response, Message)
                self.assertTrue(response.data["phrase"] in utt)
                self.assertEqual(response.data["skill_id"], self.skill.skill_id)
                self.assertIn("callback_data", response.data.keys())
                self.assertIsInstance(response.data["conf"], float)
                self.assertIsInstance(response.data["answer"], str)

                self.assertIsInstance(callback, Message)
                self.assertEqual(callback.data['skill_id'], self.skill.skill_id)
                self.assertEqual(callback.data['phrase'],
                                 response.data['phrase'])
                if not data:
                    continue
                if isinstance(data.get('callback'), dict):
                    self.assertEqual(callback.data['callback_data'],
                                     data['callback'])
                elif isinstance(data.get('callback'), list):
                    self.assertEqual(set(callback.data['callback_data'].keys()),
                                     set(data.get('callback')))
                if data.get('min_confidence'):
                    self.assertGreaterEqual(response.data['conf'],
                                            data['min_confidence'])
                if data.get('max_confidence'):
                    self.assertLessEqual(response.data['conf'],
                                         data['max_confidence'])


if __name__ == "__main__":
    unittest.main()
