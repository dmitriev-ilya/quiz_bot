import random
import os
import logging
from time import sleep

import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import redis

from logger import SupportBotLogsHandler
from question_extractor import extract_question_with_answer


logger = logging.getLogger(__name__)


def handle_quiz_request(event, vk_api, questions_with_answers, redis_db):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.SECONDARY)

    user_id = event.user_id

    if event.text == 'Новый вопрос':
        random_question = random.choice(list(questions_with_answers.keys()))
        redis_db.set(user_id, random_question)
        message = random_question
    elif event.text == 'Сдаться':
        answer = questions_with_answers.get(redis_db.get(user_id))
        random_question = random.choice(list(questions_with_answers.keys()))
        redis_db.set(user_id, random_question)
        message = f'{answer} \n\n Лови следующий вопрос:\n {random_question}'

    else:
        answer = questions_with_answers.get(redis_db.get(user_id))
        short_answer = answer.split('.')[0].split(' (')[0].lower()

        users_text = event.text
        formated_user_text = users_text.lower().split('.')[0].split(' (')[0]

        if formated_user_text == short_answer:
            message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        else:
            message = 'Неправильно… Попробуешь ещё раз?'

    vk_api.messages.send(
        user_id=user_id,
        message=message,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard()
    )


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv('VK_GROUP_TOKEN')
    telegram_bot_token = os.getenv('TG_QUIZ_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_USER_ID')
    quiz_dir_path = os.getenv('QUIZ_DIR_PATH')

    questions_with_answers = extract_question_with_answer(quiz_dir_path)

    redis_pool = redis.ConnectionPool(
        host=os.getenv('REDIS_DB_HOST'),
        port=os.getenv('REDIS_DB_PORT'),
        username=os.getenv('REDIS_DB_USERNAME'),
        password=os.getenv('REDIS_DB_PASSWORD'),
        decode_responses=True
    )
    redis_db = redis.Redis(connection_pool=redis_pool)

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    logging.basicConfig(level=logging.INFO)
    logger.addHandler(SupportBotLogsHandler(telegram_bot_token, telegram_chat_id))

    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    handle_quiz_request(event, vk_api, questions_with_answers, redis_db)
        except Exception as err:
            logger.error('ВК-бот упал с ошибкой:')
            logger.error(err, exc_info=True)
            sleep(5)
