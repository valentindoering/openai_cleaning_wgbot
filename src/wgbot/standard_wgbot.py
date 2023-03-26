from src.wgbot.wgbot import Wgbot
from src.data.database_element import Person

class SimpleWgbot(Wgbot):
    
    def ask(self, message: str, sender_person: Person) -> str:
        return super().ask(message=message, sender_person=sender_person).message