class Note:
    """
    Представляет заметку с именем и текстом.
    """
    def __init__(self,id=None,title="",content=""):
        """
        Представляет заметку с именем и текстом.

        Args:
            id = ID заметки
            name = Имя заметки
            text = Текст заметки
        """
        self.id = id
        self.title = title
        self.content = content
    

    def editContent(self,newContent):
        """
        Редактируем текст зметки.

        Args:
            newContent = Новый текст заметки
        """

        self.content = newContent

    def getTitle(self):
        """
        Получаем имя заметки.
        """
        return self.title
    

    def getContent(self):
        """
        Получаем текст заметки
        """
        return self.content
    
    def setContent(self,content):
        """
        Устанавливаем текст заметки.

        Args:
            content = Текст заметки
        """
        self.content = content
    
    def setTitle(self,title):
        """
        Устанавливаем имя заметки.

        Args:
            title = Имя заметки
        """
        self.title = title