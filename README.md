# FastAPI Highload Shop Backend



Учебный backend-сервис для массовых покупок.  

Эндпоинт purchase атомарно списывает товар со склада и выдерживает 1000+ RPS без гонок данных.



\## Стек

FastAPI + Uvicorn\ (4 workers)

PostgreSQL 16 — атомарный `UPDATE ... RETURNING` для защиты от race condition

Redis 7 — кэш стока с Lua-скриптом для быстрой проверки и списания

RabbitMQ— брокер событий о покупках

Docker Compose — оркестрация всех сервисов



\## Быстрый запуск

bash

git clone https://github.com/maloy-stack/fastapi-shop-backend

cd fastapi-shop-backend

docker compose up -d --build



API доступен по адресу http://localhost:8000/docs.

Пример запроса

bash



curl -X POST http://localhost:8000/purchase \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"user\_id":12345,"product\_id":42,"purchased\_count":2}'



Ответ: {"status":"success"}.

Как это работает



Каждый запрос выполняет один SQL-запрос:

sql



UPDATE products

SET stock = stock - :amount

WHERE product\_id = :pid AND stock >= :amount

RETURNING stock



Если RETURNING ничего не вернул — возвращаем 409 «Недостаточно товара».

Так гарантируется консистентность без блокировок.



Redis с Lua-скриптом дублирует быструю проверку, разгружая базу.

RabbitMQ публикует событие о покупке для возможной дальнейшей обработки.

Нагрузочное тестирование

Locust (интерактивный)

bash



docker compose --profile testing up locust



Открой http://localhost:8089, укажи хост http://api:8000 и запусти тест.

Скрипт на aiohttp (100 000 запросов)

bash



python tests/stress\_test.py



Скрипт асинхронно отправляет 100k запросов и выводит количество успешных ответов и ошибок.
