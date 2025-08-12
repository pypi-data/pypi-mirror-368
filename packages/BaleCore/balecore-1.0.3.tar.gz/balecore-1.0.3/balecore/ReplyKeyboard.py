class ReplyKeyboardMarkup:
    def __init__(self, keyboard=None, selective=None):
        self.keyboard = keyboard if keyboard else []
        self.selective = selective

    def add_row(self, *buttons):
        self.keyboard.append([button for button in buttons])
        return self

    def to_dict(self):
        result = {
            "keyboard": [
                [button.to_dict() for button in row] 
                for row in self.keyboard
            ]
        }
        if self.selective is not None:
            result["selective"] = self.selective
        return result

class KeyboardButton:
    def __init__(self, text, request_contact=False, request_location=False, web_app=None):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location
        self.web_app = web_app

    def to_dict(self):
        button_dict = {"text": self.text}
        if self.request_contact:
            button_dict["request_contact"] = True
        if self.request_location:
            button_dict["request_location"] = True
        if self.web_app:
            button_dict["web_app"] = self.web_app.to_dict()
        return button_dict

class KeyboardButtonPollType:
    def __init__(self, type=None):
        self.type = type

    def to_dict(self):
        return {"type": self.type} if self.type else {}

class WebAppInfo:
    def __init__(self, url):
        self.url = url

    def to_dict(self):
        return {"url": self.url}