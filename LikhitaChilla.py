import os
import google.generativeai as genai
import streamlit as st
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

model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

imp=''''Till now you read a user query.Now this is your task:You are an expert in summarizing youtube video.You will be taking the transcript text
and also the user query .so you need to carefully analyze the transcript text and answer the query accordingly.
The transcript text will be appended here:'''
def extract_transcript(youtube_video_url):
    try:
        video_id = youtube_video_url.split('=')[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['de', 'en'])
        transcript = ' '.join([i['text'] for i in transcript_text])
        return transcript
    except Exception as e:
        return f"Error extracting transcript: {str(e)}"

def generate_content(video_url, prom,imp):
    transcript_text = extract_transcript(video_url)
    response = chat.send_message(str(prom)+str(imp)+str(transcript_text))
    return response

def chatbot_interface(video_url, prom):
    response = generate_content(video_url, prom,imp)
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
interface.launch()
