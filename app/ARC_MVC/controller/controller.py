import os
from app.ARC_MVC.model.model import Model  # Импортируем модель, в которой реализована логика обработки данных


class Controller:
    """
    Класс Controller — посредник между пользовательским интерфейсом (View) и логикой приложения (Model).
    Каждый метод вызывает соответствующую функцию модели, реализуя шаблон проектирования MVC (Model-View-Controller).
    """

    def open_file(self, FileTab, filename, headers):
        """
        Открытие файла базы данных сотрудников. \n
        :param FileTab: Класс вкладки, в которой отображаются данные. \n
        :param filename: Имя файла который необходимо открыть \n
        :param headers: Заголовки таблицы \n
        """
        
        response = Model.open_file(self, FileTab, filename, headers) # Вызываем метод open_file класса Model

        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции # проверка на корректный ответ от метода
            return # выход из функции
        
        if response["type"] == "warning": # проверка на предупреждение 
            FileTab.show_warning( # вывод предупреждения что файл не корректный
                            self, # экземпляр класса
                            self.tr("Invalid File"), # тайтл окна
                            self.tr("The selected file is not a valid Object Database file."), # сообщение
                        )
        
        elif response["type"] == "critical": # проверка на ошибку
            FileTab.show_critical( # вызываем ошибку
                    self, # экземпляр класса
                    self.tr("Error"), # Тайтл окна
                    self.tr("Failed to open file: %s") % response["message"] # текст ошибки
                )

        elif response["type"] == "success": # проверка на корректное отрабатывание функции # проверка на корректное открытие файла
            file_tab, file_name = response["file_tab"], response["file_name"]
            self.tabs.addTab(file_tab, os.path.basename(file_name)) # добавляем вкладку ко всем вкладкам
            self.retranslate_ui() # переводим вкладки
            self.show_status(self.tr("File loaded: %s") % file_name) # Показываем статус
        
        

    def new_file(self, FileTab):
        """
        Создание нового пустого файла базы данных. \n
        :param FileTab: Класс вкладки для отображения нового файла.
        """
        reply = FileTab.show_question( # вызов вопроса
            self,  # Это ссылка на текущий объект, чтобы показывать диалоговое окно на главном окне
            self.tr("New file"),  # Заголовок окна (перевод)
            self.tr("Create a new empty database? Any unsaved changes will be lost."),  # Текст вопроса (перевод)
        )
        
        
        if reply == "no": # если пользователь выбрал нет выходим из функции
            return

        response = Model.new_file(self, FileTab, reply, self.headers) # вызываем метод new_file класса Model
        
        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции# проверка на корректный ответ от метода
            return # выход из функции

        if response["type"] == "success": # проверка на корректное отрабатывание функции # проверка на корректное отрабатывание функции
            self.tabs.addTab(response["new_tab"], os.path.basename(response["file_name"]))  # Добавление новой вкладки в контейнер вкладок
            self.retranslate_ui()  # Перевод интерфейса, если нужно
            self.status_bar.showMessage(self.tr("New empty database created"))  # Отображение сообщения в статусной строке



    def save_file(self, FileTab):
        """
        Сохраняет текущий открытый файл. \n
        :param FileTab: Класс вкладки в котором реализована функция show_critical для показа ошибки
        """
        
        current_tab = self.tabs.currentWidget() # Получаем текущую вкладку из контейнера вкладок
        
        response =  Model.save_file(self, current_tab) # вызываем метод save_file клсса Model
        
        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции 
        
        if response["type"] == "success": # проверка на корректное отрабатывание функции 
            self.show_status(self.tr("File saved: %s") % current_tab.file_name) # вывод статуса
                
        elif response["type"] == "critical": # проверка на ошибку
            FileTab.show_critical(self, response["title"], response["message"]) # вывод ошибки

    def save_file_as(self, file_name):
        """
        Сохраняет текущий файл под новым именем (Save As). \n
        :param file_name: Название файла (передается сразу путь до файла) который указал пользователь в всплывшем окне диалога
        """

        response = Model.save_file_as(self, file_name) # вызов метода save_file_as класса Model
        
        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции 
        
        if not response["type"] == "success": # проверка на корректную работу функции
            return # выход из функции
        
        if file_name:  # Если пользователь выбрал файл для сохранения
            if not file_name.lower().endswith(".txt"):  # Проверяем, чтобы файл заканчивался на .txt, если нет — добавляем это расширение
                file_name += ".txt"

            # Устанавливаем новый файл для текущей вкладки
            current_tab = self.tabs.currentWidget()  # Получаем текущую вкладку
            current_tab.file_name = file_name  # Присваиваем выбранное имя файлу текущей вкладки
            
            
            if self.save_file():  # Сохраняем файл с новым именем
                return True
            
    def on_header_clicked(self, column_index):
        """
        Обработка клика по заголовку столбца — сортировка данных. \n
        :param column_index: Индекс столбца, по которому нужно отсортировать.
        """
                
        response = Model.on_header_clicked(self, column_index)  # Обрабатывает сортировку по столбцу

        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции

        if response["type"] == "warning": # проверка на предупреждение
            self.show_warning(response["title"], response["message"]) # вывод предупреждения
            return
        
        elif response["type"] == "success": # проверка на корректное отрабатывание функции            
            self.data.sort(key=response["sort_key"], reverse=not self.sort_order_asc)
            self.sort_order_asc = not self.sort_order_asc  # Меняем флаг порядка сортировки
            self.load_data_to_table()  # Перезагружаем данные в таблицу

    def add_record(self):
        """
        Подготовка интерфейса к добавлению новой записи.
        """        
        # Устанавливаем текущую операцию как "добавление"
        self.current_action = "add"
        # Очищаем форму
        self.clear_form()
        # Показываем форму и кнопки видимыми
        self.form_widget.setVisible(True)
        self.form_buttons_widget.setVisible(True)

    def edit_record(self):
        """
        Подготовка интерфейса к редактированию выбранной записи.
        """
        
        # Получаем выбранные строки в таблице
        selected = self.table.selectionModel().selectedRows()
        
        # Если ничего не выбрано, выводим предупреждение
        if not selected:
            self.show_warning("No Selection", "Please select a record to edit.")
            return

        # Сохраняем индекс выбранной строки для редактирования
        self.current_row = selected[0].row()
        self.current_action = "edit"  # Устанавливаем операцию как "редактирование"

        # Получаем данные для редактирования (без ID)
        record = self.data[self.current_row][1:]
        
        # Заполняем поля формы данными выбранной записи
        for i, field in enumerate(self.form_fields):
            field.setText(record[i])

        # Делаем форму и кнопки видимыми
        self.form_widget.setVisible(True)
        self.form_buttons_widget.setVisible(True)


    
    def delete_record(self):
        """
        Удаляет выбранную запись из таблицы и данных.
        """
        
        selected = self.table.selectionModel().selectedRows() # получаем выбранные строчки

        if not selected: # если строчки не выбраны выводим предупреждение
            self.show_warning("No Selection", "Please select a record to delete.")
            return

        confirm = self.show_question("Confirm Delete", "Delete this record?") # выводим вопрос удалить ли строку
        if confirm == "no": # пользователь ответил нет входим из функции
            return 
        
        # Получаем индекс первой выбранной строки
        row = selected[0].row()
        response = Model.delete_record(self, self.data, row)  # Обрабатывает удаление

        
        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции

        # Если пользователь подтвердил удаление
        if response["type"] == "status_bar": # корректно отработала функция
            self.data = response["data"] # обновляем дату
            self.load_data_to_table() # обновление данных
            self.show_status(response["message"]) # вывод статуса
         
        elif response["type"] == "warning": # проверка на предупреждение 
            self.show_warning(response["title"], response["message"]) # вывод предупреждения
            return
 
        
        
        

    def submit_form(self):
        """
        Подтверждает добавление или редактирование записи, сохраняет данные в модель.
        """
        record = [field.text() for field in self.form_fields] # забираем текст из форм
        response = Model.submit_form(self, record, self.current_action, self.data, self.current_row) # вызов метода submit_form класса Model
        

        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции 
        
        if response["type"] == "warning": # проверка на предупреждение 
            self.show_warning(response["title"], response["message"])
        

        elif response["type"] == "status_bar": # корректно отработала функция
            self.data = response["data"] # обновление данных
            self.load_data_to_table() # обновление данных в таблице
            self.cancel_form() # закрываем форму
            self.show_status(response["message"]) # показываем статус


    def cancel_form(self):
        """
        Отменяет текущее редактирование или добавление записи, скрывает форму.
        """
        # Скрываем виджеты формы и кнопок
        self.form_widget.setVisible(False)
        self.form_buttons_widget.setVisible(False)


    def clear_form(self):
        """
        Очищает все поля формы.
        """
        # Очищаем все поля формы (устанавливаем пустое значение)
        for field in self.form_fields:
            field.clear()

    def search_in_column(self):
        """
        Выполняет поиск по выбранному столбцу таблицы.
        """
        
        # Получаем текст из поля поиска и приводим к нижнему регистру
        text = self.search_input.text().strip().lower()

        # Получаем индекс выбранного столбца для поиска
        col_index = self.column_selector.currentIndex()

        # Перебираем все строки таблицы
        for row in range(self.table.rowCount()):
            item = self.table.item(row, col_index)  # Получаем ячейку в нужной колонке

            # Если текст не найден — скрываем строку
            self.table.setRowHidden(
                row, # выбираем строку которую нужно скрыть
                text not in item.text().lower() if item else True # если введеного текста нет в строке то True если строка пустая то True
            )



    def open_file_by_path(self, path, FileTab):
        """
        Открывает файл при переносе на таблицу \n
        :param path: путь до файла \n
        :param FileTab: Класс вкладки где открыть файл \n
        """
        response = Model.open_file_by_path(self, path, FileTab, self.headers) # вызов метода open_file_by_path класса Model

        if not isinstance(response, dict):# проверка на корректный ответ от метода
            return # выход из функции

        if response["type"] == "warning": # проверка на предупреждение
            FileTab.show_warning(self, response["title"], response["message"])
        
        elif response["type"] == "critical": # проверка на ошибку
            FileTab.show_critical(self, response["title"], response["message"])

        elif response["type"] == "success": # проверка на корректное отрабатывание функции
            self.tabs.addTab(response["file_tab"], os.path.basename(path)) # добавляем вкладку ко всем вкладкам
            self.retranslate_ui() # переводим вкладки
            self.show_status("File loaded: %s" % path) # Показываем стату

        
