class Note:
    """
    Представляет заметку с именем и текстом.
    """
    def __init__(self,name="",text=""):
        """
        Представляет заметку с именем и текстом.

        Args:
            name = Имя заметки
            text = Текст заметки
        """
        self.name = name
        self.text = text
    
    '''
    Редактируем текст зметки.
    newText = Новый текст заметки
    '''
    def editText(self,newText):
        """
        Редактируем текст зметки.

        Args:
            newText = Новый текст заметки
        """

        self.text = newText

    def getName(self):
        """
        Получаем имя заметки.
        """
        return self.name
    

    def getText(self):
        """
        Получаем текст заметки
        """
        return self.text
    
    def setText(self,text):
        """
        Устанавливаем текст заметки.

        Args:
            text = Текст заметки
        """
        self.text = text
    
    def setName(self,name):
        """
        Устанавливаем имя заметки.

        Args:
            name = Имя заметки
        """
        self.name = name