class InlineKeyboardMarkup:
    def __init__(self, keyboard=None):
        self.keyboard = keyboard if keyboard else []

    def add_row(self, *buttons):
        self.keyboard.append([button for button in buttons])
        return self

    def to_dict(self):
        return {
            "inline_keyboard": [
                [button.to_dict() for button in row] 
                for row in self.keyboard
            ]
        }

class InlineKeyboardButton:
    def __init__(self, text, callback_data=None, url=None, web_app=None, copy_text=None):
        self.text = text
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.copy_text = copy_text

    def to_dict(self):
        button_dict = {"text": self.text}
        
        if self.callback_data:
            button_dict["callback_data"] = self.callback_data
        if self.url:
            button_dict["url"] = self.url
        if self.web_app:
            button_dict["web_app"] = self.web_app.to_dict()
        if self.copy_text:
            button_dict["copy_text"] = self.copy_text
            
        return button_dict

class WebAppInfo:
    def __init__(self, url):
        self.url = url

    def to_dict(self):
        return {"url": self.url}

class CopyTextButton(InlineKeyboardButton):
    def __init__(self, text: str, copy_text: str):
        super().__init__(text=text, copy_text=copy_text)