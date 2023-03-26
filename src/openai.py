import openai
import tiktoken

class OpenAi():
    def __init__(self, organization: str, api_key: str, model: str, max_tokens_per_request: int, logger = print):
        openai.organization = organization
        openai.api_key = api_key

        self._model = model
        self._max_tokens_per_request = max_tokens_per_request

        self._logger = logger
    
    def ask(self, question):
        try:
            answer = openai.Completion.create(
                model=self._model,
                prompt=question,
                max_tokens=int(self._max_tokens_per_request),
                temperature=0
            )
            text = answer['choices'][0]['text']
            # new line in csv file with date, time, question, answer
            log_text = text.replace('\n', ' ')
            self._logger(f'{question},{log_text}')
            return text
        except Exception as err:
            self._logger(f'{question},{"ChatGPT failed"}')
            raise err
        
    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        tokenizer = tiktoken.get_encoding("p50k_base")
        num_tokens = len(tokenizer.encode(string))
        return num_tokens

class ChatGPT(OpenAi):
    def __init__(self, organization: str, api_key: str, briefing: str, logger = print):
        super().__init__(organization, api_key, "gpt-3.5-turbo", 4096, logger)
        self.briefing = briefing
        self.chat_history = []
    
    def append_chat_history(self, role, message):
        self.chat_history.append(f"{role}: {message}\n")
    
    def chat_history_text(self):
        return "".join(self.chat_history)

    def n_tokens_chat_history(self):
        return self.num_tokens_from_string(self.chat_history_text())
    
    def chat_history_text_shortend(self):
        while self.n_tokens_chat_history() > (self._max_tokens_per_request - 1000):
            self.chat_history.pop(0)
        
        return self.chat_history_text()
    
    def ask(self, question, append_chat_history=False):
        messages = [
            {"role": "system", "content": self.briefing},
            {"role": "user", "content": question if not append_chat_history else f"{question}\n\nChat History:\n{self.chat_history_text_shortend()}"}
        ]

        request = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        answer = request["choices"][0]["message"]["content"]
        return answer