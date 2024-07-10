
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    if not current_question_id:
        return False, "There is no current question to answer."

    question = PYTHON_QUESTION_LIST.get(current_question_id)
    if not question:
        return False, "Invalid question ID."

    valid_answers = question.get('valid_answers', [])
    if answer not in valid_answers:
        return False, f"Invalid answer. Please choose from {valid_answers}."

    # Store the answer
    user_answers = session.get("user_answers", {})
    user_answers[current_question_id] = answer
    session["user_answers"] = user_answers
    session.save()
    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    questions = PYTHON_QUESTION_LIST
    
    # Get the list of question IDs
    question_ids = list(questions.keys())
    
    # Find the index of the current question
    try:
        current_index = question_ids.index(current_question_id)
    except ValueError:
        return "Invalid question ID", -1  # Invalid current_question_id
    
    # Get the next question index
    next_index = current_index + 1
    
    if next_index < len(question_ids):
        next_question_id = question_ids[next_index]
        next_question = questions[next_question_id]['question_text']
        return next_question, next_question_id
    else:
        return "No more questions available", -1  # No more questions available


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("user_answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0
    
    for question_id, user_answer in user_answers.items():
        question = PYTHON_QUESTION_LIST.get(question_id)
        if question and user_answer in question['valid_answers']:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    return f"Quiz completed!\nYou answered {correct_answers} out of {total_questions} questions correctly.\nYour score: {score:.2f}%"
