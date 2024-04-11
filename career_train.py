import streamlit as st
import os
import pdfplumber
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

def main():
    """
    Main function for Streamlit app.
    """
    # Get Groq API key
    groq_api_key = os.environ['GROQ_API_KEY']

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('groqcloud_darkmode.png')

    # The title and greeting message of the Streamlit application
    st.title("Chat with Groq!")
    st.write("Hello! I'm your friendly Groq chatbot. I can help answer your questions, provide information, or just chat. I'm also super fast! Let's start our conversation!")

    # File uploader for resume
    uploaded_resume = st.file_uploader("Upload your resume", type=["pdf", "txt"])

    # Initialize conversation memory
    memory = ConversationBufferWindowMemory(k=5)

    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name='mixtral-8x7b-32768')
    conversation = ConversationChain(llm=groq_chat, memory=memory)

    # If the user has uploaded a resume
    if uploaded_resume is not None:
        if uploaded_resume.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_resume)
        else:
            resume_text = uploaded_resume.getvalue().decode("utf-8")

        # Use the resume text as an initial prompt for the chatbot
        response = conversation(resume_text)
        st.write("Chatbot:", response['response'])

    # Input text area for user queries
    user_question = st.text_input("Ask a question:")

    # If the user has asked a question,
    if user_question:
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        response = conversation(user_question)
        st.write("Chatbot:", response['response'])

def extract_text_from_pdf(uploaded_resume):
    """
    Function to extract text from a PDF file using pdfplumber.
    """
    text = ""
    with pdfplumber.open(uploaded_resume) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

if __name__ == "__main__":
    main()