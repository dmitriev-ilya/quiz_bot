# quiz_bot


## Установка

Скачайте файлы из репозитория. Python3 должен быть уже установлен. 

Затем используйте `pip` (или `pip3`) для установки зависимостей:
```
pip install -r requirements.txt
```
Помимо этого, для работы понадобится создать файл `.env` в корневом каталоге проекта. Данный файл необходим для работы с переменными окружения и должен содержать в себе переменные: 
```
TG_QUIZ_BOT_TOKEN=<SUPPORT_BOT_TELEGRAM_TOKEN>
TELEGRAM_USER_ID=<TELEGRAM_USER_ID>
REDIS_DB_HOST=<адрес хоста Redis>
REDIS_DB_PORT=<порт (указан после двоеточия в Public endpoint)>
REDIS_DB_USERNAME=<REDIS DATABASE USERNAME>
REDIS_DB_PASSWORD=<REDIS DATABASE PASSWORD>
VK_GROUP_TOKEN=<VK_GROUP_API_TOKEN>
```

Для получения `REDIS_DB_HOST`, `REDIS_DB_PORT`, `REDIS_DB_USERNAME`, `REDIS_DB_PASSWORD` необходимо создать базу на [Redis](https://redis.com/). Все нужные параметры находятся на вкладке конфигурации БД:

![image](https://github.com/dmitriev-ilya/quiz_bot/assets/67222917/bb67d02d-5e9b-4c9c-acd3-a82731903668)

Также необходимо создать Telegram-бота для получения `TG_QUIZ_BOT_TOKEN`. Для этого нужно обратиться к [@BotFather](https://telegram.me/BotFather). Подробная инструкция по настройке и созданию бота приведена здесь - [Инструкция по созданию Telegram-бота](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram.html)

`TELEGRAM_USER_ID` можно получить, обратившись к боту [@userinfobot](https://t.me/getmyid_bot)

Для получения `VK_GROUP_TOKEN` создайте группу [VK](https://vk.com/groups?tab=admin), в настройках группы включите сообщения сообщества и разрешите боту отправку сообщений. Получить токен группы можно также в настройках:

![image](https://github.com/dmitriev-ilya/verb_game_support_bot/assets/67222917/3a1169a7-eb38-48b0-8cb3-0f770bdea080)

## Использование скриптов

Для запуска ботов в консоли, находясь в папке с проектом, используйте следующую команду:

```
python3 vk_bot.py
```

или 

```
python3 tg_bot.py
```
