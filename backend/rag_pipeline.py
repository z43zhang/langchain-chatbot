from dotenv import load_dotenv
load_dotenv()

from typing import Any, Dict, List

# Import LangChain modules
from langchain import hub # Fetching prompts templates
from langchain.chains.combine_documents import create_stuff_documents_chain # Combines docs into single prompt
from langchain.chains.history_aware_retriever import create_history_aware_retriever # Handles chat history context
from langchain.chains.retrieval import create_retrieval_chain # RAG wrapper

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

INDEX_NAME = "langchain-demo"

# Full RAG pipeline: Takes a query + chat history & Returns an answer and supporting documents
def run_llm(query: str, chat_history: List[Dict[str, Any]] = []):

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    docsearch = PineconeVectorStore(index_name=INDEX_NAME,
                                    embedding=embeddings)

    chat = ChatOpenAI(model='gpt-4o-mini',
                      verbose=True,
                      temperature=0)

    # Load prompts to rephrase follow-up questions into standalone ones
    rephrase_prompt = hub.pull("langchain-ai/chat-langchain-rephrase")
    # Load prompts for RAG answering
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat") # "Answer any user questions based solely on the context below:"

    # 1.Chat + Rephrase Prompts + docsearch
    # Wrap retriever with logic to turn chat history + follow-up query into standalone query
    history_aware_retriever = create_history_aware_retriever(
        llm=chat,
        prompt=rephrase_prompt,
        retriever=docsearch.as_retriever()
    )

    # 2.Stuff Docs + Prompt
    # Create chain to format retrieved docs + user query into a prompt and send to LLM
    stuff_documents_chain = create_stuff_documents_chain(chat,
                                                         retrieval_qa_chat_prompt)

    # 3.Combine 2 chains
    # Full RAG chain: uses history-aware retriever and document combination logic
    qa = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=stuff_documents_chain
    )

    # Run the chain with user input and chat history
    result = qa.invoke(input={"input": query,
                              "chat_history": chat_history})

    # Return both LLM answers and the source docs received
    return {
        "result": result["answer"],
        "source_documents": result["context"]  # Docs retrieved
    }