from openai import OpenAI
from google import genai
import re
import os
from dotenv import load_dotenv

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

def generate_test_questions(topic: str, num_questions: int = 5):
    """
    Generates a list of test questions on a given topic.
    """
    prompt = f"Generate {num_questions} test questions about {topic}. Please provide them as a numbered list."
    raw_text = prompt_openai_llm(prompt)
    questions = re.findall(r"\d+\.\s*(.*)", raw_text)
    return questions

def generate_answers(questions: list[str]):
    """
    Generates answers for a list of questions and returns a list of answers.
    """
    answers = []
    for question in questions:
        prompt = f"What is the answer to the following question: {question}"
        answer = prompt_openai_llm(prompt)
        answers.append(answer)
    return answers

def evaluate_answers(qa_pairs: list[tuple[str, str]], eval_prompt_template: str):
    """
    Evaluates the correctness of answers in a list of question-answer pairs.
    Returns a list of (score, notes) tuples.
    """
    evaluations = []
    for question, answer in qa_pairs:
        prompt = eval_prompt_template.format(question=question, answer=answer)
        response_text = prompt_openai_llm(prompt)
        
        score_match = re.search(r'\b[1-5]\b', response_text)
        score = int(score_match.group(0)) if score_match else None
        
        notes = response_text.strip()

        if score is not None:
            evaluations.append((score, notes))
        else:
            print(f"Warning: Could not extract a score for question: '{question}'")
            evaluations.append((None, notes))
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

        print("\nEvaluating answers...")
        eval_prompt_template = (
            f"Please evaluate the correctness of the following answer for the given question. "
            f"Provide a score from 1 to 5, where 1 is completely incorrect and 5 is completely correct and well-explained."
            f"\n\nQuestion: {{question}}\n\nAnswer: {{answer}}\n\nScore (1-5):"
        )
        evals = evaluate_answers(qa_pairs, eval_prompt_template)

        print("\n--- Evaluation Scores ---")
        total_score = 0
        valid_scores = 0
        for i, (q, a) in enumerate(qa_pairs):
            score, notes = evals[i]
            print(f"Q: {q}\nScore: {score}/5\nNotes: {notes}\n" if score is not None else f"Q: {q}\nScore: Not available\nNotes: {notes}\n")
            if score is not None:
                total_score += score
                valid_scores += 1

        if valid_scores > 0:
            average_score = total_score / valid_scores
            print(f"\nAverage score: {average_score:.2f}/5")
        else:
            print("\nCould not calculate an average score.")

if __name__ == '__main__':
    prompt_google_llm("Hi")
    # main()