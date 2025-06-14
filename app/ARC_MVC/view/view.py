
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import (QCoreApplication, QMimeData, QSettings, Qt,
                          QTranslator)
from PyQt6.QtGui import QAction, QDrag, QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                             QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMainWindow, QMenu, QMenuBar, QMessageBox,
                             QPushButton, QTableWidget, QTabWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget, QFileDialog)

from app.ARC_MVC.controller.controller import Controller
from app.ARC_MVC.model.model import Validators
from datetime import datetime
from collections import Counter, defaultdict
import numpy as np

class DraggableTableWidget(QTableWidget):
    """Переопределённый виджет таблицы, поддерживающий drag-and-drop и контекстное меню."""

    def __init__(self, parent=None):
        super().__init__(parent)  # Инициализация родительского класса QTableWidget

        # Устанавливает поведение выделения — по строкам (вся строка при клике)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Разрешает только перетаскивание (без сброса)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

        # Включает возможность перетаскивания
        self.setDragEnabled(True)

        # Устанавливает пользовательскую политику контекстного меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Подключает сигнал запроса контекстного меню к обработчику
        self.customContextMenuRequested.connect(self.context_menu_event)

        # Переменная для хранения позиции начала drag-события
        self.start_pos = None

    def context_menu_event(self, pos):
        """Обрабатывает контекстное меню при правом клике по ячейке."""
        item = self.itemAt(pos)  # Получает элемент таблицы по позиции курсора
        if not item:
            return  # Если клик вне содержимого — ничего не делать

        context_menu = QMenu(self)  # Создаёт контекстное меню

        # Создаёт действия для меню: добавить, редактировать, удалить
        add_action = QAction(self.parent().tr("Добавить запись"), self)
        edit_action = QAction(self.parent().tr("Редактировать запись"), self)
        delete_action = QAction(self.parent().tr("Удалить запись"), self)

        # Получает главное окно (для вызова методов редактирования)
        main_window = self.window()

        # Подключает действия к методам главного окна
        add_action.triggered.connect(lambda: main_window.add_record())
        edit_action.triggered.connect(lambda: main_window.edit_record())
        delete_action.triggered.connect(lambda: main_window.delete_record())

        # Добавляет действия в контекстное меню
        context_menu.addAction(add_action)
        context_menu.addAction(edit_action)
        context_menu.addAction(delete_action)

        # Показывает меню в глобальной позиции курсора
        context_menu.exec(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        """Обрабатывает событие нажатия кнопки мыши."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()  # Запоминает начальную позицию для drag
        super().mousePressEvent(event)  # Вызывает стандартную реализацию

    def mouseMoveEvent(self, event):
        """Обрабатывает перемещение мыши для запуска drag-события."""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return  # Игнорирует, если левая кнопка не нажата

        if self.start_pos is None:
            return  # Если начальная позиция не установлена — выход

        # Вычисляет дистанцию между текущей и стартовой позицией
        distance = (event.pos() - self.start_pos).manhattanLength()
        if distance < QApplication.startDragDistance():
            return  # Если движение слишком короткое — не начинать drag

        self.perform_drag()  # Запускает процесс перетаскивания

    def perform_drag(self):
        """Формирует и запускает drag-событие с текстовыми данными выбранных строк."""
        selected_ranges = self.selectedRanges()  # Получает диапазоны выделенных строк
        if not selected_ranges:
            return  # Если ничего не выделено — выход

        row_texts = []  # Список для хранения текстов по строкам
        for rng in selected_ranges:
            for row in range(rng.topRow(), rng.bottomRow() + 1):
                record = []
                for col in range(self.columnCount()):
                    item = self.item(row, col)  # Получает элемент таблицы
                    record.append(item.text() if item else "")  # Добавляет текст или пустую строку
                row_texts.append(" | ".join(record))  # Объединяет значения в строку

        if not row_texts:
            return  # Если строки пустые — не продолжаем

        text = "\n".join(row_texts)  # Формирует итоговый текст для передачи

        mime_data = QMimeData()  # Создаёт объект MIME-данных
        mime_data.setText(text)  # Устанавливает текст в MIME-объект

        drag = QDrag(self)  # Создаёт drag-объект
        drag.setMimeData(mime_data)  # Прикрепляет данные
        drag.exec(Qt.DropAction.CopyAction)  # Запускает drag с действием "копировать"


class ChartsWindow(QMainWindow):
    """Окно для отображения графиков на основе данных сотрудников."""

    def __init__(self, parent=None, data=None, headers=None):
        super().__init__(parent)  # Инициализация базового QMainWindow
        self.data = data  # Список данных сотрудников (строки таблицы)
        self.headers = headers  # Заголовки столбцов (может быть None)
        self.setWindowTitle(self.tr("Charts"))  # Устанавливает заголовок окна

        # Основной контейнер с вкладками
        self.tabs = QTabWidget(self)  # Создаёт таб-виджет для переключения между графиками
        self.setCentralWidget(self.tabs)  # Делает его центральным виджетом окна

        # Добавляет вкладку с графиком "начало проектов"
        self.add_graph_tab(
            self.tr("График по проектам"), 
            self.plot_start_projects()
        )


    def add_graph_tab(self, tab_name, canvas):
        """Добавляет вкладку с указанным названием и графиком (canvas)."""
        tab = QWidget()  # Создаёт новый виджет для вкладки
        layout = QVBoxLayout()  # Задаёт вертикальное расположение элементов
        layout.addWidget(canvas)  # Добавляет на вкладку холст с графиком
        tab.setLayout(layout)  # Устанавливает компоновку
        self.tabs.addTab(tab, tab_name)  # Добавляет вкладку в QTabWidget


    """
    CREATE CHART BY DATE AND STATUS IN CLOSE TIME
    """

    def plot_start_projects(self):
        """Строит график: количество проектов в каждом статусе по годам."""

        # Годы, которые будем анализировать
        all_years = sorted(set([int(record[3].split('-')[0]) for record in self.data]))

        # status_years[год][статус] = количество проектов
        status_years = {year: {"планируется": 0, "в процессе": 0, "завершён": 0} for year in all_years}

        for record in self.data:
            try:
                year = int(record[3].split('-')[0])
                status = record[5].strip().lower()
                status_years[year][status] += 1

            except Exception:
                continue

        # Подготовка данных
        statuses = ["планируется", "в процессе", "завершён"]
        years = all_years
        x = np.arange(len(years))
        width = 0.25

        counts_by_status = {
            status: [status_years[year][status] for year in years]
            for status in statuses
        }

        colors = {
            "планируется": "#FFA500",  # оранжевый
            "в процессе": "#1f77b4",   # синий
            "завершён": "#2ca02c",     # зелёный
        }

        fig, ax = plt.subplots(figsize=(10, 6))

        for i, status in enumerate(statuses):
            ax.bar(x + i * width, counts_by_status[status], width,
                label=self.tr(status.capitalize()), color=colors[status])

        ax.set_xlabel(self.tr("Года"))
        ax.set_ylabel(self.tr("Количество проектов"))
        ax.set_title(self.tr("Количество проектов по статусам в каждый год"))
        ax.set_xticks(x + width)
        ax.set_xticklabels(years, rotation=45)
        ax.legend()

        canvas = FigureCanvas(fig)
        canvas.draw()
        return canvas




class FileTab(QWidget):
    """Вкладка, содержащая таблицу сотрудников и интерфейс для управления записями.
    
    Позволяет добавлять, редактировать, удалять, искать записи, а также использовать валидацию.
    """

    def __init__(self, headers, data, file_name=None, parent=None):
        super().__init__(parent)  # Инициализация базового QWidget

        # --- Хранение параметров ---
        self.file_name = file_name  # Имя файла, с которым работает вкладка
        self.headers = headers  # Заголовки таблицы (столбцы)
        self.data = data if data is not None else list()  # Данные таблицы
        self.parent = parent  # Ссылка на родительское окно (например, EmployeeDBApp)

        # --- Внутренние состояния ---
        self.current_action = None  # Текущее действие (add/edit)
        self.current_row = None  # Индекс редактируемой строки
        self.sort_order_asc = True  # Порядок сортировки (по возрастанию/убыванию)

        # --- Главный layout ---
        self.layout = QVBoxLayout(self)

        # --- Таблица ---
        self.table = DraggableTableWidget()  # Таблица с поддержкой drag-and-drop
        self.table.setColumnCount(len(headers))  # Устанавливает количество столбцов
        self.table.setHorizontalHeaderLabels(headers)  # Устанавливает заголовки
        self.table.setRowCount(len(data) if data is not None else 0)  # Устанавливает количество строк

        # === Панель кнопок ===
        btn_layout = QHBoxLayout()  # Layout для кнопок управления
        self.add_btn = QPushButton(self.tr("Add Record"))  # Кнопка добавления
        self.edit_btn = QPushButton(self.tr("Edit Record"))  # Кнопка редактирования
        self.delete_btn = QPushButton(self.tr("Delete Record"))  # Кнопка удаления

        for btn in [self.add_btn, self.edit_btn, self.delete_btn]:
            btn.setFixedWidth(160)  # Устанавливает фиксированную ширину кнопок

        # Добавление кнопок на layout
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)

        # === Поиск ===
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()  # Поле ввода для поиска
        self.search_input.setPlaceholderText(self.tr("Enter text to search..."))  # Подсказка

        self.column_selector = QComboBox()  # Селектор колонок
        self.column_selector.addItems(headers)  # Заполнение колонками

        self.search_btn = QPushButton(self.tr("Search in Column"))  # Кнопка поиска

        # Добавление элементов поиска на layout
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.column_selector)
        search_layout.addWidget(self.search_btn)
        self.layout.addLayout(search_layout)

        # === Настройки таблицы ===
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.layout.addWidget(self.table)

        # === Форма для редактирования/добавления записи ===
        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout(self.form_widget)
        self.form_fields = []

        # Создание поля ввода для каждого столбца (кроме ID)
        for header in headers[1:]:
            row_layout = QHBoxLayout()
            label = QLabel(self.tr(header) + ":")  # Метка для поля
            field = QLineEdit()  # Поле ввода
            row_layout.addWidget(label)
            row_layout.addWidget(field)
            self.form_layout.addLayout(row_layout)
            self.form_fields.append(field)  # Сохраняем для доступа

        # Установка валидаторов для нужных полей
        self.form_fields[1].setValidator(Validators.name_validator())   # Название объекта
        self.form_fields[2].setValidator(Validators.name_validator())   # адрес
        self.form_fields[2].setValidator(Validators.date_validator())    # Дата начала
        self.form_fields[3].setValidator(Validators.date_validator())      # Дата окончания
        self.form_fields[4].setValidator(Validators.status_validator())     # Статус
        self.form_fields[5].setValidator(Validators.type_validator())      # Тип
        self.form_fields[6].setValidator(Validators.area_validator())      # Площадь
        self.form_fields[7].setValidator(Validators.floors_validator())     # этажность

        # === Кнопки формы ===
        self.form_buttons_widget = QWidget()
        form_btn_layout = QHBoxLayout(self.form_buttons_widget)
        self.submit_btn = QPushButton(self.tr("Submit"))  # Подтвердить
        self.cancel_btn = QPushButton(self.tr("Cancel"))  # Отмена
        form_btn_layout.addWidget(self.submit_btn)
        form_btn_layout.addWidget(self.cancel_btn)

        # Добавление формы на главный layout
        self.layout.addWidget(self.form_widget)
        self.layout.addWidget(self.form_buttons_widget)

        # По умолчанию форма и кнопки скрыты
        self.form_widget.setVisible(False)
        self.form_buttons_widget.setVisible(False)

        # === Подключение сигналов к методам ===
        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)
        self.search_btn.clicked.connect(self.search_in_column)
        self.submit_btn.clicked.connect(self.submit_form)
        self.cancel_btn.clicked.connect(self.cancel_form)

        # === Загрузка данных ===
        self.load_data_to_table()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        
    def load_data_to_table(self):
        # Проверка, если данные отсутствуют
        if self.data is None:
            return  # Если данных нет, выходим из метода

        # Устанавливаем количество строк в таблице согласно количеству записей в данных
        self.table.setRowCount(len(self.data))

        # Перебираем все строки данных и добавляем их в таблицу
        for row_idx, record in enumerate(self.data):  # Для каждой строки данных
            for col_idx, value in enumerate(record):  # Для каждого значения в строке
                # Создаем новый элемент для ячейки таблицы с данным значением
                item = QTableWidgetItem(value)
                
                # Убираем возможность редактирования ячейки
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Устанавливаем созданный элемент в соответствующую ячейку таблицы
                self.table.setItem(row_idx, col_idx, item)

    def on_header_clicked(self, column_index):
        Controller.on_header_clicked(self, column_index) # обрабатываем клик на колонки

    def add_record(self):
        Controller.add_record(self)  # Обрабатывает добавление записи

    def edit_record(self):
        Controller.edit_record(self)  # Обрабатывает редактирование

    def delete_record(self):
        Controller.delete_record(self) # обрабатывает удаление

    def submit_form(self):
        Controller.submit_form(self)  # Подтверждение формы

    def cancel_form(self):
        Controller.cancel_form(self)  # Отмена редактирования

    def clear_form(self):
        Controller.clear_form(self)  # Очистка полей формы

    def search_in_column(self):
        Controller.search_in_column(self)  # Поиск в выбранной колонке

    def show_warning(self, title, message):
        QMessageBox.warning(self, self.tr(title), self.tr(message)) # вывод предупреждения
    
    def show_critical(self, title, message):
        QMessageBox.critical(self, self.tr(title), self.tr(message)) # вывод ошибки

    def show_status(self, message):
        self.parent.status_bar.showMessage(self.tr(message)) # вывод статус бара
    
    def show_question(self, title, question):
        reply = QMessageBox.question(self, title, question,  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) # вывод вопроса

        # обработка ответа
        if reply == QMessageBox.StandardButton.Yes:
            return "yes"
        return "no"


class ObjectDBApp(QMainWindow):
    def __init__(self):
        super().__init__()  # Вызываем конструктор родительского класса QMainWindow

        self.settings = QSettings("MyCompany", "ObjectDBApp")  # Инициализируем объект для работы с настройками приложения

        # Инициализация переменных для меню
        self.file_menu = None
        self.lang_menu = None
        self.help_menu = None

        self.lang_code = self.settings.value("language", "en") # Код языка приложения

        # Основные переменные
        self.current_file = None  # Текущий открытый файл
        self.data = []  # Данные сотрудников
        # Заголовки столбцов в таблице
        self.headers = [
            self.tr("ID"),  # Идентификатор
            self.tr("Name object"),  # Название объекта
            self.tr("Address"),  # Адрес
            self.tr("Date start building"),  # Дата начала строительства
            self.tr("Date end building"),  # Дата окончания строительства
            self.tr("Status"),  # Статус
            self.tr("Type object"),  # Тип объекта (жилой / коммерческий / промышленный)
            self.tr("Area"),  # Площадь
            self.tr("Floors"),  # Этажи
        ]
        
        
        
        # Устанавливаем язык интерфейса, если он сохранен в настройках
        self.set_language(self.lang_code)
        # Инициализация интерфейса
        self.init_ui()
        # Загрузка настроек из QSettings (например, положение окна, язык)
        self.load_settings()

    def init_ui(self):
        # Устанавливаем заголовок окна приложения
        self.setWindowTitle(self.tr("Employee Database Manager"))
        # Устанавливаем начальные размеры окна
        self.setGeometry(100, 100, 1000, 600)
        # Устанавливаем минимальный размер окна
        self.setMinimumSize(800, 600)

        # Создаем меню
        self.create_menu_bar()

        # Создаем вкладки
        self.tabs = QTabWidget()  # Инициализируем виджет для вкладок
        self.tabs.setTabsClosable(True)  # Включаем возможность закрывать вкладки
        self.tabs.tabCloseRequested.connect(self.close_tab)  # Подключаем слот для закрытия вкладок
        self.setCentralWidget(self.tabs)  # Устанавливаем вкладки как центральный виджет

        # Кнопка для добавления новой вкладки
        self.add_tab_btn = QPushButton("+")
        self.add_tab_btn.setStyleSheet(
            """
        QPushButton {
            border: none;  
            font-size: 16px;  
            font-weight: bold;  
        }
        QPushButton:hover {
            background: #e0e0e0;  
        }
        """
        ) # border убирает рамку font-size размер шрифта font-weight жирный шрифт background меняем фон кнопки при наведении

        # Размещаем кнопку в верхнем правом углу вкладок
        self.tabs.setCornerWidget(self.add_tab_btn, Qt.Corner.TopRightCorner)
        # При нажатии на кнопку добавляем новую вкладку
        self.add_tab_btn.clicked.connect(self.create_new_tab)

        # Создаем первую вкладку
        self.create_new_tab()

        # Строка состояния
        self.status_bar = self.statusBar()

    def create_new_tab(self):
        """
        Создает новую вкладку с таблицей для ввода данных сотрудников.
        """
        # Создаем новый экземпляр вкладки для работы с файлами, передаем ей заголовки и данные
        file_tab = FileTab(headers=self.headers, data=None, parent=self)
        # Добавляем новую вкладку в виджет вкладок
        self.tabs.addTab(file_tab, self.tr("Новая вкладка"))
        # Разрешаем закрытие вкладки
        self.tabs.setTabsClosable(True)

        # Получаем таблицу из созданной вкладки
        self.table = file_tab.table

        # Переводим интерфейс на текущий язык
        self.retranslate_ui()

    def load_settings(self):
        """Загрузка настроек интерфейса из QSettings"""
        
        # Загружаем положение окна
        geometry = self.settings.value("geometry")  # Получаем сохранённое положение окна
        if geometry:
            self.restoreGeometry(geometry)  # Восстанавливаем положение окна, если оно было сохранено

        # Загружаем язык
        self.lang_code = self.settings.value("language", "en")  # Получаем язык из настроек (по умолчанию "en")
        self.set_language(self.lang_code)  # Устанавливаем язык интерфейса

        # Загружаем размеры столбцов
        if self.table.columnCount():  # Проверяем, что таблица имеет столбцы
            for col in range(self.table.columnCount()):  # Для каждого столбца
                width = self.settings.value(f"column_width_{col}", 100)  # Получаем ширину столбца (по умолчанию 100)
                self.table.setColumnWidth(col, int(width))  # Устанавливаем ширину столбца


    def save_settings(self):
        """Сохраняем настройки интерфейса в QSettings"""
        
        # Сохраняем положение окна
        self.settings.setValue("geometry", self.saveGeometry())  # Сохраняем текущее положение окна

        # Сохраняем язык
        self.settings.setValue("language", self.lang_code)  # Сохраняем текущий язык

        # Сохраняем размеры столбцов
        for col in range(self.table.columnCount()):  # Для каждого столбца
            self.settings.setValue(f"column_width_{col}", self.table.columnWidth(col))  # Сохраняем ширину столбца


    def create_menu_bar(self):
        menu_bar = QMenuBar(self)  # Создаем строку меню

        # Меню "Файл"
        self.file_menu = QMenu(self.tr("&File"), self)  # Создаем меню "Файл" с переводом

        self.new_action = self.file_menu.addAction(self.tr("&New file"))  # Добавляем пункт "Новый файл"
        self.new_action.triggered.connect(self.new_file)  # При нажатии вызываем метод new_file

        self.open_action = self.file_menu.addAction(self.tr("&Open..."))  # Добавляем пункт "Открыть"
        self.open_action.triggered.connect(self.open_file)  # При нажатии вызываем метод open_file

        self.save_action = self.file_menu.addAction(self.tr("&Save"))  # Добавляем пункт "Сохранить"
        self.save_action.triggered.connect(self.save_file)  # При нажатии вызываем метод save_file

        self.save_as_action = self.file_menu.addAction(self.tr("Save &As..."))  # Добавляем пункт "Сохранить как"
        self.save_as_action.triggered.connect(self.save_file_as)  # При нажатии вызываем метод save_file_as

        self.print_action = self.file_menu.addAction(self.tr("Print"))  # Добавляем пункт "Печать"
        self.print_action.triggered.connect(self.print_table)  # При нажатии вызываем метод print_table

        self.file_menu.addSeparator()  # Добавляем разделитель в меню

        self.exit_action = self.file_menu.addAction(self.tr("E&xit"))  # Добавляем пункт "Выход"
        self.exit_action.triggered.connect(self.close)  # При нажатии закрываем приложение

        # Меню "График"
        self.chart_menu = QMenu(self.tr("&Chart"), self)  # Создаем меню "График"
        self.chart = self.chart_menu.addAction(self.tr("&Charts"))  # Добавляем пункт "Графики"
        self.chart.triggered.connect(self.open_charts_window)  # При нажатии открываем окно с графиками

        # Меню "Справка"
        self.help_menu = QMenu(self.tr("&Help"), self)  # Создаем меню "Справка"
        self.about_action = self.help_menu.addAction(self.tr("&About"))  # Добавляем пункт "О программе"
        self.about_action.triggered.connect(self.show_about)  # При нажатии показываем информацию о программе

        # Меню "Язык"
        self.lang_menu = QMenu(self.tr("&Language"), self)  # Создаем меню "Язык"

        self.english_action = self.lang_menu.addAction("English")  # Добавляем пункт "English"
        self.english_action.triggered.connect(lambda: self.set_language("en"))  # При нажатии меняем язык на английский

        self.russian_action = self.lang_menu.addAction("Русский")  # Добавляем пункт "Русский"
        self.russian_action.triggered.connect(lambda: self.set_language("ru"))  # При нажатии меняем язык на русский

        self.franch_action = self.lang_menu.addAction("Française")
        self.franch_action.triggered.connect(lambda: self.set_language("fr"))

        # Добавляем все меню в строку меню
        menu_bar.addMenu(self.file_menu)
        menu_bar.addMenu(self.help_menu)
        menu_bar.addMenu(self.lang_menu)
        menu_bar.addMenu(self.chart_menu)

        # Устанавливаем строку меню в главное окно приложения
        self.setMenuBar(menu_bar)

    def new_file(self):
        # Вызов метода из Controller для создания нового файла, передаем текущий объект и FileTab
        Controller.new_file(self, FileTab)


    def open_file(self):
        # Вызов метода из Controller для открытия файла, передаем текущий объект и FileTab
        file_name, _filter = QFileDialog.getOpenFileName( # Выводим диалог с выбором файла
            self, # экземпляр класса
            self.tr("Open Employee Database"), # Тайтл окна
            "", # текущая директория
            self.tr("Text Files (*.txt);;All Files (*)"), # указываем что изначально ищем .txt файлы
        )

        Controller.open_file(self, FileTab, file_name, self.headers)



    def save_file(self):
        # Вызов метода из Controller для сохранения текущего файла
        Controller.save_file(self, FileTab)
            

    def save_file_as(self):
        # Вызов метода из Controller для сохранения файла с новым именем
        file_name, _filter = QFileDialog.getSaveFileName( # вызываем окно для пути сохранения
            self,  # Это ссылка на текущее окно
            self.tr("Save Object Database"),  # Заголовок окна (перевод)
            "",  # Начальная директория (пусто, значит по умолчанию открывается последний путь)
            self.tr("Text Files (*.txt);;All Files (*)"),  # Фильтр для выбора файлов (только .txt или все файлы)
        )

        
        Controller.save_file_as(self, file_name)

        
        self.show_status(self.tr("File saved as: ") + file_name)  # Отображаем сообщение о сохранении файла

    def print_table(self):
        # Получаем текущую виджет-вкладку
        current_widget = self.tabs.currentWidget()

        # Проверяем, что текущий виджет - это вкладка типа FileTab
        if not isinstance(current_widget, FileTab):
            QMessageBox.warning(
                self, self.tr("Предупреждение"), self.tr("Ваша вкладка пустая")
            )  # Если вкладка не типа FileTab, выводим предупреждение
            return

        # Проверяем, что в данных вкладки есть информация
        if not current_widget.data:
            QMessageBox.warning(
                self, self.tr("Предупреждение"), self.tr("Нет данных для печати")
            )  # Если данных нет, выводим предупреждение
            return

        # Создаем документ для печати
        document = QTextDocument()

        # Формируем HTML код для таблицы
        html = (
            "<h3>"
            + self.tr("Object Database")
            + "</h3><table border='1' cellspacing='0' cellpadding='4'>"
        )

        # Добавляем заголовки таблицы
        html += "<tr>"
        for header in current_widget.headers:
            html += f"<th>{self.tr(header)}</th>"
        html += "</tr>"

        # Добавляем строки данных
        for record in current_widget.data:
            html += "<tr>"
            for field in record:
                html += f"<td>{field}</td>"  # Добавляем ячейки для каждого поля
            html += "</tr>"

        html += "</table>"  # Закрываем таблицу
        document.setHtml(html)  # Устанавливаем HTML-контент в документ

        # Создаем объект принтера и диалоговое окно для печати
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        # Если пользователь нажал "ОК" в диалоговом окне печати
        if dialog.exec():
            document.print(printer)  # Печатаем документ


    def open_charts_window(self):
        # Получаем текущую виджет-вкладку
        current_widget = self.tabs.currentWidget()

        # Проверяем, что в данных вкладки есть информация
        if not current_widget.data:
            QMessageBox.warning(
                self, self.tr("Предупреждение"), self.tr("Нет данных для графика")
            )  # Если данных нет, выводим предупреждение
            return

        # Если данные есть, создаем окно с графиками, передаем данные и заголовки
        self.charts_window = ChartsWindow(
            parent=self, data=current_widget.data, headers=current_widget.headers
        )
        self.charts_window.show()  # Показываем окно с графиками




    def contextMenuEvent(self, event):
        # Проверяем, что таблица включена
        if self.table.isEnabled():
            # Если таблица включена, вызываем метод для обработки контекстного меню
            self.context_menu_event(event)
        else:
            # Если таблица отключена, показываем предупреждение
            QMessageBox.warning(
                self, self.tr("Предупреждение!"), self.tr("Кликните по таблице")
            )


    def set_language(self, lang_code):
        """Устанавливает язык интерфейса"""
        # Устанавливаем код языка
        self.lang_code = lang_code

        # Создаем новый объект переводчика
        self.translator = QTranslator()
        
        # Если переводчик уже был установлен, удаляем его
        if hasattr(self, "tr"):
            QCoreApplication.removeTranslator(self.translator)

        # Загружаем новый перевод, используя код языка
        translation_loaded = self.translator.load(
            f"app/translations/translations_{lang_code}.qm"
        )

        # Если перевод успешно загружен, устанавливаем его
        if translation_loaded:
            QCoreApplication.installTranslator(self.translator)
            print(f"[INFO] Перевод загружен: translations_{lang_code}.qm")
        else:
            print(f"[WARNING] Перевод не найден: translations_{lang_code}.qm")

        # Переводим интерфейс заново, чтобы применить изменения
        if hasattr(self, "tabs"):
            self.retranslate_ui()
    
    def edit_record(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, FileTab):
            current_widget.edit_record()
    
    def add_record(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, FileTab):
            current_widget.add_record()

    def delete_record(self):
        current_widget = self.tabs.currentWidget()
        if isinstance(current_widget, FileTab):
            current_widget.delete_record()


    def retranslate_ui(self):
        """Переводит все элементы интерфейса на текущий язык"""
        # Заголовок окна
        self.setWindowTitle(self.tr("Object Database Manager"))

        # Меню "File"
        if hasattr(self, "file_menu") and self.file_menu:
            self.file_menu.setTitle(self.tr("&File"))
            self.new_action.setText(self.tr("&New"))
            self.open_action.setText(self.tr("&Open..."))
            self.save_action.setText(self.tr("&Save"))
            self.save_as_action.setText(self.tr("Save &As..."))
            self.exit_action.setText(self.tr("E&xit"))
            self.print_action.setText(self.tr("Print"))

        if hasattr(self, "lang_menu") and self.lang_menu:
            self.lang_menu.setTitle(self.tr("&Language"))

        # Меню "Help"
        if hasattr(self, "help_menu") and self.help_menu:
            self.help_menu.setTitle(self.tr("&Help"))
            self.about_action.setText(self.tr("&About"))

        # Меню "Chart"
        if hasattr(self, "chart_menu") and self.chart_menu:
            self.chart_menu.setTitle(self.tr("&Chart"))
            self.chart.setText(self.tr("&Charts"))

        # Статус бар
        if hasattr(self, "status_bar"):
            if self.current_file:
                self.status_bar.showMessage(
                    self.tr("File loaded: %s") % self.current_file
                )
            else:
                self.status_bar.showMessage(self.tr("New empty database created"))

        # Заголовки таблицы
        headers = [
            self.tr("ID"),  # Идентификатор
            self.tr("Name object"),  # Название объекта
            self.tr("Address"),  # Адрес
            self.tr("Date start building"),  # Дата начала строительства
            self.tr("Date end building"),  # Дата окончания строительства
            self.tr("Status"),  # Статус
            self.tr("Type object"),  # Тип объекта (жилой / коммерческий / промышленный)
            self.tr("Area"),  # Площадь
            self.tr("Floors"),  # Этажи
        ]
        records = [
            self.tr("Add Record"),
            self.tr("Edit Record"),
            self.tr("Delete Record"),
            self.tr("Search in Column"),
            self.tr("Submit"),
            self.tr("Cancel"),
        ]

        # Перевод каждой вкладки
        for index in range(self.tabs.count()):
            if (
                self.tabs.tabText(index) == "New Tab"
                or self.tabs.tabText(index) == "Новая вкладка"
            ):
                self.tabs.setTabText(index, self.tr("New Tab"))

            current_widget = self.tabs.widget(index)

            # Перевод таблицы
            table = current_widget.findChild(QTableWidget)
            for col, header in enumerate(headers):
                table.horizontalHeaderItem(col).setText(header)

            # Перевод кнопок
            buttons = current_widget.findChildren(QPushButton)
            for button, record in zip(buttons, records):
                button.setText(record)

            # Перевод выбора сортировки
            column_selector = current_widget.findChild(QComboBox)
            column_selector.clear()
            column_selector.addItems(headers)

            # Перевод меток
            labels = current_widget.findChildren(QLabel)
            for label, header in zip(labels, headers[1:]):  # пропускаем ID
                label.setText(self.tr(header) + ":")

            # Перевод placeholder в поле поиска
            search_input = current_widget.findChild(QLineEdit)
            if search_input:
                search_input.setPlaceholderText(self.tr("Enter text to search..."))



    def show_about(self):
        """Показывает информацию об авторе программы."""
        
        # В зависимости от языка, показываем разные описания
        if self.lang_code == "ru":
            about_text = """
        <b>Приложение для управления возведенными объектами строительных организаций</b><br><br>
        Версия: <b>1.0</b><br>
        Автор: <b>Райков Максим Сергеевич</b><br>
        Университет: <b>Московский Государственный Строительный Университет МГСУ</b><br>
        Институт: <b>ИЦТМС</b><br>
        Курс: <b>2</b><br>
        Группа: <b>2</b><br><br>
        """
        elif self.lang_code == "en":
            about_text = self.tr("""
        <b>Application for managing constructed objects of construction organizations</b><br><br>
        Version: <b>1.0</b><br>
        Author: <b>Raykov Maksim Sergeyvich</b><br>
        University: <b>Moscow State University of Civil Engineering (MGSU)</b><br>
        Institute: <b>ICTMS</b><br>
        Course: <b>2</b><br>
        Group: <b>2</b><br><br>
        """)
        else:
            about_text = """
        <b>Application de gestion des objets construits pour les organisations de construction</b><br><br>
        Version : <b>1.0</b><br>
        Auteur : <b>Raykov Maksim Sergeyvich</b><br>
        Université : <b>Université d'État de génie civil de Moscou (MGSU)</b><br>
        Institut : <b>ICTMS</b><br>
        Année : <b>2</b><br>
        Groupe : <b>2</b><br><br>"""
        # Создаем и показываем диалоговое окно
        msg = QMessageBox()
        msg.setWindowTitle(["О программе", "About"][self.lang_code == "en"])
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(about_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()


    def dragEnterEvent(self, event):
        # Проверяем, есть ли в данных события URL-адреса
        if event.mimeData().hasUrls():
            # Если есть, принимаем предложенное действие (перетаскивание)
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        # Принимаем предложенное действие (перетаскивание)
        event.acceptProposedAction()


    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # Для каждого URL (файла) в данных события
            for url in event.mimeData().urls():
                # Получаем локальный путь файла
                file_path = url.toLocalFile()
                # Если файл имеет расширение .txt, открываем его
                if file_path.endswith(".txt"):
                    self.open_file_by_path(file_path)
            # Принимаем предложенное действие (файл принят)
            event.acceptProposedAction()

    def open_file_by_path(self, path):
        Controller.open_file_by_path(self, path, FileTab)

    def close_tab(self, index):
        current_index = index # получение индекса 
        print(f"[INFO] Вкладка {index+1} удалена") # логи
        self.tabs.removeTab(current_index) # удаление по индексу
        self.statusBar().showMessage(self.tr("Tab closed")) # статус бар

        if self.tabs.count() == 0: # если 0 вкладок
            print("[INFO] Осталось 0 вкладок программа закрывается") # логи
            self.close() #закрываем окно

    def show_status(self, message):
        self.status_bar.showMessage(self.tr(message))


    def closeEvent(self, event):
        # Сохраняем настройки перед закрытием
        self.save_settings()
        
        # Проверяем, есть ли несохраненные изменения
        if self.current_file and self.data:
            reply = QMessageBox.question(
                self,
                self.tr("Unsaved Changes"),
                self.tr("Do you want to save changes before exiting?"),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Если пользователь выбрал сохранить, сохраняем файл
                if not self.save_file():
                    event.ignore()  # Игнорируем закрытие, если не удается сохранить
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                # Если пользователь выбрал отменить, прерываем закрытие
                event.ignore()
                return

        event.accept()  # Если все в порядке, принимаем закрытие

