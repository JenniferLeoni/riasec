import streamlit as st
from llama_index.llms.ollama import Ollama
from pathlib import Path
import qdrant_client
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings, PromptTemplate
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding

from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer

from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes, get_root_nodes
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.chat_engine import CondensePlusContextChatEngine

import pandas as pd


class Chatbot:
    def __init__(self, llm="llama3.1:latest", embedding_model="intfloat/multilingual-e5-large", vector_store=None):
        self.Settings = self.set_setting(llm, embedding_model)

        # Indexing
        self.index = self.load_data()

        # Memory
        self.memory = self.create_memory()

        # Chat Engine
        self.chat_engine = self.create_chat_engine(self.index)

        # Load RIASEC results
        self.riasec_results = self.load_riasec_results()

    def load_riasec_results(self):
        try:
            df = pd.read_csv('docs/riasec_scores.csv')
            results = df.set_index('Type').to_dict()['Score']
            return results
        except FileNotFoundError:
            return None

    def set_setting(self, llm, embedding_model):
        Settings.llm = Ollama(model=llm, base_url="http://127.0.0.1:11434")
        Settings.embed_model = FastEmbedEmbedding(
            model_name=embedding_model, cache_dir="./fastembed_cache")
        Settings.system_prompt = """
                                You are an expert career advisor focused on the RIASEC personality test.
                                Your job is to assist users in finding suitable careers based on their RIASEC personality types (Realistic, Investigative, Artistic, Social, Enterprising, and Conventional).
                                If you don't know the answer, say 'I DON'T KNOW'.
                                """
        return Settings

    @st.cache_resource(show_spinner=False)
    def load_data(_self, vector_store=None):  # Renamed 'self' to '_self'
        with st.spinner(text="Loading and indexing – hang tight! This should take a few minutes."):
            # Read & load document from folder
            reader = SimpleDirectoryReader(input_dir="./docs", recursive=True)
            documents = reader.load_data()

        if vector_store is None:
            index = VectorStoreIndex.from_documents(documents)
        return index

    def set_chat_history(self, messages):
        self.chat_history = [ChatMessage(role=message["role"], content=message["content"]) for message in messages]
        self.chat_store.store = {"chat_history": self.chat_history}

    def create_memory(self):
        self.chat_store = SimpleChatStore()
        return ChatMemoryBuffer.from_defaults(chat_store=self.chat_store, chat_store_key="chat_history", token_limit=16000)

    def create_chat_engine(self, index):
        return CondensePlusContextChatEngine(
            verbose=True,
            memory=self.memory,
            retriever=index.as_retriever(),
            llm=Settings.llm,
            system_prompt=Settings.system_prompt,
            context_prompt=(
                "You are an expert career advisor guiding users based on RIASEC personality types. "
                "Use the RIASEC scores from the CSV file to assist users in selecting careers. "
                "If no score is available, guide the user to take the test. \n\n{context_str}"
                "If no score and no test and the user stated their RIASEC personality type, save their type, assist users in selecting careers based on their type."
            ),
            condense_prompt="""
                Given the conversation (between User and Assistant) and a follow-up message from the User, 
                transform the follow-up into an independent question that includes all relevant context from the previous chat history. 
                Keep the question short. Example: "What is the best career for someone with an Artistic score?" 
                
                <Chat History>
                {chat_history}
                
                <Follow Up Message>
                {question}
                
                <Standalone question>"""
        )

    def generate_personalized_response(self, prompt):
        if self.riasec_results:
            riasec_info = f"Your RIASEC type scores are: {self.riasec_results}."
        else:
            riasec_info = "What is your RIASEC type? Have you known or do you need to take the test?"

        combined_prompt = f"{riasec_info}\n\n{prompt}"
        response = self.chat_engine.chat(combined_prompt)
        return response.response


# Main Program
st.title("Simple RAG Chatbot for RIASEC Career Plan with Streamlit")
chatbot = Chatbot()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Hello there 👋!\n\n Good to see you, how may I help you today? Have you taken your RIASEC test? What is your personality? Feel free to ask me 😁 \n\n ps. If you haven't there's a test here you can do in the RIASEC assessment tab :) "}
    ]

# Initialize the chat engine
if "chat_engine" not in st.session_state.keys():
    init_history = [
        ChatMessage(role=MessageRole.ASSISTANT, content="Hello there 👋! How can I assist you today?")
    ]
    memory = ChatMemoryBuffer.from_defaults(token_limit=16000)
    st.session_state.chat_engine = CondensePlusContextChatEngine(
        verbose=True,
        memory=memory,
        system_prompt=Settings.system_prompt,
        retriever=chatbot.index.as_retriever(),
        llm=Settings.llm
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

chatbot.set_chat_history(st.session_state.messages)

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = chatbot.generate_personalized_response(prompt)
        st.markdown(response)

    # Add assistant message to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
