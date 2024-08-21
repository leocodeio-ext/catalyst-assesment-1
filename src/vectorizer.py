from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def vectorize_transcript(transcript):
    sentences = transcript.split('. ')
    vectors = model.encode(sentences)
    return vectors, sentences

def find_relevant_text(user_query, vectors, sentences):
    user_query_vector = model.encode([user_query])
    similarities = cosine_similarity(user_query_vector, vectors)
    best_match_idx = np.argmax(similarities)
    return sentences[best_match_idx]
