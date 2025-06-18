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
        return render_template('index.html', results=[], average_score_openai=0, average_score_google=0)

    evaluations_openai = llm_evals.evaluate_answers(qa_pairs, eval_prompt, llm_evals.prompt_openai_llm)
    evaluations_google = llm_evals.evaluate_answers(qa_pairs, eval_prompt, llm_evals.prompt_google_llm)

    results = []
    total_score_openai = 0
    valid_scores_openai = 0
    total_score_google = 0
    valid_scores_google = 0

    for i, (q, a) in enumerate(qa_pairs):
        score_openai, notes_openai = evaluations_openai[i]
        score_google, notes_google = evaluations_google[i]
        results.append({
            'question': q, 
            'answer': a, 
            'openai_score': score_openai, 
            'openai_notes': notes_openai,
            'google_score': score_google,
            'google_notes': notes_google
        })
        if score_openai is not None:
            total_score_openai += score_openai
            valid_scores_openai += 1
        if score_google is not None:
            total_score_google += score_google
            valid_scores_google += 1
    
    average_score_openai = total_score_openai / valid_scores_openai if valid_scores_openai > 0 else 0
    average_score_google = total_score_google / valid_scores_google if valid_scores_google > 0 else 0

    return render_template('index.html', results=results, average_score_openai=average_score_openai, average_score_google=average_score_google)

if __name__ == '__main__':
    app.run(debug=True) 