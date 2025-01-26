import os
from typing import List
from langchain.retrievers import WikipediaRetriever
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
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
    phoenix_endpoint = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6007")
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{phoenix_endpoint}/v1/traces",
        headers={}
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
        """Initialize the RAG system with detailed error logging."""
        try:
            # Ensure persistence directory exists
            self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
            os.makedirs(self.persist_directory, exist_ok=True)

            logger.info("Initializing RAG components...")

            # Initialize OpenAI components
            logger.debug("Checking for OpenAI API key...")
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key is not set in environment variables")

            # Initialize retrievers and embeddings
            logger.info("Initializing Wikipedia retriever...")
            self.retriever = WikipediaRetriever()

            logger.info("Initializing OpenAI embeddings...")
            self.embeddings = OpenAIEmbeddings()

            logger.info("Initializing ChatOpenAI...")
            self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7)

            # Configure ChromaDB client
            logger.info("Setting up ChromaDB...")
            chroma_client = chromadb.PersistentClient(path=self.persist_directory)

            # Get Wikipedia content about Roman Empire
            logger.info("Retrieving Wikipedia content...")
            docs = self.retriever.get_relevant_documents("Roman Empire")
            logger.info(f"Retrieved {len(docs)} documents")

            # Split documents
            logger.info("Splitting documents...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)
            logger.info(f"Created {len(splits)} text splits")

            # Create vector store with persistence
            logger.info("Creating vector store...")
            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                client=chroma_client,
                collection_name="roman_empire"
            )
            logger.info("Vector store created successfully")

            # Setup prompt template
            logger.info("Setting up prompt template...")
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a knowledgeable historian specialized in the Roman Empire. 
                Use the following context to answer questions about Roman history, culture, and society.
                If you're not sure about something, admit it and stick to what's provided in the context.

                Context: {context}"""),
                ("human", "{question}")
            ])

            # Create RAG chain
            logger.info("Creating RAG chain...")
            self.chain = (
                {"context": self.vectorstore.as_retriever() | self._format_docs, 
                 "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            logger.info("RAG system initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {str(e)}", exc_info=True)
            raise Exception(f"Failed to initialize RAG system: {str(e)}")

    def _format_docs(self, docs):
        """Format retrieved documents into context string."""
        return "\n\n".join(doc.page_content for doc in docs)

    def get_response(self, question: str) -> str:
        """Get response for user question using RAG pipeline."""
        try:
            logger.info(f"Processing question: {question}")
            response = self.chain.invoke(question)
            logger.info("Response generated successfully")
            return response
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}", exc_info=True)
            raise Exception(f"Error getting response: {str(e)}")