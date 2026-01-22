class User:
    def __init__(self, id, telegram_id, username):
        """
        Представляет пользователя
        Args:
            telegram_id = id в телеграме
            username = Имя пользователя в телеграме
        """
        self.id = id
        self.telegram_id = telegram_id
        self.username = username