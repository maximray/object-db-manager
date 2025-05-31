# Object Database Manager

Приложение для управления возведёнными объектами строительных организаций. Реализовано с использованием архитектурного шаблона **MVC** на `PyQt6` и `matplotlib`.

## 🚀 Возможности

- Создание, редактирование, удаление объектов
- Поиск по таблице по выбранному столбцу
- Сохранение и загрузка файлов `.txt` с валидацией
- Поддержка **Drag-and-Drop** и контекстного меню
- Вкладочный интерфейс (многозадачность)
- Построение графиков:
  - Типы объектов по датам
- Поддержка печати таблицы
- Смена языка интерфейса: 🇷🇺 Русский / 🇬🇧 English
- Сохранение настроек (ширина колонок, язык, размеры окна)

## 🛠️ Стек технологий

- Python 3.10+
- PyQt6
- matplotlib
- QSettings, QTranslator

## 📦 Установка и запуск

```bash
# Клонируем репозиторий
git clone https://github.com/maximray/object-db-manager.git
cd object-db-manager

# Устанавливаем зависимости
pip install -r requirements.txt

# Компиляция файлов перевода
cd app/translations
lrelease translations_ru.ts translations_en.ts
cd ..
cd ..

# Запуск приложения
py -m app.app

# Автогенерация документации
cd app/docs
make.bat html
start build/html/index.html
```

## Пример входящих данных
```
###OBJECT_DB###
1|ЖК "Северное сияние"|ул. Полярная, 15|2023-01-15|2024-06-30|в процессе|жилой|12500|9

ID|Name object|Address|Date start building|Date end building|Status|Type object|Area|Floors
