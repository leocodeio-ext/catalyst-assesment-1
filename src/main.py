import gradio as gr
from transcript import get_transcript
from vectorizer import vectorize_transcript, find_relevant_text
from response_generator import generate_response
import re

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
        return response
    except Exception as e:
        return str(e)

iface = gr.Interface(
    fn=respond_to_query,
    inputs=[gr.Textbox(label="YouTube Link"), gr.Textbox(label="Got any Query")],
    outputs="text"
)

iface.launch()
