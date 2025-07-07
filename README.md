# 🌐 **Live Demo**: [Click here to try it out](https://zhang-chatbot.streamlit.app/)

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/main1.png)

### 📒 A RAG-Powered chatbot that answers questions about [LangChain's official documentation](https://python.langchain.com/). 

---

# 🚀 Features

* 🔍 **LangChain RAG Pipeline** — Built a Retrieval-Augmented Generation system using `HistoryAwareRetriever`, `StuffDocumentsChain`, and `RetrievalChain` from LangChain
* 🗂️ **Custom Document Ingestion** — Scraped LangChain doc pages using Firecrawl API, converted to Markdown/HTML, and chunked via `RecursiveCharacterTextSplitter`
* 🧠 **Semantic Search Index** — Embedded 2,383 text chunks with OpenAI’s `text-embedding-3-small` (1536-dim) and stored in a Pinecone index using cosine similarity
* 🧬 **Deterministic Chunk IDs** — Prevented duplicate uploads using UUIDv5 generated from MD5 hashes of content
* 🔄 **Multi-Turn Query Handling** — Rephrased follow-up questions using chat context via `chat-langchain-rephrase` prompt and `HistoryAwareRetriever`
* 🤖 **Grounded Generation** — Used GPT-4o-mini to answer questions strictly based on retrieved document chunks using `retrieval-qa-chat` prompt
* 🖥️ **Interactive Chat App** — Streamlit-based UI with avatars, timestamps, real-time responses, reset functionality, and chat history download
* 🔗 **Source Attribution** — Each response cites original documentation URLs used during retrieval for full transparency

---

# 🛠️ Tech Stack

| Layer            | Tools / Libraries                                      |
|------------------|--------------------------------------------------------|
| RAG Framework    | LangChain (Retriever, Chains, Prompt Hub)              |
| LLM              | OpenAI `gpt-4o-mini`                                   |
| Embeddings       | OpenAI `text-embedding-3-small`                        |
| Vector Store     | Pinecone                                               |
| Web Crawling     | Firecrawl API                                          |
| Chunking         | `RecursiveCharacterTextSplitter`                       |
| UUID Hashing     | `uuid`, `hashlib`                                      |
| Prompt Templates | LangChain Hub                                          |
| Chat Memory      | `st.session.state`                                     |
| UI               | Streamlit                                              |

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

## Example 1: Single-Turn Query

### A direct question about LangChain’s integrations with a clear, grounded answer.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/main2.png)

### The view of the RAG pipeline execution for the question _“What is a document loader?”_. 
### It shows how context is retrieved, formatted, and passed to GPT-4o-mini, along with the grounded response generated.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/rag.png)


## Example 2: Multi-Turn Follow-Up

A follow-up question relying on previous context, demonstrating the chatbot's memory function.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/history1.png)

### The chatbot reformulates a follow-up question using chat history, powered by LangChain's `HistoryAwareRetriever`.  
### This screenshot shows how the query "Give me an example" is rewritten into "Can you provide an example of a document loader?"  
### It demonstrates that the system understands conversation flow, not just isolated queries.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/rewriting.png)


## Example 3: Source Verification

The original documentation chunk retrieved and used to generate the answer, verifying output traceability.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/source.png)



