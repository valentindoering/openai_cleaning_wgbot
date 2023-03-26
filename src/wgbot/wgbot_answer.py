class WgbotAnswer():
    def __init__(self, message: str):
        self.message = message

class ErrorAnswer(WgbotAnswer):
    pass

class WarningAnswer(WgbotAnswer):
    pass

class CommandAnswer(WgbotAnswer):
    pass

class SuccessAnswer(WgbotAnswer):
    pass
