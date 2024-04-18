# Сервис Foodgram - продуктовый помощник

![example workflow](https://github.com/kzarsnake/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание:
Сервис Foodgram позволяет пользователю создавать и редактировать рецепты блюд, оформлять подписку на других пользователей, добавлять рецепты в избранное и формировать список покупок на основе ингредиентов из рецептов. Список покупок можно выгрузить в виде файла (`формат .txt`).

## Стэк технологий:
* Django
* Django Rest Framework
* Docker
* Docker-compose
* Gunicorn
* Nginx
* PostgreSQL
* Workflow

## Workflow
* tests: Проверка кода на соответствие PEP8.
* push Docker image to Docker Hub: Сборка и публикация образа на DockerHub.
* deploy: Автоматический деплой на боевой сервер при пуше в главную ветку main.
* send_massage: Отправка уведомления в телеграм-чат.

## Запуск проекта

- Установите Docker на ваш сервер:
```
sudo apt install docker.io
```

- Установите Docker-compose на сервер:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

- Скопируйте на сервер файлы Docker-compose.yml и nginx.conf из папки infra/. Укажите в конфиге ваш IP.
```
scp docker-compose.yml <user>@<server_ip>:/home/<user>/docker-compose.yml
scp nginx.conf <user>@<server_ip>:/home/<user>/nginx.conf
```

- При первом деплоее локально в файле foodgram_workflow.yml в deploy указываем флаг --build:
```
sudo docker-compose rm -f backend --build
```

- После успешного деплоя зайдите на боевой сервер и выполните команды (только после первого деплоя):
    Собрать статические файлы в STATIC_ROOT:
```
docker-compose exec backend python manage.py collectstatic --noinput
```

- После запуска контейнеров выполните команды в терминале:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate --noinput
```

- Создаём суперпользователя
```
docker-compose exec backend python manage.py createsuperuser
```

- Загружаем ингредиенты в базу данных (необязательно):
```
docker-compose exec backend python manage.py loaddata ingredients.json
```

- Запуск контейнеров выполняется командой:
```
docker-compose up
```

- Остановка контейнеров выполняется командой:
```
docker-compose stop
```

## Базовые модели проекта

### Рецепт - все поля обязательны для заполнения
* Автор публикации (пользователь)
* Название
* Картинка
* Текстовое описание
* Ингредиенты: продукты для приготовления блюда по рецепту. Множественное поле, выбор из предустановленного списка, с указанием количества и единицы измерения
* Тег (можно установить несколько тегов на один рецепт, выбор из предустановленных)
* Время приготовления в минутах

### Тег - все поля обязательны для заполнения и уникальны
* Название
* Цветовой HEX-код (например, #49B64E)
* Slug

### Ингредиент - все поля обязательны для заполнения
Данные об ингредиентах хранятся в нескольких связанных таблицах. В результате на стороне пользователя ингредиент должен описываться такими полями:

* Название
* Количество
* Единицы измерения

## Технические требования и инфраструктура

* Проект должен использовать базу данных PostgreSQL
* Код должен находиться в репозитории `foodgram-project-react`
* В Django-проекте должен быть файл `requirements.txt` со всеми зависимостями
* Проект нужно запустить в трёх контейнерах (nginx, PostgreSQL и Django) (контейнер frontend используется лишь для подготовки файлов) через docker-compose на вашем сервере в Яндекс.Облаке. Образ с проектом должен быть запушен на Docker Hub

## Шаблон наполнения .env файла
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
DB_PORT=5432
SECRET_KEY='0q%8n81^k%z-eu1n1@mjgpc08c2)19q7mmsuft434jb_x+a*-#'
```

## Автор проекта:

[Денис Свашенко](https://github.com/KzarSnake)
