from dotenv import load_dotenv
import openai
import time
import os
from init import create_assistant_and_thread
import streamlit as st
import json

load_dotenv()

client = openai.OpenAI()

model = "gpt-4-1106-preview"

# Initialize all the session
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

assis_id, thread_id = create_assistant_and_thread()

assistants_file = 'assistants.json'


# Set up our front end page
st.set_page_config(page_title="Pair Programmer - Your Helpful Programming Assistant", page_icon=":books:")


##################################################
###            Function Definitions            ###
##################################################
def upload_file(filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file.read(), purpose="assistants")
    return response.id


# Sidehbar to upload files
file_uploaded = st.sidebar.file_uploader(
    "Upload a file to begin!", key="file_upload"
)

# Upload file button - store the file ID
if st.sidebar.button("Upload File"):
    # Uploading a file
    if file_uploaded:
        with open(file_uploaded.name, "wb") as f:
            f.write(file_uploaded.getbuffer())
        
        # Upload to OpenAI
        another_file_id = upload_file(file_uploaded.name)
        # Store in session state
        st.session_state.file_id_list.append(another_file_id)
        # Load the existing data and then write the updated data back to the file
        data = {"file_id_list": []}  # Default data in case the file doesn't exist
        if os.path.isfile(assistants_file):
            with open(assistants_file, 'r') as f:
                data = json.load(f)  # Load existing data from json file
        data["file_id_list"].append(another_file_id) # Add to data
        with open(assistants_file, 'w') as f:
            json.dump(data, f, indent=4)  # Write the updated data back to the file
    
if os.path.isfile(assistants_file):
    # Read the current list of file IDs from the JSON file
    with open(assistants_file, 'r') as f:
        data = json.load(f)
        file_id_list = data.get("file_id_list", [])  # Get the list of file IDs
    # Display the file IDs using Streamlit's sidebar
    st.sidebar.write("Uploaded File IDs:")
    for file_id in file_id_list:
        st.sidebar.text(file_id)
        client.beta.assistants.files.create(assistant_id=assis_id, file_id=file_id)
        # File delete button
        if st.sidebar.button(f"DELETE {file_id}", key=file_id):
            # Delete the file in the assistant file system
            client.beta.assistants.files.delete(assistant_id=assis_id, file_id=file_id)
            # Remove from session state
            if file_id in st.session_state.file_id_list:
                st.session_state.file_id_list.remove(file_id)
            # Remove from JSON file
            data["file_id_list"].remove(file_id)
            # Write the updated data back to the JSON file
            with open(assistants_file, 'w') as f:
                json.dump(data, f, indent=4)
            # Use Streamlit's success message to communicate the deletion
            st.success(f'Removed file: {file_id}')
            # Rerun the script to update UI
            st.rerun()

# Button to initiate the chat session
if st.sidebar.button("Start Chatting..."):
    with open(assistants_file, 'r') as f:
        data = json.load(f)
        file_id_list = data.get("file_id_list", [])  # Get the list of file IDs
    if file_id_list:
        st.session_state.start_chat = True
        # Create a new thread for this chat session
        chat_thread = client.beta.threads.create()
        st.session_state.thread_id = chat_thread.id
        st.write("Thread ID:", chat_thread.id)
    else:
        st.sidebar.warning(
            "No files found. Please upload at least one file to get started."
        )


# Process messages - extract message content
def process_message(message):
    message_content = message.content[0].text
    annotations = (
        message_content.annotations if hasattr(message_content, "annotations") else []
    )

    # Iterate over the annotations and add footnotes
    for index, annotation in enumerate(annotations):
        # Replace the text with a footnote
        message_content.value = message_content.value.replace(
            annotation.text, f" [{index + 1}]"
        )

    # Add footnotes to the end of the message content
    full_response = message_content.value
    return full_response

st.title("Pair Programmer")
st.write("Talk it out with a trained robot programmer!")


# Check sessions
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-4-1106-preview"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show existing messages if any
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat input for the user
    if prompt := st.chat_input("What's new?"):
        # Add user message to the state and display on the screen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # add the user's message to the existing thread
        client.beta.threads.messages.create( 
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )

        # Create a run
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assis_id,
        )

        # Show a spinner while the assistant is thinking
        with st.spinner("Please wait... Generating response..."):
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )
            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            # Process and display assistant messages
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            for message in reversed(assistant_messages_for_run):
                full_response = process_message(message=message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)

    else:
        # Prompt users to start chat
        st.write(
            "Please upload at least a file to get started by clicking on the 'Start Chat' button"
        )
