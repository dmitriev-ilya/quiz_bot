import os


def extract_question_with_answer(question_dir_name):
    questions_with_answers = {}
    for filename in os.listdir(question_dir_name):
        with open(os.path.join(question_dir_name, filename), 'r', encoding='KOI8-R') as question_file:
            question_file_context = question_file.read()
        question = None
        for line in question_file_context.split('\n\n'):
            line_title = line.split(':\n')[0]
            line_text = line.split(':\n')[-1]
            if 'вопрос' in line_title.lower():
                question = line_text
            elif 'ответ' in line_title.lower():
                questions_with_answers[question] = line_text
    return questions_with_answers


if __name__ == '__main__':
    question_dir_name = 'quiz-questions'

    questions_with_answers = extract_question_with_answer(question_dir_name)
    print(questions_with_answers)
