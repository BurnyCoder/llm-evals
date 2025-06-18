"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from llm_evals import llm_evals_logic
import pandas as pd
from typing import List, Dict, Any

from rxconfig import config


class State(rx.State):
    """The app state."""
    topic: str = "AI trivia"
    num_questions: int = 5
    eval_prompt: str = """Please evaluate the correctness of the following answer for the given question. Provide a score from 1 to 5, where 1 is completely incorrect and 5 is completely correct and well-explained.

Format response in this style:
                    
Score: {{score}}
                    
Question: {question}
                    
Answer: {answer}
                    
Notes: {{notes}}"""

    results: List[Dict[str, str]] = [
        {"Question": "", "Answer": "", "OpenAI Score": "", "OpenAI Notes": "", "Google Score": "", "Google Notes": ""}
        for _ in range(5)
    ]
    
    average_score_openai: float = 0.0
    average_score_google: float = 0.0
    is_loading: bool = False

    @rx.var
    def results_for_editor(self) -> List[List[str]]:
        """The results in a format suitable for the data editor."""
        columns = ["Question", "Answer", "OpenAI Score", "OpenAI Notes", "Google Score", "Google Notes"]
        return [[row.get(col, "") for col in columns] for row in self.results]

    def set_num_questions(self, value: str):
        try:
            self.num_questions = int(value)
        except ValueError:
            self.num_questions = 0

    def handle_cell_edit(self, change: Any):
        col_index = change["col"]
        row_index = change["row"]
        new_value = change["data"]
        
        columns = ["Question", "Answer", "OpenAI Score", "OpenAI Notes", "Google Score", "Google Notes"]
        column_name = columns[col_index]

        self.results[row_index][column_name] = new_value

    def add_row(self):
        self.results.append({"Question": "", "Answer": "", "OpenAI Score": "", "OpenAI Notes": "", "Google Score": "", "Google Notes": ""})

    async def generate_questions(self):
        self.is_loading = True
        yield
        questions = llm_evals_logic.generate_test_questions(self.topic, self.num_questions)
        self.results = [
            {"Question": q, "Answer": "", "OpenAI Score": "", "OpenAI Notes": "", "Google Score": "", "Google Notes": ""}
            for q in questions
        ]
        self.is_loading = False
    
    def _populate_answers(self):
        """Helper to generate answers for questions without them."""
        questions_to_answer = [row["Question"] for row in self.results if row["Question"] and not row["Answer"]]
        if questions_to_answer:
            answers = llm_evals_logic.generate_answers(questions_to_answer)
            answer_map = dict(zip(questions_to_answer, answers))
            for row in self.results:
                if row["Question"] in answer_map:
                    row["Answer"] = answer_map[row["Question"]]

    async def generate_answers(self):
        self.is_loading = True
        yield
        self._populate_answers()
        self.is_loading = False

    async def run_evaluation(self):
        self.is_loading = True
        yield
        
        self._populate_answers()

        qa_pairs = [(row["Question"], row["Answer"]) for row in self.results if row["Question"] and row["Answer"]]
        
        if not qa_pairs:
            self.is_loading = False
            return

        evaluations_openai = llm_evals_logic.evaluate_answers(qa_pairs, self.eval_prompt, llm_evals_logic.prompt_openai_llm)
        evaluations_google = llm_evals_logic.evaluate_answers(qa_pairs, self.eval_prompt, llm_evals_logic.prompt_google_llm)

        total_score_openai = 0
        valid_scores_openai = 0
        total_score_google = 0
        valid_scores_google = 0
        
        new_results = [dict(r) for r in self.results]

        for i, (q, a) in enumerate(qa_pairs):
            original_index = -1
            for idx, row in enumerate(new_results):
                if row["Question"] == q and row["Answer"] == a:
                    original_index = idx
                    break
            
            if original_index == -1: continue

            score_openai, notes_openai = evaluations_openai[i]
            score_google, notes_google = evaluations_google[i]
            
            new_results[original_index]["OpenAI Score"] = str(score_openai) if score_openai is not None else "N/A"
            new_results[original_index]["OpenAI Notes"] = notes_openai
            new_results[original_index]["Google Score"] = str(score_google) if score_google is not None else "N/A"
            new_results[original_index]["Google Notes"] = notes_google

            if score_openai is not None:
                total_score_openai += score_openai
                valid_scores_openai += 1
            if score_google is not None:
                total_score_google += score_google
                valid_scores_google += 1
        
        self.results = new_results
        self.average_score_openai = total_score_openai / valid_scores_openai if valid_scores_openai > 0 else 0
        self.average_score_google = total_score_google / valid_scores_google if valid_scores_google > 0 else 0

        self.is_loading = False

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("LLM Evaluation Sheet", size="7"),
            
            rx.hstack(
                rx.cond(
                    State.average_score_openai > 0,
                    rx.badge(f"OpenAI Avg: {State.average_score_openai:.2f}/5", color_scheme="grass")
                ),
                rx.cond(
                    State.average_score_google > 0,
                    rx.badge(f"Google Avg: {State.average_score_google:.2f}/5", color_scheme="grass")
                ),
                spacing="4"
            ),

            rx.hstack(
                rx.input(placeholder="Topic", value=State.topic, on_change=State.set_topic, width="300px"),
                rx.input(placeholder="Number of Questions", value=State.num_questions.to_string(), on_change=State.set_num_questions, type="number"),
                rx.button("Generate Questions", on_click=State.generate_questions, is_loading=State.is_loading),
                spacing="4",
                align="center",
                width="100%",
            ),
            
            rx.data_editor(
                columns=[
                    {"title": "Question", "id": "Question", "type": "str", "width": 300},
                    {"title": "Answer", "id": "Answer", "type": "str", "width": 400},
                    {"title": "OpenAI Score", "id": "OpenAI Score", "type": "str"},
                    {"title": "OpenAI Notes", "id": "OpenAI Notes", "type": "str", "width": 250},
                    {"title": "Google Score", "id": "Google Score", "type": "str"},
                    {"title": "Google Notes", "id": "Google Notes", "type": "str", "width": 250},
                ],
                data=State.results_for_editor,
                on_cell_edited=State.handle_cell_edit,
                row_height=40,
                height="35vh",
                width="100%"
            ),
            
            rx.hstack(
                rx.button("Add Row", on_click=State.add_row),
                rx.button("Generate Answers", on_click=State.generate_answers, is_loading=State.is_loading),
                spacing="4",
                align="center",
            ),

            rx.text_area(value=State.eval_prompt, on_change=State.set_eval_prompt, height="150px", width="100%", placeholder="Evaluation Prompt"),

            rx.button("Run Evaluation", on_click=State.run_evaluation, is_loading=State.is_loading, size="3", width="100%"),

            spacing="5",
            width="100%",
        ),
        padding_top="2em",
        padding_x="1em",
        width="100vw",
        height="100vh",
    )

app = rx.App(
    theme=rx.theme(
        appearance="light",
    )
)
app.add_page(index)
