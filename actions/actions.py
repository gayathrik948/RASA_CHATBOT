# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


import logging

from actions import functions
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from typing import Any, Text, Dict, List, Union

REQUESTED_SLOT = "requested_slot"
logger = logging.getLogger(__name__)
__config_responses__ = functions.db.config_responses.find_one({"use_case": "hr_portal"})


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_welcome"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = __config_responses__['responses']['welcome_message']['text']
        dispatcher.utter_message(text=message)

        return [FollowupAction("botOption_form"), AllSlotsReset()]


class BotOptionForm(FormAction):
    def name(self) -> Text:
        return 'botOption_form'

    def required_slots(self, tracker) -> List[Text]:
        return ['botOption']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {'botOption': [self.from_text()]}

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == "botOption":
                    message = __config_responses__['responses']['bot_options']['text']
                    buttons = __config_responses__['responses']['bot_options']['buttons']

                    if tracker.get_slot('retry_slot') == 'botOption':
                        retry_message = __config_responses__["responses"]["retry_botOption"]["text"]
                        message = __config_responses__['responses']['bot_options']['text']
                        buttons = __config_responses__['responses']['bot_options']['buttons']
                        dispatcher.utter_message(text=retry_message)
                    dispatcher.utter_message(text=message, buttons=buttons)

                else:
                    dispatcher.utter_template("utter_ask_{}".format(slot), tracker)

                return [SlotSet(REQUESTED_SLOT, slot)]

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker,
               domain: Dict[Text, Any], ) -> List[Dict]:

        message = tracker.latest_message.get('text')
        message = message.lower().strip()
        metadata = functions.extract_metadata_from_tracker(tracker)
        user_id = metadata.get('user_id', None)

        if message in __config_responses__['bot_options']:
            logger.debug("Selection Bot option: {}".format(message))
            if message == "ask question":
                return [SlotSet("botOption", message), SlotSet("retry_slot", None), SlotSet("user_id", user_id),
                        FollowupAction("module_form")]

            elif message == "seek information":
                dispatcher.utter_message(text="Dev in Progress")
                return [SlotSet("botOption", message), SlotSet("retry_slot", None),
                        FollowupAction("seek_information_form")]

            elif message == "direct navigation":
                dispatcher.utter_message(text="Dev in Progress")
                return [SlotSet("botOption", message), SlotSet("retry_slot", None),
                        FollowupAction("direct_navigation_form")]
        #
        else:
            if message == "/reset_chat":
                return [AllSlotsReset(), FollowupAction("action_reset_chat")]
            else:
                return [SlotSet("botOption", None), SlotSet("retry_slot", "botOption"),
                        FollowupAction('botOption_form')]


class ModuleForm(FormAction):
    def name(self) -> Text:
        return 'module_form'

    def required_slots(self, tracker) -> List[Text]:
        return ['module']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {'module': [self.from_text()]}

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == "module":
                    message = __config_responses__['responses']['module_options']['text']
                    buttons = __config_responses__['responses']['module_options']['buttons']

                    if tracker.get_slot('retry_slot') == 'module':
                        retry_message = __config_responses__["responses"]["retry_moduleOption"]["text"]
                        message = __config_responses__['responses']['module_options']['text']
                        buttons = __config_responses__['responses']['module_options']['buttons']
                        dispatcher.utter_message(text=retry_message)
                    dispatcher.utter_message(text=message, buttons=buttons)

                else:
                    dispatcher.utter_template("utter_ask_{}".format(slot), tracker)

                return [SlotSet(REQUESTED_SLOT, slot)]

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker,
               domain: Dict[Text, Any], ) -> List[Dict]:

        message = tracker.latest_message.get('text')
        message = message.lower().strip()
        # metadata = functions.extract_metadata_from_tracker(tracker)
        # user_id = metadata.get('user_id', None)

        if message in __config_responses__['module_options']:
            if message == "search across":

                search_que_message = __config_responses__['responses']['search_question']['text']
                dispatcher.utter_message(text=search_que_message)
                return [SlotSet("module", message), SlotSet("retry_slot", None)]
            else:
                # todo : Get List of Questions
                logger.debug("Selection Module: {}".format(message))
                questions_list = functions.get_questions(message)
                que_message = __config_responses__['responses']['select_question']['text']
                dispatcher.utter_message(message=que_message, buttons=questions_list)
                return [SlotSet("module", message), SlotSet("retry_slot", None)]

        else:
            if message == "/reset_chat":
                return [AllSlotsReset(), FollowupAction("action_reset_chat")]
            else:
                return [SlotSet("module", None), SlotSet("retry_slot", "module"),
                        FollowupAction('module_form')]


class ActionValidateKeyword(Action):

    def name(self) -> Text:
        return "action_validate_keyword"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        module = tracker.get_slot("module")
        user_question = tracker.latest_message['text']
        logger.debug("Input_Message: " + user_question)

        if user_question.lower() == "my question not here":
            return [SlotSet("question", user_question), FollowupAction("support_form")]
        else:
            print("@@", user_question, "@@", module)
            res_answer = functions.fetch_faq_question_answer(user_question.lower(), "", module.lower())
            if res_answer:
                answer = res_answer[0]['response']
                # buttons = __config_responses__['responses']['retrive_answer']['buttons']
                # dispatcher.utter_message(text=answer, buttons=buttons)
                return [SlotSet("question", user_question), SlotSet("answer", answer), FollowupAction("response_form")]
            else:
                
                extracted_entities = []
                entities = tracker.latest_message['entities']
                for ent in entities:
                    if ent['value'].lower() in functions.__keyphrases_list__:
                        extracted_entities.append(ent['value'])
                # Check extracted entities
                if not extracted_entities:
                    extracted_entities = functions.extract_keyphrase(user_question)

                logger.debug("Entity Extraction : {0}".format(tracker.latest_message['entities']))
                ent_mes = " ,".join(extracted_entities)
                logger.debug("{} : {}".format("Extracted Keyphrases Are: ", ent_mes))
                # Fetch the Answer form faq data
                if extracted_entities:
                    if len(extracted_entities) == 1:
                        response = functions.fetch_faq_question_answer("", extracted_entities[0])
                        if response:
                            if len(response) == 1:
                                answer = response[0]['response']

                                return [SlotSet("question", user_question), SlotSet("answer", answer),
                                        FollowupAction("response_form")]
                            else:
                                message = "Dev in progress to handle multiple questions"
                        else:
                            message = "There no Answer Available for keyphrase: "
                    else:
                        message = "Dev in progress to handle multiple keyphrases"
                else:
                    message = "There are no Keyphrases extracted"

                dispatcher.utter_message(text=message)

                return []


class ResponseForm(FormAction):
    def name(self) -> Text:
        return 'response_form'

    def required_slots(self, tracker) -> List[Text]:
        return ['reponse_feedback']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {'reponse_feedback': [self.from_text()]}

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == "reponse_feedback":
                    message = tracker.get_slot("answer")
                    buttons = __config_responses__['responses']['reponse_feedback']['buttons']
                    if tracker.get_slot('retry_slot') == 'reponse_feedback':
                        message = __config_responses__["responses"]["retry_reponse_feedback"]["text"]
                        buttons = __config_responses__['responses']['reponse_feedback']['buttons']
                    dispatcher.utter_message(text=message, buttons=buttons)

                else:
                    dispatcher.utter_template("utter_ask_{}".format(slot), tracker)

                return [SlotSet(REQUESTED_SLOT, slot)]

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker,
               domain: Dict[Text, Any], ) -> List[Dict]:

        message = tracker.latest_message.get('text')
        message = message.lower().strip()
        # metadata = functions.extract_metadata_from_tracker(tracker)
        # user_id = metadata.get('user_id', None)

        if message in ["i am happy with the answer", "ask another question", "ask for help"]:
            if message == "ask another question":
                functions.add_user_feedback_logs(tracker)
                return [SlotSet("module", None), SlotSet("question", None), SlotSet("answer", None),
                        SlotSet("reponse_feedback", None), SlotSet("retry_slot", None), FollowupAction("module_form")]
            elif message == "ask for help":
                return [SlotSet("reponse_feedback", message), SlotSet("retry_slot", None),
                        FollowupAction("support_form")]
            else:
                return [SlotSet("reponse_feedback", message), SlotSet("retry_slot", None),
                        FollowupAction("feedback_form")]

        else:
            if message == "/reset_chat":
                return [AllSlotsReset(), FollowupAction("action_reset_chat")]
            else:
                return [SlotSet("reponse_feedback", None), SlotSet("retry_slot", "reponse_feedback"),
                        FollowupAction('response_form')]


class FeedBackForm(FormAction):
    def name(self) -> Text:
        return 'feedback_form'

    def required_slots(self, tracker) -> List[Text]:
        return ['feed_back_rating']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {'feed_back_rating': [self.from_text()]}

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == "feed_back_rating":
                    message = __config_responses__["responses"]["feed_back_rating"]["text"]
                    buttons = __config_responses__['responses']['feed_back_rating']['buttons']
                    if tracker.get_slot('retry_slot') == 'feed_back_rating':
                        retry_message =  __config_responses__["responses"]["retry_feed_back_rating"]["text"]
                        message = __config_responses__["responses"]["feed_back_rating"]["text"]
                        buttons = __config_responses__['responses']['feed_back_rating']['buttons']
                        dispatcher.utter_message(text=retry_message)
                    dispatcher.utter_message(text=message, buttons=buttons)

                else:
                    dispatcher.utter_template("utter_ask_{}".format(slot), tracker)

                return [SlotSet(REQUESTED_SLOT, slot)]

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker,
               domain: Dict[Text, Any], ) -> List[Dict]:

        message = tracker.latest_message.get('text')
        message = message.lower().strip()
        # metadata = functions.extract_metadata_from_tracker(tracker)
        # user_id = metadata.get('user_id', None)

        if str(message) in ["1", "2", "3", "4", "5"]:
            functions.add_user_feedback_logs(tracker)
            return [SlotSet("feed_back_rating", message), SlotSet("retry_slot", None), FollowupAction("action_endchat")]

        else:
            if message == "/reset_chat":
                return [AllSlotsReset(), FollowupAction("action_reset_chat")]
            else:
                return [SlotSet("feed_back_rating", None), SlotSet("retry_slot", "feed_back_rating"),
                        FollowupAction('feedback_form')]


class SupportForm(FormAction):
    def name(self) -> Text:
        return 'support_form'

    def required_slots(self, tracker) -> List[Text]:
        return ['support_type']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {'support_type': [self.from_text()]}

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot == "support_type":
                    message = __config_responses__['responses']['support_options']['text']
                    buttons = __config_responses__['responses']['support_options']['buttons']

                    if tracker.get_slot('retry_slot') == 'support_type':
                        retry_message = __config_responses__["responses"]["retry_support_type"]["text"]
                        message = __config_responses__['responses']['support_options']['text']
                        buttons = __config_responses__['responses']['support_options']['buttons']
                        dispatcher.utter_message(text=retry_message)
                    dispatcher.utter_message(text=message, buttons=buttons)

                else:
                    dispatcher.utter_template("utter_ask_{}".format(slot), tracker)

                return [SlotSet(REQUESTED_SLOT, slot)]

    def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker,
               domain: Dict[Text, Any], ) -> List[Dict]:

        message = tracker.latest_message.get('text')
        message = message.lower().strip()
        # metadata = functions.extract_metadata_from_tracker(tracker)
        # user_id = metadata.get('user_id', None)

        if message in ["speek to us", "rise a service request"]:
            if message == "speek to us":
                message = __config_responses__['responses']['call_support']['text']
            else:
                message = __config_responses__['responses']['rise_mail_support']['text']
            functions.add_user_feedback_logs(tracker)
            dispatcher.utter_message(text=message)
            return [SlotSet("support_type", message), SlotSet("retry_slot", None), FollowupAction("action_endchat")]

        else:
            if message == "/reset_chat":
                return [AllSlotsReset(), FollowupAction("action_reset_chat")]
            else:
                return [SlotSet("support_type", None), SlotSet("retry_slot", "support_type"),
                        FollowupAction('support_form')]


class ActionEndChat(Action):

    def name(self) -> Text:
        return "action_endchat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = __config_responses__['responses']['end_chat']['text']
        buttons = __config_responses__['responses']['end_chat']['buttons']
        dispatcher.utter_message(text=message, buttons=buttons)
        return []


class ActionResetChat(Action):

    def name(self) -> Text:
        return "action_reset_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset(), FollowupAction("action_welcome")]


