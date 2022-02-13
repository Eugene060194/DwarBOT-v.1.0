import numpy as np  # Используется в алгоритме поиска совпадений OpenCV
import pyautogui as pg  # Для автоматизации действий мыши
import cv2  # Для распознавания изображений на экране
import configparser  # Для связи программы с конфигурационным файлом
from time import sleep  # Для создания пауз в работе программы
from PIL import ImageGrab  # Для создания и сохранения скриншотов экрана (для OpenCV)
from pytesseract import image_to_string  # Для распознавания экранного текста

# Блок для адаптации всех координат (для pyautogui) под текущее разрешение экрана
DEFAULT_RESOLUTION = (1920, 1080)
current_resolution = pg.size()
# Коэффициенты приведения координат к текущему разрешению.
xrf = current_resolution[0] / DEFAULT_RESOLUTION[0]
yrf = current_resolution[1] / DEFAULT_RESOLUTION[1]

# Присвоение программным переменным дефолтного значения из файла конфигурации
config = configparser.ConfigParser()
config.read('config.ini')
# Порог хитпоинтов в бою, ниже которого программа будет применять эликсиры
min_hp_in_fight = int(config['options']['min_hp_in_fight'])
# Порог противников в бою, выше которого программа вызовет ездовое животное
max_creature_without_help = int(config['options']['max_creature_without_help'])
# Порог хитпоинтов в бою, ниже которого программа встанет в блок (режим защиты)
max_hp_without_block = int(config['options']['max_hp_without_block'])
# Переменная задержки действий. Увеличивает задержки(time.sleep()) между основными кликами программы
delay_factor = float(config['options']['delay_factor'])

# Хранит последовательность для суперудара в бою
hit_list = config['hits_seq']['hit_list'].split(', ')


class ScreenAnalyze:
    """Выполняет оперции анализа экрана.
    Предоставляет методы для решения конкретных задач программы.
    """
    # Переменные для хранения изображений-шаблонов (для сравнения через OpenCV)
    __TEMP_IMAGE_1 = cv2.imread('images/win_image.png', 0)
    __TEMP_IMAGE_2 = cv2.imread('images/hit_image.png', 0)
    __TEMP_IMAGE_3 = cv2.imread('images/busy_creature.png', 0)
    __TEMP_IMAGE_4 = cv2.imread('images/defeat_image.png', 0)
    __TARGET_CREATURE = cv2.imread('creature_text.png', 0)
    # Переменные для хранения текстовых шаблонов (для сравнения через tesseract)
    __ERROR_TEXT1 = 'Цель еще не восстановилась!'
    __ERROR_TEXT2 = 'Не удалось выполнить действие "Напасть на монстра"!'
    __ERROR_TEXT3 = 'Выберите объект действия'
    __SEARCH_TEXT1 = 'выход'

    @staticmethod
    def __find_pattern_on_screen(base_image, x1, y1, x2, y2, threshold):
        """
        Функция для проверки текущего изображения на наличие шаблонов внутри.
        Для поиска шаблонов используется OpenCV.

        :param base_image: Шаблон (то, что ищем)
        :param x1: Координата X первой точки для скриншота
        :param y1: Координата Y первой точки для скриншота
        :param x2: Координата X второй точки для скриншота
        :param y2: Координата Y второй точки для скриншота
        :param threshold: Порог соответствия скриншота шаблону
        :return: Список координат [x, y], где был найден шаблон.
        """
        # Создание, сохранение и перевод скриншота в формат для OpenCV
        screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        path = 'images/base_screen.png'
        screen.save(path)
        rgb = cv2.imread(path)
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        # Поиск шаблона в текущем скриншоте
        res = cv2.matchTemplate(gray, base_image, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        # Получение координат места нахождения шаблона в скриншоте
        x, y = (0, 0)
        for pt in zip(*loc[::-1]):
            x = int(pt[0])
            y = int(pt[1])
        x += (202 * xrf)
        y += (270 * yrf)
        return [int(x), int(y)]

    @staticmethod
    def __check_image_on_screen(base_image, x1, y1, x2, y2, threshold):
        """
        Функция для проверки текущего изображения на наличие шаблонов внутри.
        Для поиска шаблонов используется OpenCV.

        :param base_image: Шаблон (то, что ищем)
        :param x1: Координата X первой точки для скриншота
        :param y1: Координата Y первой точки для скриншота
        :param x2: Координата X второй точки для скриншота
        :param y2: Координата Y второй точки для скриншота
        :param threshold: Порог соответствия скриншота шаблону
        :return: В зависимости от наличия шаблона на экране True/False.
        """
        # Создание, сохранение и перевод скриншота в формат для OpenCV
        screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        path = 'images/base_screen.png'
        screen.save(path)
        rgb = cv2.imread(path)
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        # Поиск шаблона в текущем скриншоте
        res = cv2.matchTemplate(gray, base_image, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        # Проверка на наличие шаблона внутри скриншота
        if np.any(loc):
            return True
        else:
            return False

    @staticmethod
    def __get_int_from_screen(x1, y1, x2, y2):
        """
        Функция для распознавания экранного текста на скриншоте.
        Для распознавания используется tesseract.

        :param x1: Координата X первой точки для скриншота
        :param y1: Координата Y первой точки для скриншота
        :param x2: Координата X второй точки для скриншота
        :param y2: Координата Y второй точки для скриншота
        :return: Распознанное целое число int.
        """
        # Создание скриншота с текстом
        screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        # Распознование числа на скриншоте
        text = image_to_string(screen, config=r'--oem 3 --psm 13')
        text = text.split('/')[0]
        text = text.split('\n')[0]
        # Перехват исключения, в случае некорректного распознавания числа
        try:
            return int(text)
        except ValueError:
            return 600

    @staticmethod
    def __check_text_on_screen(x1, y1, x2, y2, search_text):
        """
        Функция для распознавания экранного текста на скриншоте.
        Для распознавания используется tesseract.

        :param x1: Координата X первой точки для скриншота
        :param y1: Координата Y первой точки для скриншота
        :param x2: Координата X второй точки для скриншота
        :param y2: Координата Y второй точки для скриншота
        :param search_text: Текстовый шаблон (то, что ищем). В режиме int задавать пустую строку.
        :return: В зависимости от наличия текста на экране True/False.
        """
        # Создание скриншота с текстом
        screen = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        # Проверка на соответствие текстовому шаблону
        text = image_to_string(screen, lang='rus', config=r'--oem 3 --psm 13')
        text = text.split('\n')[0]
        try:
            if text == search_text:
                return True
            else:
                return False
        except ValueError:
            return False

    @staticmethod
    def find_target_creature():
        rez = ScreenAnalyze.__find_pattern_on_screen(ScreenAnalyze.__TARGET_CREATURE, 202 * xrf, 270 * yrf,
                                                     1702 * xrf,
                                                     745 * yrf, 0.9)
        if rez == [int(202 * xrf), int(270 * yrf)]:
            return [False, False]
        return rez

    @staticmethod
    def get_fight_status():
        while True:
            if ScreenAnalyze.__check_image_on_screen(ScreenAnalyze.__TEMP_IMAGE_2, 469 * xrf, 399 * yrf, 493 * xrf,
                                                     433 * yrf, 0.7):
                return 'hit'
            elif ScreenAnalyze.__check_text_on_screen(525 * xrf, 416 * yrf, 565 * xrf, 427 * yrf,
                                                      ScreenAnalyze.__SEARCH_TEXT1):
                if ScreenAnalyze.__check_image_on_screen(ScreenAnalyze.__TEMP_IMAGE_1, 407 * xrf, 301 * yrf, 689 * xrf,
                                                         429 * yrf, 0.7):
                    return 'win'
                elif ScreenAnalyze.__check_image_on_screen(ScreenAnalyze.__TEMP_IMAGE_4, 407 * xrf, 301 * yrf,
                                                           689 * xrf,
                                                           429 * yrf, 0.7):
                    return 'defeat'

    @staticmethod
    def get_hp_amount():
        return ScreenAnalyze.__get_int_from_screen(349 * xrf, 229 * yrf, 385 * xrf, 242 * yrf)

    @staticmethod
    def get_enemies_amount():
        return ScreenAnalyze.__get_int_from_screen(1168 * xrf, 233 * yrf, 1181 * xrf, 247 * yrf)

    @staticmethod
    def handling_error_1():
        return ScreenAnalyze.__check_text_on_screen(872 * xrf, 459 * yrf, 1050 * xrf, 474 * yrf,
                                                    ScreenAnalyze.__ERROR_TEXT1)

    @staticmethod
    def handling_error_2():
        return ScreenAnalyze.__check_text_on_screen(791 * xrf, 454 * yrf, 1133 * xrf, 477 * yrf,
                                                    ScreenAnalyze.__ERROR_TEXT2)

    @staticmethod
    def handling_error_3():
        return ScreenAnalyze.__check_text_on_screen(665 * xrf, 227 * yrf, 810 * xrf, 240 * yrf,
                                                    ScreenAnalyze.__ERROR_TEXT3)

    @staticmethod
    def busy_creature_error():
        return ScreenAnalyze.__check_image_on_screen(ScreenAnalyze.__TEMP_IMAGE_3, 796 * xrf, 481 * yrf, 1124 * xrf,
                                                     624 * yrf,
                                                     0.8)


class Clicker:
    """Предоставляет методы исполнения последовательностей кликов
    для реализации задач программы.
    """
    # Переменная для хранения координат лечебных эликсиров (полный перечень)
    __ELIXIRS_FULL = [((38 * xrf, 221 * yrf),),
                      ((38 * xrf, 266 * yrf),),
                      ((38 * xrf, 308 * yrf),),
                      ((38 * xrf, 353 * yrf),),
                      ((38 * xrf, 395 * yrf),),
                      ((38 * xrf, 440 * yrf),),
                      ((55 * xrf, 471 * yrf), (38 * xrf, 221 * yrf), (15 * xrf, 471 * yrf)),
                      ((55 * xrf, 471 * yrf), (38 * xrf, 266 * yrf), (15 * xrf, 471 * yrf))]
    # Динамическая переменная для хранения координат лечебных эликсиров (меняется в процессе боя)
    __elixirs_current = [((38 * xrf, 221 * yrf),),
                         ((38 * xrf, 266 * yrf),),
                         ((38 * xrf, 308 * yrf),),
                         ((38 * xrf, 353 * yrf),),
                         ((38 * xrf, 395 * yrf),),
                         ((38 * xrf, 440 * yrf),),
                         ((55 * xrf, 471 * yrf), (38 * xrf, 221 * yrf), (15 * xrf, 471 * yrf)),
                         ((55 * xrf, 471 * yrf), (38 * xrf, 266 * yrf), (15 * xrf, 471 * yrf))]
    # Переменная определяющая возможность вызвать ездовое животное (в одном бою можно вызвать только одно ездовое)
    __my_animal_ready = True
    # Хранит координаты ударов (направление удара: нужная координата)
    __direction_of_hit = {'forward': (541 * xrf, 420 * yrf),
                          'down': (512 * xrf, 471 * yrf),
                          'up': (511 * xrf, 372 * yrf)}
    # Хранит координаты для сброса ошибок при нападении на цель (номер ошибки: нужная координата)
    __handling_errors = {'ERROR1/2': (963 * xrf, 514 * yrf),
                         'BUSY_ERROR': (1044 * xrf, 579 * yrf)}

    @staticmethod
    def attack_target_creature(x, y):
        pg.leftClick((x + (54 * xrf)), (y - (25 * yrf)))
        sleep(0.5)
        pg.leftClick(615 * xrf, 226 * yrf)
        sleep(1)

    @staticmethod
    def click_on_block():
        pg.leftClick(428 * xrf, 418 * yrf)

    @staticmethod
    def clicks_on_elixir():
        if Clicker.__elixirs_current:
            for i in Clicker.__elixirs_current[0]:
                pg.leftClick(i[0], i[1])
                sleep(0.2)
            del Clicker.__elixirs_current[0]
            sleep(12)

    @staticmethod
    def click_on_hit(direction):
        pg.leftClick(Clicker.__direction_of_hit[direction][0], Clicker.__direction_of_hit[direction][1])
        sleep(1 + delay_factor * 2)

    @staticmethod
    def summon_my_animal():
        if Clicker.__my_animal_ready:
            pg.leftClick(1885 * xrf, 307 * yrf)
            sleep(1)
            pg.leftClick(263 * xrf, 187 * yrf)
            Clicker.__my_animal_ready = False

    @staticmethod
    def click_on_hunt():
        sleep(0.5 + delay_factor * 0.5)
        pg.leftClick(938 * xrf, 136 * yrf)
        sleep(2 + delay_factor * 2)

    @staticmethod
    def post_battle_refresh():
        # Обновить переменные для эликсиров и для вызова ездового
        Clicker.__elixirs_current = Clicker.__ELIXIRS_FULL
        Clicker.__my_animal_ready = True
        # Восстановить хп после боя
        sleep(0.2 + delay_factor * 0.8)
        pg.leftClick(1875 * xrf, 56 * yrf)
        sleep(0.2 + delay_factor * 0.8)
        pg.leftClick(1804 * xrf, 101 * yrf)
        sleep(0.2 + delay_factor * 0.8)

    @staticmethod
    def resurrection():
        pg.leftClick(886 * xrf, 133 * yrf)
        sleep(2 + delay_factor * 2)
        pg.leftClick(684 * xrf, 308 * yrf)
        sleep(0.3 + delay_factor * 0.7)

    @staticmethod
    def handling_error_click(error):
        pg.leftClick(Clicker.__handling_errors[error][0], Clicker.__handling_errors[error][1])
