import backend_utils as u  # Модуль с функциями анализа экрана и кликов

# Определяет актуальное состояние режима блока в бою
block_is_active = False

# Переменная для функции запуска/остановки программы
work = bool


def control_block():  # Функция управления режимом блока
    """
    С помощью функции распознавания текста определяет кол-во текущих hitpoints,
    и на основании этого принимает решение о необходимости включения/выключения режима блока.

    :return: -
    """
    global block_is_active
    # Проверка текущих hp и переменной block_is_active (0 - не в блоке, 1 - в блоке)
    if u.ScreenAnalyze.get_hp_amount() < u.max_hp_without_block and not block_is_active:
        # Встать в блок
        u.Clicker.click_on_block()
        block_is_active = True
    elif u.ScreenAnalyze.get_hp_amount() > u.max_hp_without_block and block_is_active:
        # Выйти из блока
        u.Clicker.click_on_block()
        block_is_active = False


def use_elixir():  # Функция управления эликсирами восстановления hp
    """
    С помощью функции распознавания текста определяет кол-во текущих hitpoints,
    и на основании этого принимает решение о необходимости использования эликсиров
    для восстановления hitpoints.

    :return: -
    """
    # Проверка текущих hp
    if u.ScreenAnalyze.get_hp_amount() < u.min_hp_in_fight:
        u.Clicker.clicks_on_elixir()


def help_exam():  # Функция управления призывом ездового животного.
    """
    С помощью функции распознавания текста определяет кол-во текущих врагов (через цифру на экране),
    и на основании этого принимает решение о необходимости вызова ездового животного.

    :return: -
    """
    # Проверка кол-ва врагов в бою
    if u.ScreenAnalyze.get_enemies_amount() > u.max_creature_without_help:
        u.Clicker.summon_my_animal()


def hunt():
    """
    Функция охоты. Выполняет поиск цели, с последующим нападением и
    отработкой возвомжных всплывающих ошибок.

    :return: -
    """
    # Цикл поиска цели для нападения
    while work:
        u.Clicker.click_on_hunt()
        # Определение координаты монстра для нападения
        target_x, target_y = u.ScreenAnalyze.find_target_creature()
        if not target_x and not target_y:
            continue
        u.Clicker.attack_target_creature(target_x, target_y)
        # Проверка и отработка различных всплывающих ошибок нападения
        if u.ScreenAnalyze.busy_creature_error():
            u.Clicker.handling_error_click('BUSY_ERROR')
            continue
        elif u.ScreenAnalyze.handling_error_1() or u.ScreenAnalyze.handling_error_2():
            u.Clicker.handling_error_click('ERROR1/2')
            continue
        elif u.ScreenAnalyze.handling_error_3():
            continue
        break


def fight():
    """
    Функция проведения боя.

    :return: -
    """
    fight_status = ''
    # Цикл проведения боя
    while work:
        # Переменная для учёта номера текущего удара в последовательности
        hit_value = len(u.hit_list)
        # Цикл нанесения ударов (перебирает список с последовательностью)
        for i in u.hit_list:
            # Получения статуса боя
            fight_status = u.ScreenAnalyze.get_fight_status()
            # Оценка статуса боя
            if fight_status == 'hit':
                # Условие для выхода из режима блока перед супер-ударом (последний в последовательности)
                if hit_value == 1:
                    if block_is_active:
                        control_block()
                # Условие для обычного удара
                else:
                    control_block()
                # Восполение здоровья, если это необходимо
                use_elixir()
                # Нанесение соответствующего удара
                u.Clicker.click_on_hit(i)
            # Условие выхода из боя с победой
            elif fight_status == 'win':
                break
            # Условие выхода из боя с поражением
            elif fight_status == 'defeat':
                break
            # Учёт нанесенного удара (приближение переменной учёта к суперудару)
            hit_value -= 1
        # Условие для естественного выхода из цикла (бой продолжается)
        else:
            # Вызов ездового животного, при необходимости
            help_exam()
            # Повторение цикла боя
            continue
        # Разрушение цикла боя (произойдет при победе или поражении)
        break
    # Проверка выхода из боя с поражением (для дальнейшего возрождения)
    if fight_status == 'defeat':
        u.Clicker.resurrection()


def bot_start():
    """
    Основная функция программы.
    Выполняет последовательность действий для непрерывного
    гринда внутриигровых монтров, пока глобальная
    переменная work - истина.

    :return:
    """
    u.sleep(3)
    while work:
        if not work:
            break
        hunt()
        if not work:
            break
        u.sleep(1 + u.delay_factor * 3)
        fight()
        if not work:
            break
        u.sleep(1)
        u.Clicker.post_battle_refresh()
        if not work:
            break
        u.sleep(1)


def bot_stop():  # Функция для остановки программы
    """
    Останавливает работу программы путем изменения переменной
    work.

    :return: -
    """
    global work
    work = False


# Проверка прямого запуска кода
if __name__ == '__main__':
    work = True
    bot_start()
