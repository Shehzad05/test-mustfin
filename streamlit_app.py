import streamlit as st
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Pinecone
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import os

# Set your OpenAI API key and Pinecone API key here
os.environ["OPENAI_API_KEY"] = "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"
pinecone.init(api_key='47c87c2b-d5fe-4df0-ae0e-2514cccb1cdb', environment='gcp-starter')

llm = OpenAI()
embeddings = OpenAIEmbeddings()

index_name = "mustfinetech"
docsearch = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that don't know but in future i will be give you best awnswer, don't try to make up an answer.\n\n{context}\n\nQuestion: {question}\nAnswer in short summary:"""
# prompt_template = """Use the following pieces of context to answer the question at 
# the end. If you don't know the answer, just say that don't know but in future i will be give you best 
# awnswer, don't try to make up an answer.\n\n{context}\n\nQuestion: {question}\nAnswer in comma separated 
# values with index number:"""
prompt_template = """detect user language and response in detected languge use the following pieces of context to answer the question at the end.if you don't know the answer just say that 
i don't know but in the future i will be give you best anwser,

{context}
Question {question}
Anwser in user languages remove all extra words like ** and # [] \n \n- [x],also anwsers in its language
"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

chain_type_kwargs = {"prompt": PROMPT}
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever(), memory=memory, chain_type_kwargs=chain_type_kwargs)

# Initialize conversation history and user input
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Emojis for styling
user_emoji = "💁‍♂️"
bot_emoji = "🤖"
new_chat_emoji = "🔄"
clear_chat_emoji = "🧹"

def main():
    st.title("RealState Chatbot (MustFinTech-Demo)")
    
    # Set page-wide styling
    st.markdown(
        """
        <style>
        body {
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
            padding: 0;
            margin: 0;
        }
        .header {
            background-color: #87CEFA;
            color: white;
            padding: 10px;
            border-radius: 4px 4px 0 0;
        }
        .footer {
            background-color: #f0f0f0;
            padding: 10px;
            border-top: 1px solid #ccc;
            text-align: center;
            border-radius: 0 0 4px 4px;
        }
        .chat-container {
            padding: 20px;
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            height: 400px;
            overflow-y: scroll;
        }
        .user {
            text-align: left;
            color: #007bff;
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 8px;
            margin: 5px;
        }
        .bot {
            text-align: right;
            color: #28a745;
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 8px;
            margin: 5px;
        }
        .input-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 20px;
        }
        .sidebar {
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 4px;
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .sidebar-header {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .sidebar-item {
            display: flex;
            align-items: center;
            margin-top: 10px;
            cursor: pointer;
        }
        .sidebar-item:hover {
            color: #007bff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display header with logo
    st.sidebar.markdown('<div class="sidebar-header">Well Come To</div>', unsafe_allow_html=True)
    st.sidebar.image("logo.png", width=200)
    # Display footer
   
    if st.sidebar.button(f"{new_chat_emoji} New Chat"):
        st.session_state.conversation = []
        st.session_state.user_input = ""  # Clear user input
    if st.sidebar.button(f"{clear_chat_emoji} Clear Chat"):
        st.session_state.conversation = []
    about_us_url = "https://www.mufin.co.kr/"
    st.sidebar.markdown(f'<div class="sidebar-footer"><a href="{about_us_url}" target="_blank">Contact US</a></div>', unsafe_allow_html=True)
    # Chat container
    with st.container():
        # Display previous chat history
        for message in st.session_state.conversation:
            if message["role"] == "user":
                st.markdown(f"{user_emoji} **You:**", unsafe_allow_html=True)
                st.markdown(f'<div class="user">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"{bot_emoji} **Bot:**", unsafe_allow_html=True)
                st.markdown(f'<div class="bot">{message["content"]}</div>', unsafe_allow_html=True)

        # User input and button
        user_input = st.text_input("You:", value=st.session_state.user_input)
        input_button = st.button("Send")
        # Process user input
        if input_button and user_input:
            try:
                response = qa.run(user_input)  # Use the user input as the query
                bot_response_parts = response.strip().split(",")
                
                # Add user input and bot response to the conversation history
                st.session_state.conversation.append({"role": "user", "content": user_input})
                st.session_state.conversation.append({"role": "bot", "content": response})
                
                st.session_state.user_input = ""  # Clear user input after processing
                
            except pinecone.exceptions.PineconeException as e:
                error_message = "Thanks You For Coming Please contact with Our Help Desk Team."
                # st.session_state.conversation.append({"role": "user", "content": user_input})
                # st.session_state.conversation.append({"role": "bot", "content": error_message})
                st.session_state.user_input = ""  # Clear user input after processing


    # Display footer
    # st.markdown('<div class="footer">About Us</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
