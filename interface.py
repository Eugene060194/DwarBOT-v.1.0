import backend  # Основной программный модуль
from tkinter import *  # Для создания GUI
from tkinter import messagebox   # Для вывода информационных окон
from threading import Thread  # Для создания програмного потока независимо от интерфейса
from PIL import ImageTk, Image  # Для подгрузки в интерфейс png направлений удара

# Смещение иконок ударов в окне программы
dev_HI = 0
# Переменные адаптации под разрешение экрана
xrf = backend.u.xrf
yrf = backend.u.yrf
# Содержит адаптированные под tkinter размеры окна программы
window_size = str(int(400*xrf))+'x'+str(int(400*yrf))

# Создание окна программы
window = Tk()
# Установка иконки окна
window.iconbitmap('icon.ico')
# Установка цвета фона окна
window['bg'] = 'orange'
# Установка названия программы
window.title('DWAR_fight_bot v.1.0')
# Установка прозрачности окна
window.wm_attributes('-alpha', 0.9)
# Установка размеров окна
window.geometry(window_size)
# Установка запрета на изменение геметрии окна
window.resizable(width=False, height=False)
# Закрепление окна программы над другими окнами
window.wm_attributes('-topmost', 1)


class HitIcon:
    """Управляет отрисовкой иконок последовательности ударов
    в окне программы
    """
    # Величина смещения иконок по оси x относительно координаты первой иконки
    __dev_HI = 0
    # Визуализируемый список комбинации удара
    __hit_icons = []
    # Подгрузка изображений для иконок ударов
    __HIT_IMAGE_FORWARD = ImageTk.PhotoImage(Image.open('images/hit_forward.gif'))
    __HIT_IMAGE_UP = ImageTk.PhotoImage(Image.open('images/hit_up.gif'))
    __HIT_IMAGE_DOWN = ImageTk.PhotoImage(Image.open('images/hit_down.gif'))
    __hits_dir = {'up': __HIT_IMAGE_UP, 'forward': __HIT_IMAGE_FORWARD, 'down': __HIT_IMAGE_DOWN}

    def __init__(self, direction):
        self.direction = direction
        # Присвоение иконке необходимой картинки на основе заданного направления
        self.icon = HitIcon.__hits_dir[direction]

    def __draw_icon(self):
        """
        Функция объявления и отрисовки иконки

        :return: -
        """
        hit_icon = Label(window, image=self.icon)
        hit_icon.place(x=(180 + HitIcon.__dev_HI) * xrf, y=235 * yrf, width=25 * xrf, height=25 * yrf)
        HitIcon.__hit_icons.append(hit_icon)

    def add_hit(self):
        """
        Функция добавления удара. Включает в себя:
        - отрисовку иконки в окне программы
        - установка смещения координаты x для следующей иконки
        - добавление удара в последовательность для backend-кода

        :return: -
        """
        self.__draw_icon()
        HitIcon.set_icons_deviation()
        backend.u.hit_list.append(self.direction)

    @staticmethod
    def set_icons_deviation():
        """
        Функция увеличивает переменную координаты x для отрисоки иконок ударов.

        :return: -
        """
        HitIcon.__dev_HI += 25

    @staticmethod
    def clean_hits_icons():
        """
        Данная функция привязана к кнопке "CLEAN" в окне программы.
        При нажатии на кнопку полностью очистит текущую комбинацию ударов.

        :return: -
        """
        # Уничтожение иконок в окне программы
        for i in HitIcon.__hit_icons:
            i.destroy()
        HitIcon.__hit_icons = []
        # Обнуление списка комбинации в backend-коде
        backend.u.hit_list = []
        # Обнуление смещения иконок
        HitIcon.__dev_HI = 0

    @staticmethod
    def set_default_hit_combo():  # Функция установки комбинации по умолчанию (на основе backend-кода)
        """
        Данная функция запускается при создании окна программы.
        Отрисовывает дефолтную комбинацию ударов на основе
        переменной backend-кода

        :return: -
        """
        # Цикл перезаполнения комбинации и отрисовки в окне программы
        for i in backend.u.hit_list:
            if i == 'forward':
                HitIcon('forward').__draw_icon()
                HitIcon.set_icons_deviation()
            elif i == 'down':
                HitIcon('down').__draw_icon()
                HitIcon.set_icons_deviation()
            elif i == 'up':
                HitIcon('up').__draw_icon()
                HitIcon.set_icons_deviation()


def start():  # Функция кнопки "Старт" (Запуск программы)
    """
    Данная функция привязана к кнопке "Старт" в окне программы.
    При нажатии собирает параметры из окон ввода, передает их
    в backend-код, обновляя его переменные, и запускает
    основую функцию backend-кода.

    :return: -
    """
    # Проверка на наличие комбинации ударов (без комбинации программа работать не будет)
    if backend.u.hit_list:
        # Передача в backend-код значений переменных из полей ввода
        backend.u.min_hp_in_fight = a.get()
        backend.u.max_hp_without_block = b.get()
        backend.u.max_creature_without_help = c.get()
        backend.u.delay_factor = d.get()
        backend.work = True
        # Запуск программы в отдельном потоке (независимо от интерфейса)
        th = Thread(target=backend.bot_start)
        th.start()
    else:
        messagebox.showinfo('Внимание!', 'Задайте последовательность ударов!')


def stop():  # Функция кнопки "Стоп" (Остановка программы)
    """
    Данная функция привязана к кнопке "Стоп" в окне программы.
    При нажатии запускает соответствующую функцию в backend-коде программы.

    :return: -
    """
    backend.bot_stop()


# Объявление переменных для полей ввода
a = IntVar()
b = IntVar()
c = IntVar()
d = IntVar()

# Создание текстовых виджетов
NAME_0 = Label(text='Входные данные')
NAME_0.place(x=150*xrf, y=10*yrf, width=100*xrf, height=25*yrf)
NAME_1 = Label(text='Порог применения эликсира:')
NAME_1.place(x=20*xrf, y=40*yrf, width=260*xrf, height=25*yrf)
NAME_2 = Label(text='Порог входа в блок:')
NAME_2.place(x=20*xrf, y=70*yrf, width=260*xrf, height=25*yrf)
NAME_3 = Label(text='Порог врагов для вызова ездового:')
NAME_3.place(x=20*xrf, y=100*yrf, width=260*xrf, height=25*yrf)
NAME_4 = Label(text='Коэффициент задержки:')
NAME_4.place(x=20*xrf, y=130*yrf, width=260*xrf, height=25*yrf)
NAME_5 = Label(text='Последовательность ударов')
NAME_5.place(x=115*xrf, y=165*yrf, width=170*xrf, height=25*yrf)

# Создания полей ввода для соответствующих текстовых виджетов
input_1 = Entry(textvariable=a)
input_1.delete(0, END)
input_1.insert(0, backend.u.min_hp_in_fight)
input_1.place(x=320*xrf, y=40*yrf, width=60*xrf, height=25*yrf)
input_2 = Entry(textvariable=b)
input_2.delete(0, END)
input_2.insert(0, backend.u.max_hp_without_block)
input_2.place(x=320*xrf, y=70*yrf, width=60*xrf, height=25*yrf)
input_3 = Entry(textvariable=c)
input_3.delete(0, END)
input_3.insert(0, backend.u.max_creature_without_help)
input_3.place(x=320*xrf, y=100*yrf, width=60*xrf, height=25*yrf)
input_4 = Entry(textvariable=d)
input_4.delete(0, END)
input_4.insert(0, backend.u.delay_factor)
input_4.place(x=320*xrf, y=130*yrf, width=60*xrf, height=25*yrf)

# Создания кнопок для установки комбинации ударов
UP_HIT_BUTTON = Button(text='UP', command=HitIcon('up').add_hit)
UP_HIT_BUTTON.place(x=95*xrf, y=200*yrf, width=40*xrf, height=25*yrf)
FORWARD_HIT_BUTTON = Button(text='FOR', command=HitIcon('forward').add_hit)
FORWARD_HIT_BUTTON.place(x=95*xrf, y=235*yrf, width=40*xrf, height=25*yrf)
DOWN_HIT_BUTTON = Button(text='DOWN', command=HitIcon('down').add_hit)
DOWN_HIT_BUTTON.place(x=95*xrf, y=270*yrf, width=40*xrf, height=25*yrf)
CLEAN_BUTTON = Button(text='CLEAN', command=HitIcon.clean_hits_icons)
CLEAN_BUTTON.place(x=40*xrf, y=235*yrf, width=40*xrf, height=25*yrf)

# Создания кнопок "Старт" и "Стоп"
START_BUTTON = Button(text='СТАРТ', command=start)
START_BUTTON.place(x=60*xrf, y=305*yrf, width=100*xrf, height=25*yrf)
STOP_BUTTON = Button(text='СТОП', command=stop)
STOP_BUTTON.place(x=240*xrf, y=305*yrf, width=100*xrf, height=25*yrf)

# Отрисовка дефолтной комбинации ударов
HitIcon.set_default_hit_combo()

# Программный цикл tkinter
window.mainloop()
