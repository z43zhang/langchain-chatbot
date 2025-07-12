# 🌐 **Live Demo**: [Click here to try it out](https://zhang-chatbot.streamlit.app/)

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/main1.png)

### > **TL;DR**: A multi-turn RAG chatbot over [LangChain documentation](https://python.langchain.com/), built with GPT-4o, Pinecone, and LangChain’s modular chain framework. 


---

# 🚀 Features

* 🔍 **LangChain RAG Pipeline** — Uses `HistoryAwareRetriever`, `StuffDocumentsChain`, and `RetrievalChain` from LangChain
* 🔄 **Multi-Turn Query Handling** — Rephrases follow-ups using chat context via `chat-langchain-rephrase` and `HistoryAwareRetriever`
* 🧠 **Semantic Search Index** — Embeds 2,383 chunks with `text-embedding-3-small` (1536-dim) and stored in Pinecone
* 🗂️ **Custom Document Ingestion** — Scrapes LangChain docs via Firecrawl API and chunked via `RecursiveCharacterTextSplitter`
* 📈 **LangSmith Monitoring** — Logs retriever, prompt, and LLM steps with full RAG pipeline traces
* 🔗 **Source Attribution** — Cites original documentation URLs used for each response
* 🧬 **Deterministic Chunk IDs** — Prevents duplicate uploads using UUIDv5 + MD5 hashing of content
* 🤖 **Grounded Generation** — Uses `GPT-4o-mini` to generate answers strictly from retrieved context via `retrieval-qa-chat`
* 🖥️ **Interactive Chat App** — Streamlit UI with avatars, timestamps, real-time responses, reset, and download options

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
  - Record Count: 2383

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

These examples demonstrate how the chatbot handles single-turn queries, multi-turn conversation flow, and provides transparent source attribution — with supporting LangSmith visualizations.

## Example 1: 📌 Single-Turn Query

A question about a LangChain component.
![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/main2.png)

### ⚙️ Under The Hood

LangSmith trace for the question _“What is a document loader?”_. 

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/rag.png)

This shows how relevant context is retrieved, formatted, and passed to `gpt-4o-mini`, resulting in a grounded response.

## Example 2: 📌 Follow-Up Understanding

A vague follow-up is reinterpreted based on chat history.

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/history1.png)

### ⚙️ Under The Hood

The chatbot rewrites the query "Give me an example" into _"Can you provide an example of a document loader?"_ using `HistoryAwareRetriever`.

![App Preview](https://github.com/z43zhang/langchain-chatbot/blob/main/assets/rewriting.png)

This demonstrates that the system understands conversation flow, not just isolated prompts.

## Example 3: 📌 Source Traceability

Each answer includes links to retrieved document chunks used in generation.

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
