from openai import OpenAI
from google import genai
import re
import os
from dotenv import load_dotenv
import concurrent.futures

load_dotenv()

client_openai = OpenAI()
client_google = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def prompt_openai_llm(prompt: str):
    """
    Prompt the LLM and return the output text.
    """
    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    output_text = response.choices[0].message.content
    print(output_text)
    return output_text

def prompt_google_llm(prompt: str):
    """
    Prompt the Google LLM and return the output text.
    """
    response = client_google.models.generate_content(
        model="gemini-2.5-flash-lite-preview-06-17",
        contents=prompt
    )
    print(response.text)
    return response.text

def generate_test_questions(topic: str, num_questions: int = 5):
    """
    Generates a list of test questions on a given topic in parallel.
    """
    def generate_single_question(topic_str: str):
        prompt = f"Generate one test question about {topic_str}."
        raw_text = prompt_openai_llm(prompt)
        match = re.search(r"^\s*\d+\.\s*(.*)", raw_text)
        if match:
            return match.group(1).strip()
        return raw_text.strip()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        questions = list(executor.map(generate_single_question, [topic] * num_questions))
    return questions

def generate_answers(questions: list[str]):
    """
    Generates answers for a list of questions in parallel and returns a list of answers.
    """
    def get_answer(question):
        prompt = f"What is the answer to the following question: {question}"
        return prompt_openai_llm(prompt)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        answers = list(executor.map(get_answer, questions))
    return answers

def evaluate_answers(qa_pairs: list[tuple[str, str]], eval_prompt_template: str, prompter_func):
    """
    Evaluates the correctness of answers in a list of question-answer pairs using a given prompter function in parallel.
    Returns a list of (score, notes) tuples.
    """
    def evaluate_single(qa_pair):
        question, answer = qa_pair
        prompt = eval_prompt_template.format(question=question, answer=answer)
        response_text = prompter_func(prompt)
        
        score_match = re.search(r"score:\s*([1-5])", response_text, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None
        
        if score is None:
            score_match = re.search(r'\b[1-5]\b', response_text)
            score = int(score_match.group(0)) if score_match else None
        
        notes_match = re.search(r"notes:(.*)", response_text, re.IGNORECASE | re.DOTALL)
        notes = notes_match.group(1).strip() if notes_match else response_text.strip()

        if score is not None:
            return (score, notes)
        else:
            print(f"Warning: Could not extract a score for question: '{question}'")
            return (None, notes)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        evaluations = list(executor.map(evaluate_single, qa_pairs))
    return evaluations

def main():
    topic = "AI trivia"
    print(f"Generating questions for topic: {topic}")
    questions = generate_test_questions(topic)
    print("\n--- Generated Questions ---")
    if questions:
        for q in questions:
            print(q)
    else:
        print("No questions were generated.")

    if questions:
        print("\nGenerating answers...")
        qa_pairs = []
        answers = generate_answers(questions)
        for i, question in enumerate(questions):
            qa_pairs.append((question, answers[i]))

        print("\n--- Generated Q&A Pairs ---")
        for q, a in qa_pairs:
            print(f"Q: {q}\nA: {a}\n")

        eval_prompt_template = (
            f"Please evaluate the correctness of the following answer for the given question. "
            f"Provide a score from 1 to 5, where 1 is completely incorrect and 5 is completely correct and well-explained."
            f"\n\nQuestion: {{question}}\n\nAnswer: {{answer}}\n\nScore (1-5):"
        )
        
        print("\n--- OpenAI Evaluation ---")
        evals_openai = evaluate_answers(qa_pairs, eval_prompt_template, prompt_openai_llm)

        print("\n--- Evaluation Scores (OpenAI) ---")
        total_score_openai = 0
        valid_scores_openai = 0
        for i, (q, a) in enumerate(qa_pairs):
            score, notes = evals_openai[i]
            print(f"Q: {q}\nScore: {score}/5\nNotes: {notes}\n" if score is not None else f"Q: {q}\nScore: Not available\nNotes: {notes}\n")
            if score is not None:
                total_score_openai += score
                valid_scores_openai += 1

        if valid_scores_openai > 0:
            average_score_openai = total_score_openai / valid_scores_openai
            print(f"\nAverage score (OpenAI): {average_score_openai:.2f}/5")
        else:
            print("\nCould not calculate an average score for OpenAI.")

        print("\n--- Google Evaluation ---")
        evals_google = evaluate_answers(qa_pairs, eval_prompt_template, prompt_google_llm)

        print("\n--- Evaluation Scores (Google) ---")
        total_score_google = 0
        valid_scores_google = 0
        for i, (q, a) in enumerate(qa_pairs):
            score, notes = evals_google[i]
            print(f"Q: {q}\nScore: {score}/5\nNotes: {notes}\n" if score is not None else f"Q: {q}\nScore: Not available\nNotes: {notes}\n")
            if score is not None:
                total_score_google += score
                valid_scores_google += 1
        
        if valid_scores_google > 0:
            average_score_google = total_score_google / valid_scores_google
            print(f"\nAverage score (Google): {average_score_google:.2f}/5")
        else:
            print("\nCould not calculate an average score for Google.")

if __name__ == '__main__':
    main()