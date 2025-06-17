# llm-evals

This repository contains a web-based application for evaluating Large Language Models.

![image](https://github.com/user-attachments/assets/862efda7-a320-4314-8278-2d3adbd57891)

## Features

- Generate test questions on a given topic.
- Provide your own custom questions.
- Customize the evaluation prompt.
- View evaluation results and average scores.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/BurnyCoder/llm-evals.git
    cd llm-evals
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file** in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=your_api_key_here
    ```

## Usage

Run the Flask application:

```bash
python app.py
```

Open your web browser and go to `http://127.0.0.1:5000`. 
