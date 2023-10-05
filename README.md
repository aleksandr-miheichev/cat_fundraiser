# CatFundraiser: Платформа целевых пожертвований для кошачьих проектов

## Содержание

- [Описание проекта](#описание-проекта)
- [Технологический стек](#технологический-стек)
- [Как развернуть проект](#как-развернуть-проект)
- [Шаблон наполнения файла .env](#шаблон-наполнения-файла-env)
- [Настройка базы данных](#настройка-базы-данных)
- [Запуск приложения](#запуск-приложения)
- [Документация API](#документация-api)
- [Над проектом работал](#над-проектом-работал)

---

### Описание проекта:

Фонд собирает пожертвования на различные целевые проекты: на медицинское
обслуживание нуждающихся хвостатых, на обустройство кошачьей колонии в
подвале, на корм оставшимся без попечения кошкам — на любые цели, связанные с
поддержкой кошачьей популяции. В приложении есть возможность формирования
отчёта в гугл-таблице. В таблице будут закрытые проекты, отсортированные по
скорости сбора средств — от тех, что закрылись быстрее всего, до тех, что долго
собирали нужную сумму.

#### Проекты

В Фонде может быть открыто несколько целевых проектов. У каждого проекта
есть название, описание и сумма, которую планируется собрать. После того как
нужная сумма собрана — проект закрывается.

Пожертвования в проекты поступают по принципу First In, First Out: все
пожертвования идут в проект, открытый раньше других; когда этот проект
набирает необходимую сумму и закрывается — пожертвования начинают поступать в
следующий проект.

#### Пожертвования

Каждый пользователь может сделать пожертвование и сопроводить его комментарием.
Пожертвования не целевые: они вносятся в фонд, а не в конкретный проект.
Каждое полученное пожертвование автоматически добавляется в первый открытый
проект, который ещё не набрал нужную сумму. Если пожертвование больше нужной
суммы или же в Фонде нет открытых проектов — оставшиеся деньги ждут открытия
следующего проекта. При создании нового проекта все неинвестированные
пожертвования автоматически вкладываются в новый проект.

#### Пользователи

Целевые проекты создаются администраторами сайта.

Любой пользователь может видеть список всех проектов, включая требуемые и уже
внесенные суммы. Это касается всех проектов — и открытых, и закрытых.

Зарегистрированные пользователи могут отправлять пожертвования и просматривать
список своих пожертвований.

---

### Технологический стек:

- [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
- [![FastAPI](https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white)](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [FastAPI Users](https://fastapi-users.github.io/fastapi-users/)
- [Aiogoogle](https://aiogoogle.readthedocs.io/en/latest/)
- [![Google Sheets API](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)](https://developers.google.com/sheets/api/guides/concepts?hl=en)
- [![Google Sheets API](https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://developers.google.com/drive/api/guides/about-sdk?hl=en)

---

### Как развернуть проект:

Клонировать репозиторий и перейти в него в терминале используя команду

```
cd
```

```bash
git clone git@github.com:aleksandr-miheichev/cat_fundraiser.git
```

Создать и активировать виртуальное окружение:

```bash
python -m venv venv
```

```bash
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

___

### Шаблон наполнения файла .env:

```
APP_TITLE=Кошачий благотворительный фонд
DESCRIPTION=Сервис для поддержки котиков!
DATABASE_URL=sqlite+aiosqlite:///./fastapi.db
SECRET=Secret
FIRST_SUPERUSER_EMAIL=test@gmail.com
FIRST_SUPERUSER_PASSWORD=test
EMAIL=ya.test@gmail.com
TYPE=service_account
PROJECT_ID=massive-current-387709
PRIVATE_KEY_ID=35613ds5fg13ds56g43sdh4513sdf5h46
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\xxyyzz=\n-----END PRIVATE KEY-----\n"
CLIENT_EMAIL=admin@massive-current-387709.iam.gserviceaccount.com
CLIENT_ID=117011975999992899009
AUTH_URI=https://accounts.google.com/o/oauth2/auth
TOKEN_URI=https://oauth2.googleapis.com/token
AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/admin2%40massive-current-387709.iam.gserviceaccount.com
```

___

### Настройка базы данных:

Применить миграции:

```bash
alembic upgrade head 
```

---

### Запуск приложения:

Чтобы запустить приложение, необходимо в терминале использовать команду:

```bash
uvicorn app.main:app --reload
```

---

### Документация API:

- [Swagger](http://127.0.0.1:8000/docs)
- [Redoc](http://127.0.0.1:8000/redoc)

---

### Над проектом работал:

- [Михеичев Александр](https://github.com/aleksandr-miheichev)
