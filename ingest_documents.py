from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from firecrawl import FirecrawlApp, ScrapeOptions

from uuid import uuid5, NAMESPACE_URL

import hashlib

load_dotenv()
INDEX_NAME = "langchain-demo"

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

"""
def ingest_docs():
    loader = ReadTheDocsLoader("...")

    raw_documents = loader.load()
    print(f"Loaded {len(raw_documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    documents = text_splitter.split_documents(raw_documents)

    # Give the full url of where the document actually came
    for doc in documents:
        new_url = doc.metadata["source"]
        new_url = new_url.replace("langchain-docs", "https:/")
        doc.metadata.update({"source": new_url})

    print(f"Going to add {len(documents)} to Pinecone")

    # Take all the documents, convert them into vectors, index them in the vector store
    PineconeVectorStore.from_documents(documents,
                                       embeddings,
                                       index_name=INDEX_NAME)

    print("****Loading to vectorstore done ***")
"""

def ingest_docs2() -> None:

    langchain_documents_base_urls = [
        "https://python.langchain.com/docs/introduction/",
        "https://python.langchain.com/docs/integrations/chat/",
        "https://python.langchain.com/docs/integrations/llms/",
        "https://python.langchain.com/docs/integrations/text_embedding/",
        "https://python.langchain.com/docs/integrations/document_loaders/",
        "https://python.langchain.com/docs/integrations/document_transformers/",
        "https://python.langchain.com/docs/integrations/vectorstores/",
        "https://python.langchain.com/docs/integrations/retrievers/",
        "https://python.langchain.com/docs/integrations/tools/",
        "https://python.langchain.com/docs/integrations/stores/",
        "https://python.langchain.com/docs/integrations/llm_caching/",
        "https://python.langchain.com/docs/integrations/graphs/",
        "https://python.langchain.com/docs/integrations/memory/",
        "https://python.langchain.com/docs/integrations/callbacks/",
        "https://python.langchain.com/docs/integrations/chat_loaders/",
        "https://python.langchain.com/docs/concepts/",
        "https://python.langchain.com/docs/concepts/chat_models/"
    ]

    # langchain_documents_base_urls2 = [langchain_documents_base_urls[0]]

    for url in langchain_documents_base_urls:
        print(f"🔥 FireCrawling url='{url}'")

        app = FirecrawlApp()

        result = app.crawl_url(
            url=url,
            limit=10,
            scrape_options=ScrapeOptions(formats=['markdown', 'html'])
        )

        pages = result.data or []

        docs = [
            Document(
                page_content=page.markdown or page.html or "",
                metadata={"source": page.metadata.get("sourceURL", url)}
            )
            for page in pages if (page.markdown or page.html)
        ]

        print(f"📄 Got {len(docs)} documents")

        # Split each doc into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        split_docs = text_splitter.split_documents(docs)

        print(f"🔎 Split into {len(split_docs)} chunks")

        # Generate consistent IDs based on source and chunk index
        def generate_id(doc):
            content_hash = hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()
            return str(uuid5(NAMESPACE_URL, f"{doc.metadata['source']}#{content_hash}"))

        ids = [generate_id(doc) for doc in split_docs]

        texts = [doc.page_content for doc in split_docs]
        metadatas = [doc.metadata for doc in split_docs]

        PineconeVectorStore.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            ids=ids,
            index_name=INDEX_NAME
        )

        print(f"✅ Uploaded {len(split_docs)} chunks for: {url}\n")

        # print("Sample IDs:", ids[:5])


if __name__ == "__main__":
    ingest_docs2()