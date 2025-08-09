# Enhanced RAGRunner with query() method for Jupyter environments

from typing import List, Dict, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import copy

from .core import Document
from .chat_models.base import BaseChatModel
from .chat_models import LocalChatModel, LocalChatConfig
from .embeddings.base import BaseEmbeddings
from .embeddings import LocalEmbeddings
from .vectors.base import BaseVectorStore
from .vectors import FAISSVectorStore
from .text_splitters import (
    TextSplitter, RecursiveCharacterTextSplitter, PythonCodeTextSplitter,
    MarkdownHeaderTextSplitter, Language
)
from .core.types import SystemMessage, HumanMessage, AIMessage, BaseMessage

@dataclass
class RAGConfig:
    """A dataclass for configuring the RAGRunner."""
    knowledge_texts: List[str] = field(default_factory=list)
    knowledge_files: List[Union[str, Path]] = field(default_factory=list)
    
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    splitter_mapping: Dict[str, TextSplitter] = field(default_factory=dict)
    
    retrieval_k: int = 3
    similarity_threshold: Optional[float] = None
    system_prompt: Optional[str] = None
    chat_model: Optional[BaseChatModel] = None
    embeddings: Optional[BaseEmbeddings] = None
    text_splitter: Optional[TextSplitter] = None
    vector_store: Optional[BaseVectorStore] = None
    debug: bool = True

class RAGRunner:
    """A professional RAG runner that handles knowledge ingestion, retrieval, and chat sessions."""
    def __init__(self, config: RAGConfig):
        self.config = config
        self.vector_store: Optional[BaseVectorStore] = None
        self.chat_model: Optional[BaseChatModel] = None
        self.default_splitter: TextSplitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap
        )
        
    def setup(self) -> 'RAGRunner':
        """Sets up all RAG components based on the configuration."""
        if self.config.debug: print("--- Setting up RAG Components ---")
        
        if self.config.text_splitter:
            self.default_splitter = self.config.text_splitter
        
        embeddings = self.config.embeddings or LocalEmbeddings()
        documents = self._prepare_documents()
        
        self.vector_store = self.config.vector_store or (
            FAISSVectorStore.from_documents(documents, embeddings) if documents
            else FAISSVectorStore(embeddings=embeddings)
        )
        
        self.chat_model = self.config.chat_model or LocalChatModel(LocalChatConfig(model="local-model"))
        
        if self.config.debug:
            num_chunks = len(self.vector_store) if self.vector_store else 0 # type: ignore
            file_count = len(self.config.knowledge_files) + len(self.config.knowledge_texts)
            print(f"✅ RAG setup complete. Ingested {file_count} source(s) into {num_chunks} document chunks.")
        
        return self
    
    def _prepare_documents(self) -> List[Document]:
        """Loads and splits documents using the file-type-aware splitter mapping."""
        all_split_docs: List[Document] = []
        source_texts: List[str] = list(self.config.knowledge_texts)
        source_metadatas: List[Dict] = [{"source_type": "text"}] * len(source_texts)

        for file_path in self.config.knowledge_files:
            file = Path(file_path)
            if not file.is_file():
                if self.config.debug: print(f"Warning: Path is not a file, skipping: {file}")
                continue
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    source_texts.append(f.read())
                    source_metadatas.append({"source": str(file), "file_extension": file.suffix})
            except Exception as e:
                print(f"Warning: Could not read file {file}: {e}")

        for i, text in enumerate(source_texts):
            metadata = source_metadatas[i]
            file_ext = metadata.get("file_extension", ".txt")
            splitter = self.config.splitter_mapping.get(file_ext, self.default_splitter)
            
            if self.config.debug:
                source_name = metadata.get('source', 'raw text')
                print(f"Splitting '{source_name}' with {splitter.__class__.__name__}...")
            
            chunks = splitter.split_text(text)
            for chunk_content in chunks:
                all_split_docs.append(Document(page_content=chunk_content, metadata=copy.deepcopy(metadata)))
            
        return all_split_docs

    def _retrieve_context(self, query: str) -> str:
        """Retrieves relevant context from the vector store."""
        if not self.vector_store: return ""
        try:
            search_results = self.vector_store.similarity_search(query, k=self.config.retrieval_k)
            return "\n\n".join([doc.page_content for doc, score in search_results])
        except Exception as e:
            if self.config.debug: print(f"[DEBUG] Error retrieving context: {e}")
            return ""
    
    # NEW METHOD: Single query for Jupyter environments
    def query(self, message: str, include_context: bool = True) -> str:
        """
        Invoke the model with a single message. Perfect for Jupyter environments.
        
        Args:
            message: The user's question or prompt
            include_context: Whether to include retrieved context (default: True)
            
        Returns:
            The model's response as a string
        """
        if not self.chat_model:
            raise RuntimeError("RAG runner not set up. Call setup() first.")
        
        # Retrieve context if requested
        context = ""
        if include_context:
            context = self._retrieve_context(message)
        
        # Prepare the enhanced message
        enhanced_message = f"Context:\n{context}\n\nQuestion: {message}" if context else message
        
        # Build message history
        messages = []
        if self.config.system_prompt:
            messages.append(SystemMessage(content=self.config.system_prompt))
        
        messages.append(HumanMessage(content=enhanced_message))
        
        # Get response from model
        try:
            # If the model supports streaming, collect all chunks
            if hasattr(self.chat_model, 'stream'):
                response_chunks = list(self.chat_model.stream(messages))
                return "".join(response_chunks)
            else:
                # Fallback for non-streaming models
                return self.chat_model.invoke(messages)
        except Exception as e:
            if self.config.debug:
                print(f"[DEBUG] Error in query: {e}")
            raise
    
    # ALTERNATIVE: Query without context retrieval
    def query_direct(self, message: str) -> str:
        """
        Query the model directly without RAG context retrieval.
        Useful for general questions that don't need document context.
        """
        return self.query(message, include_context=False)
    
    # ENHANCED: Query with custom context
    def query_with_context(self, message: str, custom_context: str) -> str:
        """
        Query the model with custom context instead of retrieved context.
        
        Args:
            message: The user's question
            custom_context: Custom context to provide to the model
        """
        if not self.chat_model:
            raise RuntimeError("RAG runner not set up. Call setup() first.")
        
        enhanced_message = f"Context:\n{custom_context}\n\nQuestion: {message}"
        
        messages = []
        if self.config.system_prompt:
            messages.append(SystemMessage(content=self.config.system_prompt))
        
        messages.append(HumanMessage(content=enhanced_message))
        
        try:
            if hasattr(self.chat_model, 'stream'):
                response_chunks = list(self.chat_model.stream(messages))
                return "".join(response_chunks)
            else:
                return self.chat_model.invoke(messages)
        except Exception as e:
            if self.config.debug:
                print(f"[DEBUG] Error in query_with_context: {e}")
            raise
    
    def run_chat(self) -> None:
        """Starts an interactive, streaming RAG-enabled chat session."""
        if not self.chat_model: raise RuntimeError("RAG runner not set up. Call setup() first.")
        
        print("\n" + "="*50); print(" Mini-Chain RAG Chat ".center(50, " ")); print("="*50)
        print("Enter your message. Type 'exit' or 'quit' to end the session.")
        
        history: List[Dict[str, str]] = []
        if self.config.system_prompt:
            history.append({"role": "system", "content": self.config.system_prompt})
        
        while True:
            try:
                user_input = input("\n[ You ] -> ")
                if user_input.lower() in ["exit", "quit"]:
                    print("\n🤖 Session ended. Goodbye!"); break
                
                context = self._retrieve_context(user_input)
                enhanced_input = f"Context:\n{context}\n\nQuestion: {user_input}" if context else user_input
                
                history.append({"role": "user", "content": enhanced_input})
                messages_for_llm = [(SystemMessage if msg["role"] == "system" else AIMessage if msg["role"] == "assistant" else HumanMessage)(content=msg["content"]) for msg in history]
                
                print("[ AI  ] -> ", end="", flush=True)
                full_response = "".join(self.chat_model.stream(messages_for_llm)) # type: ignore
                print(full_response)
                
                history.append({"role": "assistant", "content": full_response})
            except KeyboardInterrupt:
                print("\n\n🤖 Session ended. Goodbye!"); break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                if self.config.debug: import traceback; print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
                break

# Convenience functions remain the same
def create_rag_from_texts(knowledge_texts: List[str], **kwargs) -> RAGRunner:
    """Creates a RAG runner from a list of raw text strings."""
    config = RAGConfig(knowledge_texts=knowledge_texts, **kwargs)
    return RAGRunner(config).setup()

def create_rag_from_files(file_paths: List[Union[str, Path]], **kwargs) -> RAGRunner:
    """Creates a RAG runner from a list of files."""
    config = RAGConfig(knowledge_files=file_paths, **kwargs)
    return RAGRunner(config).setup()

def create_rag_from_directory(directory: Union[str, Path], file_extensions: Optional[List[str]] = None, **kwargs) -> RAGRunner:
    """Creates a RAG runner from all files in a directory with specified extensions."""
    if file_extensions is None:
        file_extensions = ['.py', '.md', '.js', '.ts', '.html', '.txt']
    directory = Path(directory)
    if not directory.is_dir(): raise ValueError(f"Not a directory: {directory}")
    
    file_paths = [p for ext in file_extensions for p in directory.rglob(f"*{ext}")]
    if kwargs.get('debug', True):
        print(f"Found {len(file_paths)} files to load from '{directory}'.")
    
    return create_rag_from_files(file_paths=file_paths, **kwargs) # type: ignore

def create_steroid_rag(knowledge_files: List[Union[str, Path]], **kwargs) -> RAGRunner:
    """Creates a RAG runner with a pre-configured, intelligent splitter mapping."""
    
    default_splitter_mapping = {
        ".py": PythonCodeTextSplitter(chunk_size=1200, chunk_overlap=120),
        ".md": MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")]),
        ".js": RecursiveCharacterTextSplitter.from_language(language=Language.JS, chunk_size=1200, chunk_overlap=120),
    }
    
    kwargs.pop('chunk_size', None)
    kwargs.pop('chunk_overlap', None)
    
    config = RAGConfig(
        knowledge_files=knowledge_files,
        splitter_mapping=default_splitter_mapping,
        **kwargs
    )
    return RAGRunner(config).setup()
