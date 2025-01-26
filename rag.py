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
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from openinference.instrumentation.langchain import LangChainInstrumentor

    # Set up the tracer
    tracer_provider = TracerProvider()

    # Configure the OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://0.0.0.0:6006/v1/traces",
        headers={}  # Add any required headers here
    )

    # Add BatchSpanProcessor with the OTLP exporter
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set the tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Initialize LangChain instrumentation
    LangChainInstrumentor().instrument()

    logger.info("OpenTelemetry and LangChain instrumentation initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenTelemetry: {str(e)}", exc_info=True)
    logger.warning("Continuing without OpenTelemetry instrumentation")

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