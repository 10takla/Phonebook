# файл *.pyw (расширение .pyw необходимо для подавления окна DOS)

from tkinter import *  # импорт объектов для графики
from tkinter.messagebox import *  # импорт объектов для диалоговых окон
import shelve  # импорт модуля для работы с базой данных


class PhoneBook:
    # класс Телефонная книга
    def __init__(self, nameBook, dicRec={}):
        # метод инициализации атрибутов экземпляров класса  и передача в метод значений для атрибутов
        self.nameBook = nameBook  # инициализация атрибута Имя книги
        self.dicRec = dicRec  # перечень записей в виде словаря, по умолчанию пустой

    def loadBook(self):
        # загрузка записей из базы данных
        db = shelve.open(self.nameBook)  # открытие базы данных (имя берется из атрибута nameBook экземпляра класса)
        self.dicRec = dict(
            db.items())  # загрузка записей из базы данных в атрибут dicRec экземпляра класса (в словарь экземпляра класса)
        db.close()  # закрытие базы данных

    def saveBook(self):
        # сохранение записей в базе данных
        db = shelve.open(self.nameBook)  # открытие базы данных
        for (key, record) in self.dicRec.items():  # запись содержимого из 
            db[key] = record  # словаря экземпляра класса в базу данных
        db.close()  # закрытие базы данных


class PhoneRec:
    # класс Запись
    def __init__(self, keyRec, char, label, phone, familyName, comment, delR=''):
        # инициализация атрибутов экземпляров класса
        self.keyRec = keyRec  # ключ записи
        self.char = char  # буква, на странице которой находится запись
        self.label = label  # метка, к чему относится запись
        self.phone = phone  # телефон
        self.familyName = familyName  # Ф.И.О.
        self.comment = comment  # комментарий
        self.delR = delR  # служебное поле для пометки записи:
        # ''- видимая, 'с' - скрытая, 'у' - удаляемая


fieldnamesRec = ('keyRec', 'char', 'label', 'phone', 'familyName', 'comment', 'delR')  # кортеж имен полей в записи
activCh = 'А'  # буква, актмвная на текущий момент
typeRec = ''  # тип выводимых на экран записей, '' - открытые, "с" - скрытые
dicRem = {}  # словарь оставшихся не выведенными записей


def onDeleteRequest():
    #    print('Got wm delete') # щелчок на кнопке X в окне: можно отменить или перехватить
    saveRec()
    window.destroy()  # возбудит событие <Destroy>


# def doRootDestroy(event):
#    print('Got event <destroy>') # для каждого виджета в корневом окне
def makeWidgets():
    # создание графической формы
    global entriesRec, entRec, lab1, alph  # перечень глобальных переменных, которые будут использоваться и за пределами функции
    entRec = {}  # словарь, в который будут заносится объекты ввода entFind (поиск) и entKeyRec (ключ)
    window = Tk()  # создание главного окна
    window.title('Телефоны')  # заголовок окна
    window.geometry('1760x700+0+0')  # размеры окна
    #    window.bind('<Destroy>', doRootDestroy)              # для корневого и дочерних
    window.protocol('WM_DELETE_WINDOW', onDeleteRequest)  # на кнопке X окна (перехватывает нажатие кнопки Х)
    form1 = Frame(window)  # создание внутри окна window контейнера form1
    form1.pack()
    lab1 = Label(form1, text=activCh, fg="#eee", bg="#333", width=5)  # метка, показывающая
    lab1.pack(side=LEFT)  # активную букву
    Label(form1, text='  ', width=30).pack(side=LEFT)  # вспомагательная пустая метка для улучшения расположения
    alph = ["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т",
            "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Э", "Ю", "Я"]  # список букв
    for i in range(len(alph)):  # создание кнопок с буквами
        Button(form1, text=alph[i], command=(lambda x=alph[i]: fetchChr(x))).pack(side=LEFT)
    ent = Entry(form1, width=27)  # поле ввода для поиска
    ent.pack(side=LEFT)
    entRec['entFind'] = ent  # поместить объект поля ввода в словарь entRec
    Button(form1, text="Поиск", command=fetchFind).pack(side=LEFT)  # создание кнопки Поиск

    form2 = Frame(window)  # создание внутри окна window контейнера form2
    form2.pack()
    entriesRec = {}  # словарь, для занесения в него объектов Entry ячеек таблицы ввода записей
    fieldnamesRecCyr = ('№№', 'Буква', 'Метка', 'Телефон', 'ФИО', 'Комментарий', 'тип')  # кортеж имен полей на руском
    for (ix, label) in enumerate(fieldnamesRecCyr):  # создание надписей заголовков столбцов таблицы
        lab = Label(form2, text=label)
        lab.grid(row=2, column=ix)
    for i in range(1, 26):  # создаются ячейки таблицы для ввода записей
        for (ix, label) in enumerate(fieldnamesRec):
            if label == 'keyRec' or label == 'char' or label == 'delR':  # выделяются столбцы, которые потом будут иметь особый режим доступа
                ent = Entry(form2, state='normal', width=6)
            else:
                ent = Entry(form2, width=40)
            ent.grid(row=i + 2, column=ix)
            entriesRec[label + str(i)] = ent  # объекты ячеек таблицы заносятся в словарь, причем к имени
            # столбца ячейки добавляется номер строки,
            # тем самым однозначно определяются координаты ячейки,
            # что бы к ней обращаться
    form3 = Frame(window)  # создание внутри окна window контейнера form3
    form3.pack()
    Button(window, text="Следующая страница", command=fetchNext).pack()  # кнопка Следующая страница
    Label(window, text='      ', width=10).pack(side=LEFT)  # вспомогательная пустая метка
    labKeyRec = Label(window, text='№').pack(side=LEFT)  # надпись перед полем ввода номера ключа
    ent = Entry(window, width=10)  # поле ввода номера ключа
    ent.pack(side=LEFT)
    entRec['entKeyRec'] = ent  # занесение объекта поле ввода номера ключа в словарь entRec
    Button(window, text="Скрыть", command=hideRec).pack(side=LEFT)  # кнопка Скрыть (запись)
    Button(window, text="Показать скрытые", command=fetchHide).pack(side=LEFT)  # кнопка Показать скрытые
    Button(window, text="Открыть", command=openRec).pack(side=LEFT)  # кнопка Открыть (запись)
    Label(window, text=' ', width=5).pack(side=LEFT)  # вспомогательная пустая метка
    Button(window, text="Удалить", command=delKeyRec).pack(side=LEFT)  # кнопка удалить (запись)
    Label(window, text='      ', width=30).pack(side=LEFT)  # вспомогательная пустая метка
    btns = Button(window, text="Сохранить", command=interSave).pack(side=LEFT)  # кнопка Сохранить (страницу)
    Label(window, text='      ', width=20).pack(side=LEFT)  # вспомогательная пустая метка
    Button(window, text="Выход", command=fin).pack(side=LEFT)  # кнопка Выход (из программы)
    return window  # функция makeWidgets возвращает окно window


def clear_sheet():
    # очистка листа
    for i in range(1, 26):
        for field in fieldnamesRec:
            if field == 'keyRec' or field == 'delR':  # для очистки полей keyRec и delR,
                entriesRec[field + str(i)].config(state='normal')  # нужно открыть их для записи
                entriesRec[field + str(i)].delete(0, END)
                entriesRec[field + str(i)].config(state='readonly')
            else:
                entriesRec[field + str(i)].delete(0, END)  # очистка остальных полей


def fetchChr(ch):
    # выбрать записи на букву ch
    global activCh, typeRec, lab1
    saveRec()  # предварительно сохранить предыдущую страницу
    typeRec = ''  # выбор для буквы делать только из открытых записей
    activCh = ch  # сделать ch текущей буквой
    lab1.config(text=activCh)  # написать, для какой буквы выводятся записи
    dicRecChr = {}  # словарь, в который помещаются выбранные записи
    for key in t1.dicRec.keys():  # выбор записей и помещение их в словарь
        if t1.dicRec[key].char == ch:
            dicRecChr[key] = t1.dicRec[key]
    fetch(dicRecChr)  # вывод записей в таблицу формы


def interSave():
    # # принудительное сохранение текущей страницы и повторный вывод записей для этой буквы начиная с первой страницы
    fetchChr(activCh)


def fetchHide():
    # вывод скрытых записей
    global typeRec, lab1
    saveRec()
    lab1.config(text='скр')
    typeRec = 'с'
    fetch(t1.dicRec)


def fetch(dicR):
    # вывод записей из заданнго словаря
    global dicRem  # словарь записей, оставшихся не выведенными
    clear_sheet()  # очистка таблицы
    count = 1  # счетчик показывающий номер строки, в которую выводится запись
    dicRe = dicR.copy()  # словарь, ведущий учет записей, которые еще не выведены
    while count <= 25 and len(dicRe):  # в цикле, заполнение строк таблицы записями
        for key in dicR.keys():  # в цикле вывод записи удовлетворяющей условию
            if dicR[key].delR == typeRec:
                record = dicR[key]  # запись для вывода
                for field in fieldnamesRec:  # в цикле последовательное заполнение полей в строке
                    if field == 'keyRec' or field == 'delR':  # поля, которые необходимо открыть для записи
                        entriesRec[field + str(count)].config(state='normal')
                        entriesRec[field + str(count)].insert(0, getattr(record, field))
                        entriesRec[field + str(count)].config(state='readonly')
                    else:
                        entriesRec[field + str(count)].insert(0, getattr(record, field))  # все остальные поля
                count += 1  # переход к следующей строке таблицы
                dicRe.pop(key)  # удаление записи, которая выведена из словаря учета оставшихся записей
                if count > 25:  # если все строки таблицы заполнены, то выход из цикла while
                    break
            else:
                dicRe.pop(key)  # удаление из словаря учета записи, которая не удовлетворяет условию вывода в таблицу
    dicRem = dicRe.copy()  # словарь записей, оставшихся не выведенными


def fetchNext():
    # вывод на следующей странице записей, оставшихся не выведенными
    saveRec()
    fetch(dicRem)


def delKeyRec():
    # физическое удаление из базы данных записи, которая указана в ячейке entKeyRec
    key = entRec['entKeyRec'].get()  # из ячейки entKeyRec берется ключ записи для удаления
    if askyesno('Подтверждение', 'Удалить запись без возможности востановления?'):  # подтверждение на удаление
        del t1.dicRec[key]  # запись удаляется из динамического словаря t1.dicRec
        db = shelve.open(t1.nameBook)  # открывается база данных
        del db[key]  # указанная запись физически удаляется из базы данных
        db.close()  # база данных закрывается
        for i in range(1, 26):  # ищется строка таблицы с этой записью, и помечается как удаленная,
            if entriesRec['keyRec' + str(i)].get() == key:  # что бы потом при сохранении страницы,
                entriesRec['delR' + str(i)].config(state='normal')  # она не была вновь занесена в базу данных
                entriesRec['delR' + str(i)].insert(0, 'у')
                entriesRec['delR' + str(i)].config(state='readonly')
        entRec['entKeyRec'].delete(0, END)  # очищается ячейка, содержащая номер удаляемой записи
    else:
        showinfo('Отмена', 'Удаление записи отменено')  # удаление отменено


def hideRec():
    # пометить как скрытую
    key = entRec['entKeyRec'].get()  # из ячейки entKeyRec берется ключ записи для сокрытия
    for i in range(1, 26):  # ищется строка таблицы с этой записью, и помечается как скрытая
        if entriesRec['keyRec' + str(i)].get() == key:
            entriesRec['delR' + str(i)].config(state='normal')
            entriesRec['delR' + str(i)].insert(0, 'с')
            entriesRec['delR' + str(i)].config(state='readonly')
    entRec['entKeyRec'].delete(0, END)  # очищается ячейка, содержащая номер скрываемой записи записи


def openRec():
    # открыть скрытую запись
    key = entRec['entKeyRec'].get()  # из ячейки entKeyRec берется ключ записи для открытия
    for i in range(1, 26):  # ищется строка таблицы с этой записью, и помечается как открытая
        if entriesRec['keyRec' + str(i)].get() == key:
            entriesRec['delR' + str(i)].config(state='normal')
            entriesRec['delR' + str(i)].delete(0, END)
            entriesRec['delR' + str(i)].insert(0, '')
            entriesRec['delR' + str(i)].config(state='readonly')
    entRec['entKeyRec'].delete(0, END)  # очищается ячейка, содержащая номер открываемой записи


def fetchFind():
    # поиск записей по заданной строке
    global lab1
    saveRec()
    clear_sheet()
    lab1.config(text='поиск')  # сигнализирует о режиме поиска
    strF = entRec['entFind'].get().lower()  # строка для поиска берется из ячейки entFind
    dicFind = {}  # словарь, для занесения в него найденных записей
    for key in t1.dicRec.keys():  # в тлефонном справочнике ищутся записи содержащие искомую строку
        record = t1.dicRec[key]
        for field in fieldnamesRec:
            if (
                    field != 'keyRec' and field != 'char' and field != 'delR' and  # поиск в полях, за исключением перечисленных
                    getattr(record, field).lower().find(strF) != -1):
                dicFind[key] = record
                break
    fetch(dicFind)  # вывод найденных записей


def saveRec():
    # сохранение текущей страницы
    global typeRec
    for i in range(1, 26):  # просмотр строк и при наличии хотя бы в одном поле строки данных, сохранение ее
        key = entriesRec['keyRec' + str(i)].get()  # проверка наличия в строке ключа
        if entriesRec['delR' + str(i)].get() == 'у':  # записи помеченные как удаленные пропускаются
            continue
        elif key:  # иначе, если запись не удаленная и с ключом, то она перезаписывается
            record = t1.dicRec[key]
            for field in fieldnamesRec:
                setattr(record, field, entriesRec[field + str(i)].get())
            t1.dicRec[key] = record
        else:  # иначе, если в строке нет ключа, но в одном из полей есть данные, то создается запись-экземпляр
            existRec = False  # и помещается а словарь t1.dicRec
            for field in fieldnamesRec:
                if entriesRec[field + str(i)].get(): existRec = True  # Если существует запись в поле на этой строке
            if existRec:  # если данные в строке существуют, то создается запись
                if entriesRec['char' + str(i)].get():  # если поле буквы не пусто, то в запись заносится эта буква
                    char = entriesRec['char' + str(i)].get()
                else:  # иначе в запись заносится буква, являющаяся на данный момент активной
                    char = activCh
                label = entriesRec['label' + str(i)].get()  # заполняются переменные
                phone = entriesRec['phone' + str(i)].get()  # для формирования записи
                familyName = entriesRec['familyName' + str(i)].get()
                comment = entriesRec['comment' + str(i)].get()
                if len(t1.dicRec) > 0:  # если телефонный справочник не пуст, то к максимальному значению ключа
                    L = sorted(t1.dicRec.items(), key=lambda item: int(item[0]))  # прибавляется единица
                    keyRec = str(int(L[-1][0]) + 1)
                else:  # иначе записи присваивается ключ равный 1
                    keyRec = "1"
                record = PhoneRec(keyRec, char, label, phone, familyName,
                                  comment)  # создается запись, экземпляр класса PhoneRec
                t1.dicRec[keyRec] = record  # и записывается в словарь t1.dicRec
    t1.saveBook()  # словарь t1.dicRec сохраняется во внешней базе данных "Телефоны"


def fin():  # сохранение перед закрытием окна
    saveRec()
    window.destroy()


if __name__ == '__main__':
    t1 = PhoneBook("Телефоны")  # создание экземпляра класса PhoneBook
    t1.loadBook()  # загрузка внешней базы данных в словарь t1.dicRec,
    # с которым в дальнейшем будет производится вся работа,
    # перед выгрузкой потом назад в базу данных
    window = makeWidgets()  # создание формы
    fetchChr('А')  # вывод в качестве стартовой страницу с буквой "А"
    window.mainloop()  # передача управления форме