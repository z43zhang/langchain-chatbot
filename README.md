# 🌐 **Live Demo**: [Click here to try it out](https://zhang-chatbot.streamlit.app/)

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/main1.png)

### > **TL;DR**: A multi-turn RAG chatbot over [LangChain documentation](https://python.langchain.com/), built with GPT-4o, Pinecone, and LangChain’s modular chain framework. 


---

# 🚀 Features

* 🔍 **LangChain RAG Pipeline** — Built a Retrieval-Augmented Generation system using `HistoryAwareRetriever`, `StuffDocumentsChain`, and `RetrievalChain` from LangChain
* 🔄 **Multi-Turn Query Handling** — Rephrased follow-up questions using chat context via `chat-langchain-rephrase` prompt and `HistoryAwareRetriever`
* 🧠 **Semantic Search Index** — Embedded 2,383 text chunks with OpenAI’s `text-embedding-3-small` (1536-dim) and stored in a Pinecone index using cosine similarity
* 🗂️ **Custom Document Ingestion** — Scraped LangChain doc pages using Firecrawl API, converted to Markdown/HTML, and chunked via `RecursiveCharacterTextSplitter`
* 📈 **LangSmith Monitoring** — Traces all RAG pipeline executions with full visibility into retriever, prompt, and LLM steps
* 🔗 **Source Attribution** — Each response cites original documentation URLs used during retrieval for full transparency
* 🧬 **Deterministic Chunk IDs** — Prevented duplicate uploads using UUIDv5 generated from MD5 hashes of content
* 🤖 **Grounded Generation** — Used GPT-4o-mini to answer questions strictly based on retrieved document chunks using `retrieval-qa-chat` prompt
* 🖥️ **Interactive Chat App** — Streamlit-based UI with avatars, timestamps, real-time responses, reset functionality, and chat history download

---

# 🛠️ Tech Stack

| Layer            | Tools / Libraries                                      |
|------------------|--------------------------------------------------------|
| RAG Framework    | LangChain (`Retriever`, `Chains`, `Prompt Hub`)        |
| LLM + Embedding  | OpenAI `gpt-4o-mini`, `text-embedding-3-small`         |            
| Vector DB        | Pinecone                                               |
| Monitoring       | LangSmith                                              |
| Web Scraper      | Firecrawl API                                          |
| Chunking         | `RecursiveCharacterTextSplitter`                       |
| UUID Hashing     | `uuid`, `hashlib`                                      |
| Prompt Templates | LangChain Hub                                          |
| UI & Deployment  | Streamlit Cloud                                        |

---

# 🔬 Project Breakdown

This section follows the full life cycle: data ingestion → RAG pipeline → UI deployment.

## 1. 📥 Ingest Documentation 

The ingestion pipeline scrapes and prepares LangChain docs for semantic search:

- **Data Source**: LangChain documentation URLs
- **Crawling Tool**: `FirecrawlApp().crawl_url()`
  - Supports both Markdown and HTML output formats
- **Chunking**: 
  - Tool: `RecursiveCharacterTextSplitter`  
  - Config: `chunk_size=800`, `chunk_overlap=100`
- **UUID Hashing**: 
  - Generates deterministic chunk IDs using `uuid5(NAMESPACE_URL, MD5(content))`  
  - Prevents duplicates during repeated runs
- **Embedding**: 
  - Model: `text-embedding-3-small` (OpenAI)
  - Dimensions: 1536
- **Storage**: 
  - Vector store: `PineconeVectorStore`
  - Record Count: `2383`

> ✅ Output: A Pinecone index filled with chunked and deduplicated documentation vectors.

---

## 2. 🔧 RAG Pipeline

This module handles backend processing for user queries using LangChain’s chain API.

### 🔹 Retriever
   - Wraps Pinecone’s retriever in a `HistoryAwareRetriever`  
   - Uses the prompt `chat-langchain-rephrase` from LangChain Hub to convert follow-up queries into standalone ones

### 🔹 Document Combiner  
   - Uses `StuffDocumentsChain` with `retrieval-qa-chat` prompt  
   - Merges retrieved documents + user query → formatted prompt for LLM

### 🔹 Retrieval Chain
   - Uses `create_retrieval_chain()` to link retriever + combiner  
   - Input: `query`, `chat_history`  
   - Output: `result["answer"]`, `result["context"]`

> ✅ Output: A structured dictionary containing the final answer and source documents.

---

## 3. 💬 Streamlit App 

This is the front-end entry point that drives user interaction.

- `st.session_state` persist:
  - User inputs
  - Assistant responses
  - Chat history for multi-turn context
  - Timestamps for each message
- Captures input from `st.chat_input()`
- Records user timestamp
- Sends input to `run_llm()` (calls backend pipeline)
- Formats output:
  - Appends sources via `create_sources_string()`
  - Adds assistant timestamp
- Displays chat messages with avatars (`🧑‍💻` for user, `🤖` for assistant)
- Provides:
  - 🔄 Reset chat button (clears session state)
  - 🖨️ Download chat history as `.txt`

> ✅ Output: A live conversational UI backed by a real-time RAG pipeline with full session memory and source transparency.

---

# 🧪 Examples

## Example 1: 📌 Single-Turn Query

Shows a direct response to a single-turn question about LangChain components.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/main2.png)

### ⚙️ Under The Hood
The LangSmith view of the RAG pipeline for the question _“What is a document loader?”_. 

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/rag.png)

It shows how context is retrieved, formatted, and passed to GPT-4o-mini, along with the grounded response generated.

## Example 2: 📌 Follow-Up Understanding

The chatbot correctly rewrites and handles vague follow-up questions using history.

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/history1.png)

### ⚙️ Under The Hood
The chatbot reformulates a follow-up question using chat history, powered by LangChain's `HistoryAwareRetriever`.  

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/rewriting.png)

This screenshot above shows how the query "Give me an example" is rewritten into "Can you provide an example of a document loader?"  

It demonstrates that the system understands conversation flow, not just isolated queries.

## Example 3: 📌Source Traceability

Every response is traceable to the exact retrieved document chunk, shown here.

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/source.png)

---

# 🧑‍💻 Run Locally

```bash
git clone https://github.com/z43zhang/langchain-rag-chatbot.git
cd langchain-rag-chatbot
pipenv install 

# Add your OpenAI key, Pinecone key, and Firecrawl key to a .env file

# Ingest Documentation
pipenv run python ingest_documents.py

# Launch the App
streamlit run app.py
