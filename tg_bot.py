from functools import partial
import logging
import os
import random

from dotenv import load_dotenv
import redis
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from question_extractor import extract_question_with_answer


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_markdown_v2(
        fr'Здравствуй, {user.mention_markdown_v2()}\!',
        reply_markup=reply_markup
    )


def new_question(update: Update, context: CallbackContext, questions_with_answers, redis_db) -> None:
    random_question = random.choice(list(questions_with_answers.keys()))
    user_id = update.message.from_user["id"]
    if update.message.text == 'Новый вопрос':
        update.message.reply_text(random_question)
        redis_db.set(user_id, random_question)


if __name__ == '__main__':
    load_dotenv()
    tg_quiz_token = os.getenv('TG_QUIZ_BOT_TOKEN')
    questions_with_answers = extract_question_with_answer('quiz-questions')

    redis_pool = redis.ConnectionPool(
        host=os.getenv('REDIS_DB_HOST'),
        port=os.getenv('REDIS_DB_PORT'),
        username=os.getenv('REDIS_DB_USERNAME'),
        password=os.getenv('REDIS_DB_PASSWORD'),
        decode_responses=True
    )
    redis_db = redis.Redis(connection_pool=redis_pool)

    send_question = partial(new_question, questions_with_answers=questions_with_answers, redis_db=redis_db)

    updater = Updater(tg_quiz_token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_question))

    updater.start_polling()
    updater.idle()
