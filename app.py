from flask import Flask, render_template, request, jsonify
import llm_evals
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    data = request.get_json()
    topic = data.get('topic', 'AI trivia')
    num_questions = int(data.get('num_questions', 5))
    questions = llm_evals.generate_test_questions(topic, num_questions)
    return jsonify({'questions': questions})

@app.route('/generate-answers', methods=['POST'])
def generate_answers():
    data = request.get_json()
    questions = data.get('questions', [])
    if not questions:
        return jsonify({'answers': []})
    answers = llm_evals.generate_answers(questions)
    return jsonify({'answers': answers})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    eval_data_str = request.form['eval_data']
    eval_prompt = request.form['eval_prompt']
    
    eval_data = json.loads(eval_data_str)

    questions_to_answer = [item['question'] for item in eval_data if item.get('question') and not item.get('answer')]
    if questions_to_answer:
        answers = llm_evals.generate_answers(questions_to_answer)
        
        answer_map = dict(zip(questions_to_answer, answers))
        
        for item in eval_data:
            if item['question'] in answer_map:
                item['answer'] = answer_map[item['question']]

    qa_pairs = [(item['question'], item['answer']) for item in eval_data if item.get('question') and item.get('answer')]

    if not qa_pairs:
        return render_template('index.html', results=[], average_score=0)

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

    return render_template('index.html', results=results, average_score=average_score)

if __name__ == '__main__':
    app.run(debug=True) 