import gradio as gr
from transcript import get_transcript
from vectorizer import vectorize_transcript, find_relevant_text
from response_generator import generate_response
import re

# History storage
history = []

def add_to_history(youtube_link, user_query):
    history.append({
        'youtube_link': youtube_link,
        'user_query': user_query
    })

def get_history():
    formatted_history = ""
    for entry in history:
        formatted_history += f"URL: {entry['youtube_link']}\nQuery: {entry['user_query']}\n\n"
    return formatted_history

def extract_video_id(youtube_link):
    match = re.search(r'v=([^&]+)', youtube_link)
    return match.group(1) if match else ''

def respond_to_query(youtube_link, user_query):
    video_id = extract_video_id(youtube_link)
    if not video_id:
        return "Invalid YouTube link. Please provide a valid link."

    try:
        transcript = get_transcript(video_id)
        vectors, sentences = vectorize_transcript(transcript)
        relevant_text = find_relevant_text(user_query, vectors, sentences)
        response = generate_response(relevant_text, user_query)

        # Log the URL and query in history
        add_to_history(youtube_link, user_query)

        return response
    except Exception as e:
        return str(e)

def show_history():
    return get_history()

# Create Gradio interface with Blocks API
with gr.Blocks() as demo:
    with gr.Row():
        youtube_link = gr.Textbox(label="YouTube Link")
        user_query = gr.Textbox(label="Got any Query")
        submit_button = gr.Button("Submit")
        response_output = gr.Textbox(label="Response")

    with gr.Row():
        history_button = gr.Button("Show History")
        history_output = gr.Textbox(label="History", interactive=True)

    # Bind the functions to the buttons
    submit_button.click(fn=respond_to_query, inputs=[youtube_link, user_query], outputs=response_output)
    history_button.click(fn=show_history, outputs=history_output)

# Launch the Gradio interface
demo.launch(share=True, debug=True)
