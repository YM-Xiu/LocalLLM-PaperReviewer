# LocalLLM-PaperReviewer

A Local LLM-Powered Paper Reviewing Assistant

## 📌 Overview

LocalLLM-PaperReviewer is a lightweight, privacy-friendly tool that utilizes a local large language model (LLM) to assist with academic paper reviews. It enables researchers to analyze, summarize, and critique papers efficiently without relying on cloud-based AI services.

## ✨ Features

✅ Runs Locally – No internet required, ensuring data privacy;

✅ File Upload Support – Upload research papers in pdf/doc format for context-aware analysis;

✅ Adaptive Reviewing – Customize the number of relevant document chunks for better context;

✅ Multi-Turn Conversations – Keeps track of previous discussions for coherent feedback;

✅ Custom Model Selection – Choose between different LLMs, like deepseek-r1:8b.


## 🔧 Setup

Install ollama at [Ollama Official Website](https://ollama.com/);

Open a command prompt, deploy the models you want. For example, with deepseekr1-14b:
```markdown
ollama pull deepseekr1-14b
```


Clone the repo:
```markdown
git clone https://github.com/YM-Xiu/LocalLLM-PaperReviewer.git
```

Create python environment with Anaconda: (assume you already have anaconda and pip ready)
```markdown
conda create -n localllm python=3.10
```

Install the dependencies: (for different devices, use the faiss version that suits your device)
```markdown
pip install langchain requests gradio fitz frontend pymupdf langchain_ollama langchain_community
conda install -c conda-forge faiss-gpu / conda install -c conda-forge faiss-cpu
```

Then, get into the repo folder:
```markdown
cd LocalLLM-PaperReviewer
python localllm.py
```

Before running the code, you may (and may not) need to activate the ollama service in the command prompt:
```markdown
ollama serve
```

