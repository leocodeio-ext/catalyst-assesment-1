import os
import google.generativeai as genai
# import streamlit as st
from dotenv import load_dotenv
model=genai.GenerativeModel('gemini-1.5-flash')
chat=model.start_chat(history=[])
import gradio as gr
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


def extract_transcript(youtube_video_url):
    try:
        video_id = youtube_video_url.split('=')[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['de', 'en'])
        transcript = ' '.join([i['text'] for i in transcript_text])
        return transcript
    except Exception as e:
        return f"Error extracting transcript: {str(e)}"

def generate_content(video_url, prom):
    transcript_text = extract_transcript(video_url)

    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=[])

    imp = f"""The line before this is the user query or his feelings he want to express to you or he is most probably trying to talk to you.Now this is your task:Either You are an expert in summarizing youtube video.You will be taking the transcript text
    and also the user query .so you need to carefully analyze the transcript text and answer the query accordingly.
    or you are an expert who can answer any kind of questions if you are not provided with the transcript text
    The transcript text will be appended here if the user wants an answer from the video else if he wants from you he will just ask a query 
    you have to answer it in anyway.
    The user input: 
    The transcript text is append here:"""

    response = chat.send_message(str(prom)+str(imp)+str(transcript_text))
    return response

def chatbot_interface(video_url, prom):
    response = generate_content(video_url, prom)
    return response.text
# Create the Gradio interface
interface = gr.Interface(
    fn=chatbot_interface,  # Function to call
    inputs=[
        gr.Textbox(label="YouTube Video URL", placeholder="Enter the video URL"),
        gr.Textbox(label="Query Prompt", placeholder="Enter your query")
    ],  # Inputs
    outputs=[
        gr.Textbox(label="Bot Response"),  # Output for the bot's response
       
    ], 
)

# Launch the interface
interface.launch(share=True)
