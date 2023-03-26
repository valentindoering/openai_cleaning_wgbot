from src.wgbot.wgbot import Wgbot
from src.data.database_element import Person
from src.utils import Config, CSVLogger
from src.openai import OpenAi, ChatGPT
from src.wgbot.wgbot_answer import ErrorAnswer, WarningAnswer, CommandAnswer, SuccessAnswer
from src.data.data import Data


class AiWgbot(Wgbot):

    def __init__(self, data: Data, organization: str, api_key: str, role: str, system_briefing: str, question_briefing_func, message_briefing, log_func):
        super().__init__(data=data)
        self.role = role
        self.question_briefing = question_briefing_func
        self.message_briefing = message_briefing

        self.ai = ChatGPT(
            organization = organization,
            api_key = api_key,
            briefing = system_briefing,
            logger=log_func,
        )

    def filter_wgbot_start(self, message: str) -> str:
        unwanted_start = f"{self.role.lower()}: "
        if message.lower().startswith(unwanted_start):
            return message[len(unwanted_start):]
        return message
    
    def ask(self, message: str, sender_person: Person) -> str:

        # This tracks all messsages in the chat
        print(f"incoming message: {sender_person.name}: {message}")
        self.ai.append_chat_history(role=sender_person.name, message=message)
        print()

        # See if a worker gets trigger, if yes, continue
        worker_reply = super().ask(message=message, sender_person=sender_person)
        if not worker_reply:
            ai_reply = self.ai.ask(
                question=self.message_briefing,
                append_chat_history=True
            )
            reply = self.filter_wgbot_start(ai_reply)
        else:
            # on success or warning, we let the ai improve the answer
            if isinstance(worker_reply, SuccessAnswer) or isinstance(worker_reply, WarningAnswer):
                ai_reply = self.ai.ask(
                    question=self.question_briefing(worker_reply.message),
                    append_chat_history=True
                )
                reply = self.filter_wgbot_start(ai_reply)
            else:
                reply = worker_reply.message
        
        # also track reply for full chat history
        self.ai.append_chat_history(role=self.role, message=reply)
        print(self.ai.chat_history_text())
        print("-------------------------------")
        return reply
