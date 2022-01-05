"""Данный код описывает графический интерфейс бота для браузерной
онлайн-игры Легенда: Наследие Драконов. Бот предназначен для
автоматического гринда игровых существ"""

import dwarBOT_backend  # Основной программный модуль
from tkinter import *  # Для создания GUI
from tkinter import messagebox   # Для вывода информационных окон
from threading import Thread  # Для создания програмного потока независимо от интерфейса
from PIL import ImageTk, Image  # Для подгрузки в интерфейс png направлений удара

# Визуализируемый список комбинации удара
hit_icons = []
# Смещение иконок ударов в окне программы
dev_HI = 0
# Переменные адаптации под разрешение экрана
xrf = dwarBOT_backend.xrf
yrf = dwarBOT_backend.yrf
# Содержит адаптированные под tkinter размеры окна программы
window_size = str(int(400*xrf))+'x'+str(int(400*yrf))


def start():  # Функция кнопки "Старт" (Запуск программы)
    """
    Данная функция привязана к кнопке "Старт" в окне программы.
    При нажатии собирает параметры из окон ввода, передает их
    в backend-код, обновляя его переменные, и запускает
    основую функцию backend-кода.

    :return: -
    """
    # Проверка на наличие комбинации ударов (без комбинации программа работать не будет)
    if dwarBOT_backend.hit_list:
        # Передача в backend-код значений переменных из полей ввода
        dwarBOT_backend.min_hp_in_fight = a.get()
        dwarBOT_backend.max_hp_without_block = b.get()
        dwarBOT_backend.max_creature_without_help = c.get()
        dwarBOT_backend.delay_factor = d.get()
        # Запуск программы в отдельном потоке (независимо от интерфейса)
        th = Thread(target=dwarBOT_backend.bot_start)
        th.start()
    else:
        messagebox.showinfo('Внимание!', 'Задайте последовательность ударов!')


def stop():  # Функция кнопки "Стоп" (Остановка программы)
    """
    Данная функция привязана к кнопке "Стоп" в окне программы.
    При нажатии запускает соответствующую функцию в backend-коде программы.

    :return: -
    """
    dwarBOT_backend.bot_stop()


def install_up_hit():  # Функция отрисовки в окне программы ударов вверх (в комбинации ударов)
    """
    Данная функция привязана к кнопке "UP" в окне программы.
    При нажатии отрисовыет иконку выбранного удара в окне программы,
    и добавляет выбранный удар в список комбинации в переменной
    backend-кода.

    :return: -
    """
    global dev_HI, hit_icons
    # Создание и отрисовка выбранного удара (для комбинации)
    hit_icon = Label(window, image=HIT_IMAGE_UP)
    # Иконки ударов отрисовываются друг за другом с помощью переменной dev_HI (смещение)
    hit_icon.place(x=(180+dev_HI)*xrf, y=235*yrf, width=25*xrf, height=25*yrf)
    hit_icons.append(hit_icon)
    # Добавление в комбинацию выбранного удара (в переменной backend-кода)
    dwarBOT_backend.hit_list.append('up')
    # Обновление смещения
    dev_HI += 25


def install_forward_hit():  # Функция отрисовки в окне программы ударов вперед (в комбинации ударов)
    """
    Данная функция привязана к кнопке "FOR" в окне программы.
    При нажатии отрисовыет иконку выбранного удара в окне программы,
    и добавляет выбранный удар в список комбинации в переменной
    backend-кода.

    :return: -
    """
    global dev_HI, hit_icons
    # Создание и отрисовка выбранного удара (для комбинации)
    hit_icon = Label(window, image=HIT_IMAGE_FORWARD)
    # Иконки ударов отрисовываются друг за другом с помощью переменной dev_HI (смещение)
    hit_icon.place(x=(180+dev_HI)*xrf, y=235*yrf, width=25*xrf, height=25*yrf)
    hit_icons.append(hit_icon)
    # Добавление в комбинацию выбранного удара (в переменной backend-кода)
    dwarBOT_backend.hit_list.append('forward')
    # Обновление смещения
    dev_HI += 25


def install_down_hit():  # Функция отрисовки в окне программы ударов вниз (в комбинации ударов)
    """
    Данная функция привязана к кнопке "DOWN" в окне программы.
    При нажатии отрисовыет иконку выбранного удара в окне программы,
    и добавляет выбранный удар в список комбинации в переменной
    backend-кода.

    :return: -
    """
    global dev_HI, hit_icons
    # Создание и отрисовка выбранного удара (для комбинации)
    hit_icon = Label(window, image=HIT_IMAGE_DOWN)
    # Иконки ударов отрисовываются друг за другом с помощью переменной dev_HI (смещение)
    hit_icon.place(x=(180+dev_HI)*xrf, y=235*yrf, width=25*xrf, height=25*yrf)
    hit_icons.append(hit_icon)
    # Добавление в комбинацию выбранного удара (в переменной backend-кода)
    dwarBOT_backend.hit_list.append('down')
    # Обновление смещения
    dev_HI += 25


def clean_hits():  # Функция очистки комбинации ударов
    """
    Данная функция привязана к кнопке "CLEAN" в окне программы.
    При нажатии на кнопку полностью очистит текущую комбинацию ударов.

    :return: -
    """
    global dev_HI, hit_icons
    # Цикл для уничтожения иконок в окне программы
    for i in hit_icons:
        i.destroy()
    # Обнуление списка комбинации в backend-коде
    dwarBOT_backend.hit_list = []
    # Обнуление смещения
    dev_HI = 0


def set_default_hit_combo():  # Функция установки комбинации по умолчанию (на основе backend-кода)
    """
    Данная функция запускается при создании окна программы.
    Отрисовывает дефолтную комбинацию ударов на основе
    переменной backend-кода

    :return: -
    """
    # Берет комбинацию из backend-кода
    hl = dwarBOT_backend.hit_list
    # Очистка backend-кода
    dwarBOT_backend.hit_list = []
    # Цикл перезаполнения комбинации и отрисовки в окне программы
    for i in hl:
        if i == 'forward':
            install_forward_hit()
        elif i == 'down':
            install_down_hit()
        elif i == 'up':
            install_up_hit()


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

# Подгрузка изображений для иконок ударов
HIT_IMAGE_FORWARD = ImageTk.PhotoImage(Image.open('images/hit_forward.gif'))
HIT_IMAGE_UP = ImageTk.PhotoImage(Image.open('images/hit_up.gif'))
HIT_IMAGE_DOWN = ImageTk.PhotoImage(Image.open('images/hit_down.gif'))

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
input_1.insert(0, dwarBOT_backend.min_hp_in_fight)
input_1.place(x=320*xrf, y=40*yrf, width=60*xrf, height=25*yrf)
input_2 = Entry(textvariable=b)
input_2.delete(0, END)
input_2.insert(0, dwarBOT_backend.max_hp_without_block)
input_2.place(x=320*xrf, y=70*yrf, width=60*xrf, height=25*yrf)
input_3 = Entry(textvariable=c)
input_3.delete(0, END)
input_3.insert(0, dwarBOT_backend.max_creature_without_help)
input_3.place(x=320*xrf, y=100*yrf, width=60*xrf, height=25*yrf)
input_4 = Entry(textvariable=d)
input_4.delete(0, END)
input_4.insert(0, dwarBOT_backend.delay_factor)
input_4.place(x=320*xrf, y=130*yrf, width=60*xrf, height=25*yrf)

# Создания кнопок для установки комбинации ударов
UP_HIT_BUTTON = Button(text='UP', command=install_up_hit)
UP_HIT_BUTTON.place(x=95*xrf, y=200*yrf, width=40*xrf, height=25*yrf)
FORWARD_HIT_BUTTON = Button(text='FOR', command=install_forward_hit)
FORWARD_HIT_BUTTON.place(x=95*xrf, y=235*yrf, width=40*xrf, height=25*yrf)
DOWN_HIT_BUTTON = Button(text='DOWN', command=install_down_hit)
DOWN_HIT_BUTTON.place(x=95*xrf, y=270*yrf, width=40*xrf, height=25*yrf)
CLEAN_BUTTON = Button(text='CLEAN', command=clean_hits)
CLEAN_BUTTON.place(x=40*xrf, y=235*yrf, width=40*xrf, height=25*yrf)

# Создания кнопок "Старт" и "Стоп"
START_BUTTON = Button(text='СТАРТ', command=start)
START_BUTTON.place(x=60*xrf, y=305*yrf, width=100*xrf, height=25*yrf)
STOP_BUTTON = Button(text='СТОП', command=stop)
STOP_BUTTON.place(x=240*xrf, y=305*yrf, width=100*xrf, height=25*yrf)

# Отрисовка дефолтной комбинации ударов
set_default_hit_combo()

# Программный цикл tkinter
window.mainloop()
