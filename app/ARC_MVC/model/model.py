import os # Импортируем библиотеку для работы с системой (файлы)
from datetime import datetime # Импортируем библиотеку для работы с временем

from PyQt6.QtCore import (QRegularExpression, Qt) # Для регулярных выражений
from PyQt6.QtGui import QRegularExpressionValidator # Валидатор 
 


class Validators:
    """
    Класс, содержащий статические методы для валидации данных в форме.
    Класс с валидаторами для разных типов данных
    """

    @staticmethod # Статический метод, можем вызвать без экземпляра класса
    def name_validator(): # объявляем функцию для валидации имени
        regex = QRegularExpression("[A-Za-zА-Яа-яёЁ\\s-]{2,50}") # регулярное выражение все буквы английского и русского алфавита([A-Za-zА-Яа-я) так же 
        # буквы ёЁ(ёЁ) так как они не входят в А-Яа-я дальше пробельные символы(\\s) и дефис(-]) строка должна содержать от 2 до 50 символов ({2, 50})
        return QRegularExpressionValidator(regex) # возвращаем переработанное регулярное выражение

    @staticmethod # Статический метод, можем вызвать без экземпляра класса
    def date_validator(): # объявляем функцию для валидации даты
        regex = QRegularExpression("20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])") # 20 - первые две цифры, [0-9] любая цифра от 1 до 9 {2} 2 цифры 
        # -(0[1-9]|1[0-2]) если первая цифра 0 то следующая от 1 до 9 если первая цифра 1 следующая от 0 до 2 валидация месяцев -(0[1-9]|[12][0-9]|3[01]) если цифра 0 следующая от 1 до 9
        # если цифра 1 или 2 следующая от 1 до 9 если 3 то либо 0 либо 1
        return QRegularExpressionValidator(regex) # возвращаем переработанное регулярное выражение

    @staticmethod # Статический метод, можем вызвать без экземпляра класса
    def area_validator(): # объявляем функцию для валидации зарплаты
        regex = QRegularExpression("\\d{1,12}") # зарплата от 1 до 12 цифр
        return QRegularExpressionValidator(regex) # возвращаем переработанное регулярное выражение

    @staticmethod
    def floors_validator():
        regex = QRegularExpression("^(1[0-1][0-9]|120|[1-9][0-9]?)$") # этажность от 1 до 120
        return QRegularExpressionValidator(regex)


class Model:
    """
    Класс бизнес логики
    """

    def open_file(self, FileTab, file_name, headers): # обьявляем функцию принимающую другой класс FileTab и экземпляр класса
        if file_name: # Если пользователь выбрал файл
            try: # конструкция try except обработка исключений
                with open(file_name, "r", encoding="utf-8") as file: # пробуем открыть файл
                    first_line = file.readline().strip() # читаем первую строку файла, убираем пробелы с двух сторон
                    if first_line != "###OBJECT_DB###": # Проверка на наш формат файла (первая строка содержит сигнатуру)
                        return {"type": "warning"}

                    # Чтение данных
                    data = [] # создаем пустой список с данными
                    for line in file: # читаем строки файла
                        record = line.strip().split("|") # удаляем пробелы строки и делим строку по символу |
                        if len(record) == len(headers): # если количество параметров в строке совпадает с заголовкаи (корректная строка)
                            data.append(record) # добавляем строку в список

                    # Создаем вкладку с этим файлом
                    file_tab = FileTab( # вызываем класс описаный в view.py
                        file_name=file_name, # название вкладки = название файла
                        headers=headers, # заголовки
                        data=data, # данные таблицы
                        parent=self, # для вызова родительского класса parent
                    )
                    
                    return {"type": "success",
                            "file_tab": file_tab,
                            "file_name": file_name}

            except Exception as e: # обрабатываем любое исключение
                return {"type": "critical", 
                        "message": str(e)}
            
    def open_file_by_path(self, path, FileTab, headers):
            try: # конструкция try except обработка исключений
                with open(path, "r", encoding="utf-8") as file: # пробуем открыть файл
                    first_line = file.readline().strip() # читаем первую строку файла, убираем пробелы с двух сторон
                    if first_line != "###OBJECT_DB###": # Проверка на наш формат файла (первая строка содержит сигнатуру)
                        return {"type": "warning",
                                "title": "Invalid File",
                                "message": "The selected file is not a valid Object Database file."}

                    # Чтение данных 
                    data = [] # создаем пустой список с данными
                    for line in file: # читаем строки файла
                        record = line.strip().split("|") # удаляем пробелы строки и делим строку по символу |
                        if len(record) == len(headers): # если количество параметров в строке совпадает с заголовкаи (корректная строка)
                            data.append(record) # добавляем строку в список

                    # Создаем вкладку с этим файлом
                    file_tab = FileTab( # вызываем класс описаный в view.py
                        file_name=path, # название вкладки = название файла
                        headers=headers, # заголовки
                        data=data, # данные таблицы
                        parent=self, # для вызова родительского класса parent
                    )
                    return {"type": "success",
                            "file_tab": file_tab}
                    
            except Exception as e: # обрабатываем любое исключение
                return {"type": "critical", 
                        "title": "Error",
                        "message": "Failed to open file: %s" % str(e)}


    def new_file(self, FileTab, reply, headers): 
        if reply:  # Если пользователь выбрал "Yes"
            file_name = "new_file.txt"  # Название нового файла, который будет создан
            data = []  # Пустой список данных для нового файла (таблицы)

            # Создание новой вкладки с пустыми данными
            new_tab = FileTab(
                file_name=file_name,  # Название файла, которое будет отображаться в новой вкладке
                headers=headers,  # Заголовки для таблицы
                data=data,  # Пустые данные для таблицы
                parent=self  # Родительский объект, в данном случае главное окно
            )

            return {"type": "success",
                    "new_tab": new_tab,
                    "file_name": file_name}

    def save_file(self, current_tab):
        if current_tab and hasattr(current_tab, "file_name"):  # Проверяем, что у текущей вкладки есть атрибут file_name
            try:
                # Открываем файл для записи (перезаписываем файл, если он уже существует)
                with open(current_tab.file_name, "w", encoding="utf-8") as file:
                    file.write("###OBJECT_DB###\n")  # Записываем сигнатуру в файл (определяет формат файла)
                    
                    # Записываем данные в файл (по строкам)
                    for record in current_tab.data:  # Перебираем все записи в данных вкладки
                        file.write("|".join(record) + "\n")  # Каждую запись записываем через | и переходим на новую строку

                return {"type": "success",
                        "message": "File saved: %s" % str(current_tab.file_name)}
                
            except Exception as e:  # Если возникла ошибка при сохранении
                return {"type": "critical",
                        "title": "Error", 
                        "message": str(e)}


    def save_file_as(self, file_name):
        return {"type": "success"}

    def on_header_clicked(self, column_index):


        try:
            # Определяем функцию сортировки для данных
            def sort_key(record):
                value = record[column_index]  # Получаем значение в указанном столбце
                try:
                    # Пробуем преобразовать значение в число
                    return float(value.replace(",", "").replace(" ", ""))
                except:
                    try:
                        # Пробуем преобразовать значение в дату (формат: YYYY-MM-DD)
                        return datetime.strptime(value, "%Y-%m-%d")
                    except:
                        # Если не число и не дата, возвращаем строку в нижнем регистре для сортировки
                        return value.lower()

            # Сортируем данные, меняем порядок сортировки на противоположный
            return {"type": "success",
                    "sort_key": sort_key
                    }
        
        except Exception as e:
            return {"type": "warning",
                    "title": "Sort Error",
                    "message": "Could not sort: " + str(e)}
           
    def delete_record(self, data, row):
        try:
            del data[row]
            return {"type": "status_bar", 
                    "message": "Record deleted", 
                    "data": data}
        
        except IndexError:
            return {"type": "warning",
                    "title": "Delete Error",
                    "message": "Invalid row selected."}
            
    def submit_form(self, record, action, data, current_row):
        # Считываем значения всех полей формы и убираем пробелы по краям
        
        # Проверка, все ли поля заполнены
        if not all(record):
            return {"type": "warning",
                    "title": "Validation Error",
                    "message": "All fields are required."}
        
        # Получаем значение даты 
        date_start = record[2]
        date_end = record[3]
        try:
            # Преобразуем строку в дату
            date_start = datetime.strptime(date_start, "%Y-%m-%d")
            date_end = datetime.strptime(date_end, "%Y-%m-%d")

            if date_start > date_end:
                raise ValueError("The start date must be less than the completion date of construction")
            

        except ValueError as e:
            return {"type": "warning",
                    "title": "Date Error",
                    "message": str(e)}

        # В зависимости от действия (добавление или редактирование)
        if action == "add":
            new_id = str(len(data) + 1)  # Создаем новый ID
            data.append([new_id] + record)  # Добавляем запись с ID
            return {"type": "status_bar",
                    "message": "Record added",
                    "data": data}
        
            
        elif action == "edit":
            data[current_row][1:] = record  # Обновляем данные записи, кроме ID
            return {"type": "status_bar",
                    "message": "Record updated",
                    "data": data}
