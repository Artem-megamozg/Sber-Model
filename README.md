# Sber-Model
В данном репозитории реализовано использование модели SberGiGaChat, как врачебного помощника-ассистента, который может подсказать какие поликлиники доступны и какие врачи в них есть, также можно зарегистрироваться в базе пациентов и записаться на приём к нужному врачу 
# Описание проекта: Врачебный ассистент на основе языковой модели
Этот проект представляет собой приложение для взаимодействия с языковой моделью, предназначенное для помощи пользователям в записи к врачам и предоставления информации о медицинских услугах. Приложение использует библиотеку tkinter для создания графического интерфейса и обращается к GraphQL API для получения данных о врачах, клиниках и пациентах.

Структура проекта
Проект состоит из двух основных частей:

Получение данных с сервера:

Код, отвечающий за взаимодействие с GraphQL сервером для получения информации о врачах, клиниках, пациентах и их записях.
Функции для выполнения запросов к API и форматирования полученных данных для удобного отображения.
Интерфейс взаимодействия с пользователем:

Использует tkinter для создания графического интерфейса, где пользователи могут вводить свои симптомы и получать рекомендации по записи к врачу.
Языковая модель GigaChat обрабатывает пользовательские запросы и предоставляет информацию на основе загруженных данных о врачах.
Основные функции
Получение данных с сервера
GraphQL запросы:

get_all_doctor_types(): Получает все типы врачей.
get_all_doctors(): Получает список всех врачей.
get_all_customers(): Получает информацию о клиентах.
get_all_clinics(): Получает данные о клиниках.
get_clinic_offices(clinic_id): Получает кабинеты в указанной клинике.
get_doctor_availability(clinic_doctor_id, date_from, date_to): Получает доступность врача в указанные даты.
Форматирование данных:

Функции для форматирования полученных данных в виде таблиц с использованием библиотеки tabulate, что позволяет удобно отображать информацию в консоли.
Интерфейс взаимодействия с пользователем
Графический интерфейс:

Создание главного окна с текстовым полем для чата и полем ввода для пользовательских сообщений.
Кнопки для отправки сообщений и записи к врачу.
Обработка пользовательских запросов:

Получение симптомов от пользователя и определение, какой врач ему нужен.
В случае необходимости, предложение зарегистрироваться и предоставление формы для ввода личной информации.
Интеграция с языковой моделью:

Использование GigaChat для обработки пользовательских сообщений и предоставления рекомендаций на основе загруженных данных о врачах и клиниках.

Файловая струтура репозитория:
---release3.py => это основной файл, который получает использует языковую модель, получает и сортирует данные с сервера, предоставляет функционал ###
---doctor.py => это дополнительный файл к release3 который помогает записаться к врачу ###
---zapis.py => это допольнительный файл к release3 который регистрирует пациентов в системе ###
---vivod.py => это файл который считывает всю информацию с сервера, сортирует и выводит в терминал ###
---test-api => это папка с начатой фронтенд частью для проекта

