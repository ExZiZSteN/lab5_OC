class Nodes:
    '''
    Представляет заметку с именем и текстом.
    name = Имя заметки
    text = Текст заметки
    '''
    def __init__(self,name,text):
        self.name = name
        self.text = text
    
    '''
    Редактируем текст зметки.
    newText = Новый текст заметки
    '''
    def editText(self,newText):
        self.text = newText

    '''
    Получаем имя заметки.
    '''
    def getName(self):
        return self.name
    
    '''
    Получаем текст заметки
    '''
    def getText(self):
        return self.text