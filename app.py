from flask import Flask, render_template, request
import llm_evals

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    topic = request.form['topic']
    num_questions = int(request.form['num_questions'])
    custom_questions = request.form['questions']
    eval_prompt = request.form['eval_prompt']

    if custom_questions:
        questions = custom_questions.strip().split('\n')
    else:
        questions = llm_evals.generate_test_questions(topic, num_questions)

    qa_pairs = llm_evals.generate_answers(questions)
    scores = llm_evals.evaluate_answers(qa_pairs, eval_prompt)

    results = []
    total_score = 0
    valid_scores = 0
    for i, (q, a) in enumerate(qa_pairs):
        score = scores[i]
        results.append({'question': q, 'answer': a, 'score': score})
        if score is not None:
            total_score += score
            valid_scores += 1
    
    average_score = total_score / valid_scores if valid_scores > 0 else 0

    return render_template('results.html', results=results, average_score=average_score)

if __name__ == '__main__':
    app.run(debug=True) 