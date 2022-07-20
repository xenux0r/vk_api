# Имитация API VK

Перед началом работы, введите в локальный терминал команды:

 1. Создать образ БД `docker-compose -f docker-compose.yaml up -d`
 2.  Выполнить инициализацию БД внутри приложения `FLASK_APP=wsgi.py flask db init`
 3. Зафиксировать изменения в БД `FLASK_APP=wsgi.py flask db migrate -m "Init commit"`
 4. Внести изменения в БД `FLASK_APP=wsgi.py flask db upgrade`
 5. Более простой путь использовать дамп базы данных (пропускаем 2, 3, 4 пункт)

После запуска приложения доступ к Swagger будет доступен по адресу `http://127.0.0.1:5000/docs/`