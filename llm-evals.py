from openai import OpenAI
import re
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def prompt_llm(prompt: str):
    """
    Prompt the LLM and return the output text.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    output_text = response.choices[0].message.content
    print(output_text)
    return output_text

def generate_test_questions(topic: str, num_questions: int = 5):
    """
    Generates a list of test questions on a given topic.
    """
    prompt = f"Generate {num_questions} test questions about {topic}. Please provide them as a numbered list."
    raw_text = prompt_llm(prompt)
    questions = re.findall(r"\d+\.\s*(.*)", raw_text)
    return questions

def generate_answers(questions: list[str]):
    """
    Generates answers for a list of questions and returns question-answer pairs.
    """
    qa_pairs = []
    for question in questions:
        prompt = f"What is the answer to the following question: {question}"
        answer = prompt_llm(prompt)
        qa_pairs.append((question, answer))
    return qa_pairs

def evaluate_answers(qa_pairs: list[tuple[str, str]]):
    """
    Evaluates the correctness of answers in a list of question-answer pairs.
    Returns a list of scores.
    """
    scores = []
    for question, answer in qa_pairs:
        prompt = (
            f"Please evaluate the correctness of the following answer for the given question. "
            f"Provide a score from 1 to 5, where 1 is completely incorrect and 5 is completely correct and well-explained."
            f"\n\nQuestion: {question}\n\nAnswer: {answer}\n\nScore (1-5):"
        )
        response_text = prompt_llm(prompt)
        match = re.search(r'\b[1-5]\b', response_text)
        if match:
            scores.append(int(match.group(0)))
        else:
            print(f"Warning: Could not extract a score for question: '{question}'")
            scores.append(None)
    return scores

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
        qa_pairs = generate_answers(questions)

        print("\n--- Generated Q&A Pairs ---")
        for q, a in qa_pairs:
            print(f"Q: {q}\nA: {a}\n")

        print("\nEvaluating answers...")
        scores = evaluate_answers(qa_pairs)

        print("\n--- Evaluation Scores ---")
        total_score = 0
        valid_scores = 0
        for i, (q, a) in enumerate(qa_pairs):
            score = scores[i]
            print(f"Q: {q}\nScore: {score}/5\n" if score is not None else f"Q: {q}\nScore: Not available\n")
            if score is not None:
                total_score += score
                valid_scores += 1

        if valid_scores > 0:
            average_score = total_score / valid_scores
            print(f"\nAverage score: {average_score:.2f}/5")
        else:
            print("\nCould not calculate an average score.")

if __name__ == '__main__':
    main()