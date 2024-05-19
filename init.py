import os
from dotenv import load_dotenv
import openai
import json

load_dotenv()

client = openai.OpenAI()

model = "gpt-4-1106-preview" 
assistants_file = 'assistants.json'

def create_assistant_and_thread():
    # If assistants.json already exists
    if os.path.isfile(assistants_file):
        with open(assistants_file, 'r') as f:
            data = json.load(f)
            # Extract assistant and thread IDs
            return data['assis_id'], data['thread_id']
        
    # Otherwise, create the assistant and thread
    assistant = client.beta.assistants.create(
        name="Pair Programmer",
        instructions="""You are a helpful programming assistant who knows a lot about coding, specifically in Python.
        Your role is to work with the user to debug, optimize, and otherwise develop the code the present to you.
        Ignore the first file that is already in the system, that is just used for initializiation. 
        Cross-reference information, including different known frameworks and libraries, to provide accurate and helpful information.
        Consider different coding principles and implementation options, suggesting when an alternative approach may be better.
        Respond to queries effectively, incorporating feedback to enhance your accuracy.
        Handle data securely and update your knowledge base with the latest research.
        Be aware of the absence of information in regard to the greater codebase.
        Maintain a feedback loop for continuous improvement and user support.""",
        tools=[{"type": "code_interpreter"}],
        model=model,
        file_ids=[],
    )
    thread = client.beta.threads.create()

    # Store IDs in json 
    with open(assistants_file, 'w') as f:
        json.dump({'assis_id': assistant.id, 'thread_id': thread.id, 'file_id_list':[]}, f)
    return assistant.id, thread.id

assis_id, thread_id = "", ""
# Load IDs into vars
if os.path.isfile(assistants_file):
    with open(assistants_file, 'r') as f:
        data = json.load(f)
        assis_id = data['assis_id'],
        thread_id = data['thread_id']