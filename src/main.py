import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable
import re

# List to store history of queries and responses
history = []

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except VideoUnavailable:
        return "Error: The video is unavailable."
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except Exception as e:
        return f"Error retrieving transcript: {str(e)}"

def get_video_id(url):
    # Regular expressions for extracting video ID
    patterns = [
        r"youtube\.com\/shorts\/([a-zA-Z0-9_-]+)",
        r"youtu\.be\/([a-zA-Z0-9_-]+)",
        r"youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return "Error: Invalid YouTube URL"

def process_query(youtube_url, user_query):
    video_id = get_video_id(youtube_url)
    if "Error" in video_id:
        result = video_id
    else:
        transcript = get_transcript(video_id)
        result = f"Transcript: {transcript}\n\nUser Query: {user_query}"
    
    # Store the URL, user query, and response in history
    history.append({"URL": youtube_url, "Query": user_query, "Response": result})
    
    return result

def get_history():
    # Format history for display
    formatted_history = "\n\n".join([
        f"URL: {entry['URL']}\nQuery: {entry['Query']}\nResponse: {entry['Response']}" 
        for entry in history
    ])
    return formatted_history if formatted_history else "No history available."

# Create Gradio interface
with gr.Blocks() as iface:
    with gr.Row():
        with gr.Column():
            url_input = gr.Textbox(label="Enter YouTube URL", placeholder="Enter the YouTube video URL here...", lines=1)
            query_input = gr.Textbox(label="Enter Your Question", placeholder="Enter your question here...", lines=1)
        with gr.Column():
            submit_button = gr.Button("Submit")
    
    with gr.Row():
        output = gr.Textbox(label="Response", lines=10)

    with gr.Row():
        history_output = gr.Textbox(label="History", lines=20)
        # Adjust the button to fit the text and move it here
        history_button = gr.Button("Show History", size="small")  
    
    # Submit both URL and question
    submit_button.click(process_query, inputs=[url_input, query_input], outputs=output)
    history_button.click(get_history, outputs=history_output)

iface.launch(share=True, debug=True)
