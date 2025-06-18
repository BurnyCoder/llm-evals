# LLM Evaluation Sheet

This is a web application built with [Reflex](https://reflex.dev/) that allows you to evaluate and compare the performance of different Large Language Models (LLMs), specifically OpenAI and Google models.

![image](https://github.com/user-attachments/assets/f0e4ac17-c476-4172-93d7-b67566b43b00)

## Features

- **Generate Questions:** Automatically generate a set of questions on a given topic.
- **Generate Answers:** Automatically generate answers for the questions using a selected LLM.
- **Side-by-Side Evaluation:** Score the answers from both OpenAI and Google models and add notes.
- **Dynamic Table:** Add or remove rows from the evaluation sheet as needed.
- **Custom Evaluation Prompt:** Modify the prompt used to evaluate the answers.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/BurnyCoder/llm-evals/
    cd llm-evals
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your environment variables:**
    Create a `.env` file in the root of the project and add your API keys:
    ```
    OPENAI_API_KEY="your-openai-api-key"
    GOOGLE_API_KEY="your-google-api-key"
    ```

## Running the Application

1. **Initialize the Reflex application:**
    ```bash
    reflex init
    ```

2. **Run the application:**
    ```bash
    reflex run
    ```
    The application will be available at `http://localhost:3000`.

*Note: If the `reflex` command is not found, you can use `python -m reflex ...` instead.*
