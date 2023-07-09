from functools import partial
import logging
import os
import random

from dotenv import load_dotenv
import redis
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from logger import SupportBotLogsHandler
from question_extractor import extract_question_with_answer


logger = logging.getLogger(__name__)

QUESTION, ANSWER = range(2)


def start(update: Update, context: CallbackContext):
    user = update.effective_user

    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счёт']
    ]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Здравствуй, {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup
    )
    return QUESTION


def handle_new_question_request(update: Update, context: CallbackContext, questions_with_answers, redis_db):
    user_id = update.message.from_user["id"]

    random_question = random.choice(list(questions_with_answers.keys()))
    update.message.reply_text(random_question)
    redis_db.set(user_id, random_question)

    return ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, questions_with_answers, redis_db):
    user_id = update.message.from_user["id"]

    answer = questions_with_answers.get(redis_db.get(user_id))
    short_answer = answer.split('.')[0].split(' (')[0].lower()

    users_text = update.message.text
    formated_user_text = users_text.lower().split('.')[0].split(' (')[0]

    if formated_user_text == short_answer:
        update.message.reply_text(text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        return QUESTION
    else:
        update.message.reply_text(text='Неправильно… Попробуешь ещё раз?')
        return ANSWER


def handle_solution(update: Update, context: CallbackContext, questions_with_answers, redis_db):
    user_id = update.message.from_user["id"]
    answer = questions_with_answers.get(redis_db.get(user_id))
    update.message.reply_text(answer)

    update.message.reply_text('Лови следующий вопрос:')

    random_question = random.choice(list(questions_with_answers.keys()))
    update.message.reply_text(random_question)
    redis_db.set(user_id, random_question)

    return ANSWER


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Пока! Надеюсь скоро увидимся!',
        reply_markup=ReplyKeyboardRemove()
    )


if __name__ == '__main__':
    load_dotenv()
    tg_quiz_token = os.getenv('TG_QUIZ_BOT_TOKEN')
    quiz_dir_path = os.getenv('QUIZ_DIR_PATH')
    telegram_chat_id = os.getenv('TELEGRAM_USER_ID')

    questions_with_answers = extract_question_with_answer(quiz_dir_path)

    logging.basicConfig(level=logging.INFO)
    logger.addHandler(SupportBotLogsHandler(tg_quiz_token, telegram_chat_id))

    redis_pool = redis.ConnectionPool(
        host=os.getenv('REDIS_DB_HOST'),
        port=os.getenv('REDIS_DB_PORT'),
        username=os.getenv('REDIS_DB_USERNAME'),
        password=os.getenv('REDIS_DB_PASSWORD'),
        decode_responses=True
    )
    redis_db = redis.Redis(connection_pool=redis_pool)

    send_question = partial(
        handle_new_question_request,
        questions_with_answers=questions_with_answers,
        redis_db=redis_db
    )
    check_answer = partial(
        handle_solution_attempt,
        questions_with_answers=questions_with_answers,
        redis_db=redis_db
    )
    send_answer = partial(
        handle_solution,
        questions_with_answers=questions_with_answers,
        redis_db=redis_db
    )

    updater = Updater(tg_quiz_token)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            QUESTION: [
                MessageHandler(Filters.regex('Новый вопрос'), send_question)
            ],
            ANSWER: [
                MessageHandler(Filters.regex('Сдаться'), send_answer),
                MessageHandler(Filters.text & ~Filters.command, check_answer)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
