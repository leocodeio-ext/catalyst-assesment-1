import requests
from dotenv import load_dotenv
import os
from langchain import LLMChain, PromptTemplate
from langchain.llms import HuggingFaceInference
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

#try running it, i can't see the terminal
load_dotenv()

gemini_api_key = os.getenv('gemini_api_key')

def generate_response(relevant_text, user_query):
    # context = f"{relevant_text}\n\nUser Query: {user_query}"

    # llm = HuggingFaceInference(model_id="hf_transformers/google/flan-t5-xxl", api_key=gemini_api_key)#whatdid u do here??

    llm = ChatGoogleGenerativeAI(
        temperature=0.6,
        google_api_key=gemini_api_key,
        model='gemini-1.5-flash',
        max_output_tokens=2048,
        verbose=True,
    )

    prompt_template = PromptTemplate(
        input_variables=["context", "query"],
        template=f"context: {relevant_text}\n\nQuestion: {user_query}"
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt_template)

    response = llm_chain.run(context=relevant_text, query=user_query)

    return response
