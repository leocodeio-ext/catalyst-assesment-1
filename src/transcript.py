from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, VideoUnavailable

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
