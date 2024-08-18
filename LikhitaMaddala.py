import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api.formatters import TextFormatter
from sentence_transformers import SentenceTransformer, util
import moviepy.editor as mp
import speech_recognition as sr
import nltk
import requests
nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
from bs4 import BeautifulSoup

def extract_video_id(url):
    try:
        if "v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        else:
            return None
    except IndexError:
        return None
    
def download_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)
    except TranscriptsDisabled:
        return None

def extract_audio_from_video(video_url):
    video = mp.VideoFileClip(video_url)
    audio_file = "audio.wav"
    video.audio.write_audiofile(audio_file)
    return audio_file


def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)

def preprocess_text(text):
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stopwords.words('english') and word not in string.punctuation]
    return tokens

def find_best_answer(transcript, question):
    transcript_sentences = transcript.split('.')
    question_embedding = model.encode(question)
    transcript_embeddings = model.encode(transcript_sentences)

    # Find the most similar sentence to the question
    similarities = util.cos_sim(question_embedding, transcript_embeddings)
    best_match_idx = similarities.argmax()

    # Increase context by including more sentences around the best match
    context_length = 5  # Increase the number of additional sentences to include
    start_idx = max(best_match_idx - context_length, 0)  # Start a few sentences before the best match
    end_idx = min(best_match_idx + context_length + 1, len(transcript_sentences))  # Include a few sentences after

    extended_answer = ". ".join(transcript_sentences[start_idx:end_idx]).strip()

    # Ensure the answer ends with a period
    if not extended_answer.endswith('.'):
        extended_answer += '.'

    return extended_answer

def web_search(query):
    api_key = "AIzaSyCQRsDmbO-3yhM_ud_a9pSchfZUWhXLDCw"  
    search_engine_id = "430a7912cc7f041a8"  
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()
        
        if "items" in results and len(results["items"]) > 0:
            for item in results["items"]:
                link = item.get("link")
                snippet = fetch_full_content(link)
                if snippet:
                    return snippet
            return "I couldn't find any detailed information from the web that directly answers your question."
        else:
            return "I couldn't find any relevant information on the web."
    
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return "There was an issue with the web search."

    except KeyError as e:
        print("KeyError:", e)
        return "There was an issue processing the web search results."

    except Exception as e:
        print("An unexpected error occurred:", e)
        return "An unexpected error occurred during the web search."


def fetch_full_content(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Extract main content (this might vary depending on the website structure)
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs if para.get_text()])
        
        # Filter out irrelevant content (e.g., dates, unrelated snippets)
        content = ' '.join(content.split())
        
        # Check if the content is long enough and meaningful
        if len(content) > 200:  # Arbitrary threshold for meaningful content
            return content
        return None

    except Exception as e:
        print("An error occurred while fetching content:", e)
        return None
    
def generate_response(transcript, question):
    best_sentence = find_best_answer(transcript, question)
    
    web_answer = web_search(question)

    if best_sentence:
        answer = f"Based on the video, here's what I found: {best_sentence}."
        
        answer = answer.strip()
        answer = answer.replace("..", ".")
        if not answer.endswith('.'):
            answer += '.'
        
        return answer
    else:
        # If no match in the video, return the web search result
        return f"I couldn't find an exact match in the video, but here's what I found on the web: {web_answer}"

chat_history = []  # Define chat_history at the top

def chatbot(video_url, question):
    try:
        print("Received video URL:", video_url)  # Debugging: print video URL
        video_id = extract_video_id(video_url)
        if not video_id:
            return "Error: Could not extract video ID from the URL.", gr.update(visible=False), gr.update(visible=False)

        print("Extracted video ID:", video_id)  # Debugging: print video ID
        transcript = download_transcript(video_id)
        if not transcript:
            print("Transcript not found, attempting audio transcription.")  # Debugging
            audio_file = extract_audio_from_video(video_url)
            transcript = transcribe_audio(audio_file)
            if not transcript:
                return "Error: Could not retrieve or transcribe the video.", gr.update(visible=False), gr.update(visible=False)

        print("Transcript retrieved.")  # Debugging: indicate that transcript is retrieved
        response = generate_response(transcript, question)
        chat_history.append({"User": question, "Bot": response})

        return response, gr.update(visible=True), gr.update(visible=True)
    except IndexError as e:
        print(f"IndexError: {str(e)}")  # Debugging: print IndexError
        return f"Error: {str(e)}. Likely caused by out-of-bound indices.", gr.update(visible=False), gr.update(visible=False)
    except Exception as e:
        print(f"An error occurred: {str(e)}")  # Debugging: print general error
        return f"An error occurred: {str(e)}", gr.update(visible=False), gr.update(visible(False))

def another_question_on_same_video(video_url):
    return gr.update(value="", visible=True), gr.update(visible=True), gr.update(visible=True)

def another_video():
    return gr.update(value="", visible=True), gr.update(value="", visible=True), gr.update(visible=False)

def show_chat_history():
    if chat_history:
        history = "\n\n".join([f"User: {entry['User']}\nBot: {entry['Bot']}" for entry in chat_history])
        return gr.update(value=history, visible=True)  
    else:
        return gr.update(value="No chat history available.", visible=True)  

iface = gr.Blocks()

with iface:
    with gr.Row():
        video_url = gr.Textbox(label="YouTube Video URL")
        question = gr.Textbox(label="Your Question")
    with gr.Row():
        answer = gr.Textbox(label="Answer")
    with gr.Row():
        btn_another_question = gr.Button("Another question on the same video?", visible=False)
        btn_another_video = gr.Button("Another video?", visible=False)
        btn_show_history = gr.Button("Show Chat History")
        history_output = gr.Textbox(label="Chat History", visible=False)
    
    btn_another_question.click(another_question_on_same_video, inputs=video_url, outputs=[question, btn_another_question, btn_another_video])
    btn_another_video.click(another_video, inputs=[], outputs=[video_url, question, btn_another_question])
    btn_show_history.click(show_chat_history, inputs=[], outputs=history_output)
    
    submit = gr.Button("Submit")
    submit.click(chatbot, inputs=[video_url, question], outputs=[answer, btn_another_question, btn_another_video])

iface.launch()




