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

    tracer_provider = TracerProvider()
    phoenix_endpoint = os.environ.get("PHOENIX_ENDPOINT", "http://localhost:6006")
    otlp_exporter = OTLPSpanExporter(endpoint=f"{phoenix_endpoint}/v1/traces")
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(tracer_provider)
    LangChainInstrumentor().instrument()

    logger.info("OpenTelemetry and LangChain instrumentation initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenTelemetry: {str(e)}", exc_info=True)
    logger.warning("Continuing without OpenTelemetry instrumentation")

class RagSystem:
    def __init__(self):
        try:
            self.persist_directory = os.path.join(os.getcwd(), "chroma_db")
            os.makedirs(self.persist_directory, exist_ok=True)

            logger.info("Initializing RAG components...")

            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key is not set in environment variables")

            self.retriever = WikipediaRetriever()
            self.embeddings = OpenAIEmbeddings()
            self.llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0.7)

            chroma_client = chromadb.PersistentClient(path=self.persist_directory)

            docs = self.retriever.get_relevant_documents("Roman Empire")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)

            self.vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                client=chroma_client,
                collection_name="roman_empire"
            )

            self.prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a knowledgeable historian specialized in the Roman Empire. 
                Use the following context to answer questions about Roman history, culture, and society.
                If you're not sure about something, admit it and stick to what's provided in the context.
                Context: {context}"""),
                ("human", "{question}")
            ])

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
            raise

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_response(self, question: str) -> str:
        try:
            logger.info(f"Processing question: {question}")
            response = self.chain.invoke(question)
            logger.info("Response generated successfully")
            return response
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}", exc_info=True)
            raise