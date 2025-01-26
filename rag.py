import os
from typing import List
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import WikipediaRetriever
from langchain.prompts import ChatPromptTemplate
import chromadb

# Import Phoenix and OpenTelemetry components
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace

# Initialize OpenTelemetry with Phoenix configuration
tracer_provider = register()
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

class RagSystem:
    def __init__(self):
        # Ensure persistence directory exists
        self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
        os.makedirs(self.persist_directory, exist_ok=True)
        self.setup_rag_pipeline()

    def setup_rag_pipeline(self):
        """Initialize the RAG pipeline components."""
        try:
            # Initialize retrievers and embeddings
            self.retriever = WikipediaRetriever()
            self.embeddings = OpenAIEmbeddings()
            self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125")

            # Configure ChromaDB client
            chroma_client = chromadb.PersistentClient(path=self.persist_directory)

            # Get Wikipedia content about Roman Empire
            docs = self.retriever.invoke("Roman Empire")

            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)

            # Create vector store with persistence
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                client=chroma_client,
                collection_name="roman_empire"
            )

            # Setup prompt template
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a knowledgeable historian specialized in the Roman Empire. 
                Use the following context to answer questions about Roman history, culture, and society.
                If you're not sure about something, admit it and stick to what's provided in the context.

                Context: {context}"""),
                ("human", "{question}")
            ])

            # Create RAG chain
            self.chain = (
                {"context": self.vectorstore.as_retriever() | self._format_docs, 
                 "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )

        except Exception as e:
            raise Exception(f"Failed to initialize RAG system: {str(e)}")

    def _format_docs(self, docs):
        """Format retrieved documents into context string."""
        return "\n\n".join(doc.page_content for doc in docs)

    def get_response(self, question: str) -> str:
        """Get response for user question using RAG pipeline."""
        try:
            response = self.chain.invoke(question)
            return response
        except Exception as e:
            raise Exception(f"Error getting response: {str(e)}")