# Local LLM v3.0

# ! important features:
# 1. you don't have to upload PDF/DOC file first before chatting anymore. However, in each conversation, you can only upload one PDF/DOC file.
# 2. the file content is saved in the "context",  not in the chat history.
# 3. currently it can remember the last 5 chat history.

# ! faiss-gpu is installed by conda-forge!!!
import fitz  # PyMuPDF for extracting text from PDFs
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import requests
import json
import gradio as gr

# Global variables
file_uploaded = False
context_uploaded = False

document_chat_history = None
vectorstore = None
chat_history = []

# Available models. You can add more models here.
AVAILABLE_MODELS = ["deepseek-r1:8b", "deepseek-r1:14b"]


def extract_text_from_file(file_path):
    """Extract text from a PDF/DOC file."""
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

def create_vector_store(text, model):
    """Create a FAISS vector store from text chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # Generate embeddings using Ollama
    embeddings = OllamaEmbeddings(model=model)
    return FAISS.from_texts(chunks, embeddings)

def retrieve_relevant_chunks(query, k):
    """Retrieve top-k most relevant chunks from the vector database."""
    """20 is enough for most of the academic papers."""
    if vectorstore is None:
        return []
    return vectorstore.similarity_search(query, k=k)

def format_chat_history():
    """Formats chat history to keep the first and last 5 exchanges."""
    if len(chat_history) <= 6:
        return "\n".join([f"User: {q}\nAssistant: {a}" for q, a in chat_history])  # If small history, return all

    # first_entry = chat_history[0]  # Keep first history entry
    last_entries = chat_history[-5:]  # Keep last 5 exchanges

    return "\n".join(
        [f"User: {q}\nAssistant: {a}" for q, a in last_entries]
    )


def stream_ollama_response(prompt, context, model):
    """Stream responses from Ollama in real-time."""
    chat_memory = format_chat_history()
    global context_uploaded
    
    if context_uploaded == False:
        full_prompt = f"Chat History:\n{chat_memory}\n\nUser Query:\n{prompt}"
    else:
        full_prompt = f"Chat History:\n{chat_memory}\n\nDocument Context:\n{context}\n\nUser Query:\n{prompt}"

    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": full_prompt, "stream": True}

    response = requests.post(url, json=data, stream=True)

    for line in response.iter_lines():
        if line:
            try:
                json_data = json.loads(line.decode("utf-8"))
                word = json_data.get("response", "")
                yield word  # Send word-by-word output
            except json.JSONDecodeError:
                pass  # Ignore incomplete JSON lines

def upload_file(file, model):
    """Handles PDF upload and initializes vector store."""
    global vectorstore, file_uploaded
    if file is None:
        return "⚠ No file uploaded"

    file_text = extract_text_from_file(file.name)
    vectorstore = create_vector_store(file_text, model)  # ✅ Pass selected model
    file_uploaded = True
    return "✅ File loaded successfully!"


def chat_with_file(user_input, history, model, k):
    global file_uploaded, context_uploaded, chat_history
    
    """Handles user input, retrieves relevant context, and generates response."""
    if file_uploaded:
        relevant_chunks = retrieve_relevant_chunks(user_input, k)
        context = "\n".join([doc.page_content for doc in relevant_chunks])
        context_uploaded = True
        
    else:
        context = "the document is in the chat history."
    
    accumulated_response = ""
    
    
    for chunk in stream_ollama_response(user_input, context, model):
        # the <think> and </think> makes the output unable to be displayed in the chatbox.
        if chunk == "<think>":
            chunk = "[Think]\n "  
        elif chunk == "</think>":  
            chunk = "\n[End of think]\n"
        accumulated_response += chunk
        yield accumulated_response
        
    chat_history.append((user_input, accumulated_response))

# Gradio Interface
with gr.Blocks(fill_height=True) as demo:
    gr.Markdown("# ☝️🤓 Chat with a Local LLM!")
    
    with gr.Row():
        file_input = gr.File(label="📂 Upload File: .pdf/.doc", type="filepath")
        file_status = gr.Textbox(label="File Status", interactive=False)

    upload_button = gr.Button("📄 Load File")
    with gr.Row():
        model_dropdown = gr.Dropdown(choices=AVAILABLE_MODELS, value="deepseek-r1:14b", label="🤖 Select Model")
        k_slider = gr.Slider(minimum=1, maximum=50, value=20, step=1, label="🔍 Number of Relevant Chunks.\n(More chunks maintain more information from the document but may also include question-irrelavant information.")

    upload_button.click(upload_file, inputs=[file_input, model_dropdown], outputs=[file_status])

    # chatbox = gr.ChatInterface(fn=chat_with_file, additional_inputs=[model_dropdown], fill_height=True)
    chatbox = gr.ChatInterface(fn=chat_with_file, additional_inputs=[model_dropdown, k_slider], fill_height=True)

    
    gr.Markdown("---")
    gr.Markdown("By Yanming Xiu, Duke ECE")


# Start the UI with browser auto-launch
demo.launch(share=False, inbrowser=True)



