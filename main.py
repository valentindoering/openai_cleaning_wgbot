from src.data.data import Data
from src.utils import Config, CSVLogger, on_error_send_traceback
from src.openai import OpenAi
from src.telegram import Telegram, TelegramMessage
from src.wgbot.ai_wgbot import AiWgbot

if __name__ == "__main__":

    config = Config(
        config_file='config.yml'
    )
 
    data = Data(
        data_file = config.get('environment_files')['data'], 
        # special_load_file="data/backup_data.json"
    )
    telegram = Telegram(
        bot_key = config.get('telegram')['bot_key'], 
        chat_id = config.get('telegram')['chat_id'],
        polling_interval_in_seconds=config.get('telegram')['polling_interval_in_seconds']
    )

    config = Config(
        config_file='config.yml'
    )

    log_in_csv = CSVLogger(
        file_name = config.get('environment_files')['log']
    ).log


    wgbot = AiWgbot(
        data=data,
        organization = config.get('openai')['organization'],
        api_key = config.get('openai')['api_key'],
        role = "Mom",
        system_briefing = "You are a helpful assistant.",
        message_briefing=f"You act as the Mom of 3 children who live in a shared apartment. You are currently in a conversation with your children, see the chat history below. Please formulate the next message of the caring mom.\n\nIf possible, try to be funny and creative. The message should fit well into the context of the chat history. Only output the answer, do not give descriptions or explanations to justify your answer.",
        question_briefing_func= lambda message: f"You act as the Mom of 3 children who live in a shared apartment. You are currently in a conversation with your children, see the chat history below. The next thing you should say is '{message}'. Don't change the meaning of the answer, but speak in your own words acting as the caring Mom. If it fits you can add aditional information.\n\nIf possible, try to be funny and creative. The message should fit well into the context of the chat history. Only output the answer, do not give descriptions or explanations to justify your answer.",
        log_func=log_in_csv
    )

    @on_error_send_traceback(log_func=telegram.send)
    def reply(message: TelegramMessage) -> str:

        # identify sender
        sender_persons = data.find('persons', lambda person: person.telegram_id == message.user_id)
        if len(sender_persons) != 1:
            persons_found_str = ',\n'.join([person for person in sender_persons])
            return f"Coulnd't identify exactly one person with telegram id {message.user_id}, found:\n[\n{persons_found_str}\n]"
        sender_person = sender_persons[0]

        return wgbot.ask(message=message.text, sender_person=sender_person)
    
    # Program Loop
    telegram.poll_reply(callback=reply)











    

    










