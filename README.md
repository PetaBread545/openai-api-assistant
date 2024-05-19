### OpenAI API Assistant Local Streamlit App - Pair Programmer

A little project implementing OpenAI API's assistant object. 

# Warnings
**Usage Costs**: This will use your OpenAI account to generate assistants, which requires an OpenAI account. Submitting messages will lead to some charges on your account, depending on how many tokens you submit, and assistants may not be available to free accounts.**

**Key Secrecy": Be careful not to expose your OpenAI API key; your OpenAI API key should remain secret!


# How To Use:
## Prerequisites
### Python Installation
If not already installed, download the latest version of [Python](https://www.python.org/downloads/) for your system.

### OpenAI API Account
Make sure you have an OpenAI API account and OpenAI API secret key (read more on that [here](https://platform.openai.com/docs/overview)).
Note that you may need to have a paid account for the assistant feature to be available to you.

## Installation
Consider setting up a virtual environment.
```
python3 -m venv venv
source venv/bin/activate  # On macOS and Linux
venv\Scripts\activate  # On Windows
```

Install the code using ```git clone https://github.com/PetaBread545/openai-api-assistant.git```

**Set up API key**
At the root level, create a `.env` file containing `OPENAI_API_KEY=<Your key here>`, where `<Your key here>` is replaced with your OpenAI API key (read more about this [here](https://platform.openai.com/api-keys))

Install dependencies with ```pip install -r requirements.txt``` or with your prefered package manager

## Running the App
Run the Streamlit App with ```streamlit run main.py``` and open the page in your browser
