# src/minichain/rag_runner.py
"""
Provides a professional, configurable RAG (Retrieval-Augmented Generation) runner.
This version is backward-compatible and supports intelligent, file-type-aware splitting.
"""
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
    
    # --- FIX: Restore chunk_size/overlap for backward compatibility ---
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # --- ENHANCEMENT: Add splitter_mapping for advanced use ---
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
        
        # Allow user to override the default splitter
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

# ==============================================================================
# 3. High-Level Convenience Functions
# ==============================================================================

# --- FIX: This is the function you were missing. Now restored. ---
def create_rag_from_texts(knowledge_texts: List[str], **kwargs) -> RAGRunner:
    """Creates a RAG runner from a list of raw text strings."""
    config = RAGConfig(knowledge_texts=knowledge_texts, **kwargs)
    return RAGRunner(config).setup()

# --- FIX: This function was also missing. Now restored. ---
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
    
    # Now uses the restored `create_rag_from_files`
    return create_rag_from_files(file_paths=file_paths, **kwargs) # type: ignore

def create_steroid_rag(knowledge_files: List[Union[str, Path]], **kwargs) -> RAGRunner:
    """Creates a RAG runner with a pre-configured, intelligent splitter mapping."""
    
    # --- FIX: Instantiate PythonCodeTextSplitter directly to avoid TypeError ---
    default_splitter_mapping = {
        ".py": PythonCodeTextSplitter(chunk_size=1200, chunk_overlap=120),
        ".md": MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "Header 1"), ("##", "Header 2")]),
        ".js": RecursiveCharacterTextSplitter.from_language(language=Language.JS, chunk_size=1200, chunk_overlap=120),
    }
    
    # We remove chunk_size and overlap since they are defined in the splitter mapping
    kwargs.pop('chunk_size', None)
    kwargs.pop('chunk_overlap', None)
    
    config = RAGConfig(
        knowledge_files=knowledge_files,
        splitter_mapping=default_splitter_mapping,
        **kwargs
    )
    return RAGRunner(config).setup()
# # src/minichain/rag_runner.py
# """
# Provides a professional, configurable RAG (Retrieval-Augmented Generation) runner.

# This module features an intelligent, file-type-aware document splitting system
# that correctly leverages the `langchain-text-splitters` library without creating
# type conflicts. It is designed to be robust, extensible, and easy to use.
# """

# from typing import List, Dict, Optional, Union
# from dataclasses import dataclass, field
# from pathlib import Path
# import copy

# # --- Core MiniChain Imports ---
# from .core import Document
# from .chat_models.base import BaseChatModel
# from .chat_models import LocalChatModel, LocalChatConfig
# from .embeddings.base import BaseEmbeddings
# from .embeddings import LocalEmbeddings
# from .vectors.base import BaseVectorStore
# from .vectors import FAISSVectorStore
# from .core.types import SystemMessage, HumanMessage, AIMessage, BaseMessage

# # --- External, Battle-Tested Splitter Imports ---
# from .text_splitters import (
#     TextSplitter,
#     RecursiveCharacterTextSplitter,
#     PythonCodeTextSplitter,
#     MarkdownHeaderTextSplitter,
#     Language,
# )

# # ==============================================================================
# # 1. RAG Configuration
# # ==============================================================================

# @dataclass
# class RAGConfig:
#     """
#     A dataclass for configuring the RAGRunner.

#     This provides a structured way to define the knowledge base, retrieval
#     parameters, and the components (models, splitters, etc.) to be used.
#     """
    
#     # --- Knowledge Base Configuration ---
#     knowledge_texts: List[str] = field(default_factory=list)
#     knowledge_files: List[Union[str, Path]] = field(default_factory=list)
    
#     # --- Splitting Strategy ---
#     # Maps file extensions (e.g., ".py") to a pre-configured TextSplitter instance.
#     # This enables intelligent, file-type-aware document chunking.
#     splitter_mapping: Dict[str, TextSplitter] = field(default_factory=dict)
    
#     # --- Retrieval Configuration ---
#     retrieval_k: int = 3
#     similarity_threshold: Optional[float] = None
    
#     # --- Chat Configuration ---
#     system_prompt: Optional[str] = None
#     conversation_keywords: List[str] = field(default_factory=lambda: [
#         "conversation", "chat", "history", "our discussion"
#     ])
    
#     # --- Core Components (can be overridden) ---
#     chat_model: Optional[BaseChatModel] = None
#     embeddings: Optional[BaseEmbeddings] = None
#     # A default splitter for file types not in the splitter_mapping.
#     text_splitter: Optional[TextSplitter] = None
#     vector_store: Optional[BaseVectorStore] = None
    
#     debug: bool = True

# # ==============================================================================
# # 2. The RAG Runner Class
# # ==============================================================================

# class RAGRunner:
#     """
#     A professional RAG runner that handles knowledge ingestion, retrieval, and
#     augmented chat sessions with a high degree of configurability.
#     """
    
#     def __init__(self, config: RAGConfig):
#         """Initializes the runner with a configuration object."""
#         self.config = config
#         self.vector_store: Optional[BaseVectorStore] = None
#         self.chat_model: Optional[BaseChatModel] = None
#         self.default_splitter: TextSplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
#     def setup(self) -> 'RAGRunner':
#         """
#         Sets up all RAG components based on the configuration.

#         This method prepares the embeddings model, processes and splits the
#         source documents using the intelligent splitter mapping, and initializes
#         the vector store and chat model.

#         Returns:
#             The configured RAGRunner instance, allowing for method chaining.
#         """
#         if self.config.debug:
#             print("--- Setting up RAG Components ---")
        
#         if self.config.text_splitter:
#             self.default_splitter = self.config.text_splitter
        
#         embeddings = self.config.embeddings or LocalEmbeddings()
        
#         documents = self._prepare_documents()
        
#         if self.config.vector_store:
#             self.vector_store = self.config.vector_store
#         else:
#             if documents:
#                 self.vector_store = FAISSVectorStore.from_documents(documents, embeddings)
#             else:
#                 self.vector_store = FAISSVectorStore(embeddings=embeddings)
        
#         self.chat_model = self.config.chat_model or LocalChatModel(LocalChatConfig(model="local-model"))
        
#         if self.config.debug:
#             num_chunks = len(self.vector_store._docstore) if self.vector_store and hasattr(self.vector_store, '_docstore') else 0
#             print(f"✅ RAG setup complete. Ingested {len(self.config.knowledge_files)} files into {num_chunks} document chunks.")
        
#         return self
    
#     def _prepare_documents(self) -> List[Document]:
#         """
#         Loads, splits, and prepares documents for ingestion into the vector store.
#         This method correctly handles the type mismatch between MiniChain's Document
#         and LangChain's Document by only passing primitive types to the splitter.
#         """
#         raw_docs: List[Document] = []
        
#         # Ingest from raw text strings
#         for text in self.config.knowledge_texts:
#             raw_docs.append(Document(page_content=text, metadata={"source_type": "text"}))
        
#         # Ingest from files
#         for file_path in self.config.knowledge_files:
#             file = Path(file_path)
#             if not file.is_file():
#                 if self.config.debug: print(f"Warning: Path is not a file, skipping: {file}")
#                 continue
#             try:
#                 with open(file, 'r', encoding='utf-8') as f:
#                     content = f.read()
#                     raw_docs.append(Document(
#                         page_content=content,
#                         metadata={"source": str(file), "file_extension": file.suffix}
#                     ))
#             except Exception as e:
#                 print(f"Warning: Could not read file {file}: {e}")

#         # Split documents using the intelligent mapping, avoiding type conflicts
#         all_split_docs: List[Document] = []
#         for doc in raw_docs:
#             file_ext = doc.metadata.get("file_extension", ".txt")
#             splitter = self.config.splitter_mapping.get(file_ext, self.default_splitter)
            
#             if self.config.debug:
#                 source_name = doc.metadata.get('source', 'raw text')
#                 print(f"Splitting '{source_name}' with {splitter.__class__.__name__}...")
            
#             # --- THE CORE FIX ---
#             # 1. We pass the raw text (str) to the LangChain splitter.
#             chunks = splitter.split_text(doc.page_content)
            
#             # 2. We create new MiniChain Documents from the resulting text chunks,
#             #    preserving the metadata from the original source document.
#             for chunk_content in chunks:
#                 new_doc = Document(page_content=chunk_content, metadata=copy.deepcopy(doc.metadata))
#                 all_split_docs.append(new_doc)
#             # --- END OF CORE FIX ---
            
#         return all_split_docs

#     def _retrieve_context(self, query: str) -> str:
#         """Retrieves relevant context from the vector store for a given query."""
#         if not self.vector_store: return ""
#         try:
#             search_results = self.vector_store.similarity_search(query, k=self.config.retrieval_k)
#             # Join with two newlines for better separation in the prompt
#             return "\n\n".join([doc.page_content for doc, score in search_results])
#         except Exception as e:
#             if self.config.debug: print(f"[DEBUG] Error retrieving context: {e}")
#             return ""
    
#     def run_chat(self) -> None:
#         """Starts an interactive, streaming RAG-enabled chat session."""
#         if not self.chat_model:
#             raise RuntimeError("RAG runner not set up. Call setup() first.")
        
#         print("\n" + "="*50)
#         print(" Mini-Chain RAG Chat ".center(50, " "))
#         print("="*50)
#         print("Enter your message. Type 'exit' or 'quit' to end the session.")
        
#         history: List[Dict[str, str]] = []
#         if self.config.system_prompt:
#             history.append({"role": "system", "content": self.config.system_prompt})
        
#         while True:
#             try:
#                 user_input = input("\n[ You ] -> ")
#                 if user_input.lower() in ["exit", "quit"]:
#                     print("\n🤖 Session ended. Goodbye!")
#                     break
                
#                 context = self._retrieve_context(user_input)
#                 if context:
#                     if self.config.debug: print(f"[DEBUG] Retrieved context: {context[:150]}...")
#                     enhanced_input = f"Based on the following context, answer the user's question.\n\nContext:\n{context}\n\nQuestion: {user_input}"
#                 else:
#                     enhanced_input = user_input
                
#                 history.append({"role": "user", "content": enhanced_input})
                
#                 messages_for_llm: List[BaseMessage] = [
#                     (SystemMessage if msg["role"] == "system" else
#                      AIMessage if msg["role"] == "assistant" else HumanMessage)
#                     (content=msg["content"]) for msg in history
#                 ]
                
#                 print("[ AI  ] -> ", end="", flush=True)
                
#                 full_response = ""
#                 for chunk in self.chat_model.stream(messages_for_llm):
#                     print(chunk, end="", flush=True)
#                     full_response += chunk
#                 print()
                
#                 history.append({"role": "assistant", "content": full_response})
            
#             except KeyboardInterrupt:
#                 print("\n\n🤖 Session ended. Goodbye!")
#                 break
#             except Exception as e:
#                 print(f"\nAn error occurred: {e}")
#                 if self.config.debug:
#                     import traceback
#                     print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
#                 break

# # ==============================================================================
# # 3. High-Level Convenience Functions
# # ==============================================================================

# def create_rag(
#     knowledge_files: Optional[List[Union[str, Path]]] = None,
#     knowledge_texts: Optional[List[str]] = None,
#     **kwargs
# ) -> RAGRunner:
#     """
#     Creates a RAG runner with a pre-configured, intelligent splitter mapping.

#     This is the recommended entry point for most use cases.

#     Args:
#         knowledge_files: A list of file paths to ingest.
#         knowledge_texts: A list of raw text strings to ingest.
#         **kwargs: Additional parameters to pass to the RAGConfig.

#     Returns:
#         A fully set-up RAGRunner instance.
#     """
#     default_splitter_mapping = {
#         ".py": PythonCodeTextSplitter.from_language(
#             language=Language.PYTHON, chunk_size=1200, chunk_overlap=120
#         ),
#         ".md": MarkdownHeaderTextSplitter(
#             headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
#         ),
#         ".js": RecursiveCharacterTextSplitter.from_language(
#             language=Language.JS, chunk_size=1200, chunk_overlap=120
#         ),
#         ".html": RecursiveCharacterTextSplitter.from_language(
#             language=Language.HTML, chunk_size=1200, chunk_overlap=120
#         ),
#     }
    
#     config = RAGConfig(
#         knowledge_files=knowledge_files or [],
#         knowledge_texts=knowledge_texts or [],
#         splitter_mapping=default_splitter_mapping,
#         **kwargs
#     )
#     return RAGRunner(config).setup()

# def create_rag_from_directory(
#     directory: Union[str, Path],
#     file_extensions: Optional[List[str]] = None,
#     **kwargs
# ) -> RAGRunner:
#     """
#     Creates a RAG runner from all files in a directory with specified extensions.
#     """
#     if file_extensions is None:
#         file_extensions = ['.py', '.md', '.js', '.ts', '.html', '.css', '.txt']

#     directory = Path(directory)
#     if not directory.is_dir():
#         raise ValueError(f"Provided path is not a directory: {directory}")
        
#     file_paths = []
#     for ext in file_extensions:
#         file_paths.extend(directory.rglob(f"*{ext}")) # rglob for recursive search
    
#     if kwargs.get('debug', True):
#         print(f"Found {len(file_paths)} files to load from '{directory}'.")
    
#     return create_rag(knowledge_files=file_paths, **kwargs)
# # """
# # Configurable RAG (Retrieval-Augmented Generation) runner for Mini-Chain.

# # This module provides a high-level interface for creating RAG-enabled chat sessions
# # with configurable knowledge bases, models, and retrieval strategies.
# # """

# # from typing import List, Dict, Optional, Union, Callable
# # from dataclasses import dataclass, field
# # from pathlib import Path

# # from .core import Document
# # from .chat_models.base import BaseChatModel
# # from .chat_models import LocalChatModel, LocalChatConfig
# # from .embeddings.base import BaseEmbeddings
# # from .embeddings import LocalEmbeddings
# # from .vectors.base import BaseVectorStore
# # from .vectors import FAISSVectorStore
# # from .text_splitters import BaseTextSplitter
# # from .text_splitters import RecursiveCharacterTextSplitter
# # from .core.types import SystemMessage, HumanMessage, AIMessage, BaseMessage


# # @dataclass
# # class RAGConfig:
# #     """Configuration class for RAG setup."""
    
# #     # Knowledge base configuration
# #     knowledge_texts: List[str] = field(default_factory=list)
# #     knowledge_files: List[Union[str, Path]] = field(default_factory=list)
# #     chunk_size: int = 1000
# #     chunk_overlap: int = 200
    
# #     # Retrieval configuration
# #     retrieval_k: int = 3
# #     similarity_threshold: Optional[float] = None
    
# #     # Chat configuration
# #     system_prompt: Optional[str] = None
# #     conversation_keywords: List[str] = field(default_factory=lambda: [
# #         "ask", "question", "said", "last", "first", "previous", 
# #         "conversation", "chat", "tell me about our", "what did"
# #     ])
    
# #     # Components (optional - will use defaults if not provided)
# #     chat_model: Optional[BaseChatModel] = None
# #     embeddings: Optional[BaseEmbeddings] = None
# #     text_splitter: Optional[BaseTextSplitter] = None
# #     vector_store: Optional[BaseVectorStore] = None
    
# #     # Debug mode
# #     debug: bool = True


# # class RAGRunner:
# #     """
# #     A configurable RAG runner that handles setup and execution of RAG-enabled chats.
# #     """
    
# #     def __init__(self, config: RAGConfig):
# #         self.config = config
# #         self.vector_store: Optional[BaseVectorStore] = None
# #         self.chat_model: Optional[BaseChatModel] = None
        
# #     def setup(self) -> 'RAGRunner':
# #         """Set up all RAG components based on configuration."""
# #         if self.config.debug:
# #             print("--- Setting up RAG Components ---")
        
# #         # 1. Setup text splitter
# #         text_splitter = self.config.text_splitter or RecursiveCharacterTextSplitter(
# #             chunk_size=self.config.chunk_size,
# #             chunk_overlap=self.config.chunk_overlap
# #         )
        
# #         # 2. Setup embeddings
# #         embeddings = self.config.embeddings or LocalEmbeddings()
        
# #         # 3. Prepare documents
# #         documents = self._prepare_documents(text_splitter)
        
# #         # 4. Setup vector store
# #         if self.config.vector_store:
# #             self.vector_store = self.config.vector_store
# #         else:
# #             if documents:
# #                 self.vector_store = FAISSVectorStore.from_documents(documents, embeddings)
# #             else:
# #                 # Create empty vector store
# #                 self.vector_store = FAISSVectorStore(embeddings)
        
# #         # 5. Setup chat model
# #         self.chat_model = self.config.chat_model or LocalChatModel(LocalChatConfig())
        
# #         if self.config.debug:
# #             print(f"✅ RAG setup complete with {len(documents)} document chunks")
        
# #         return self
    
# #     def _prepare_documents(self, text_splitter: BaseTextSplitter) -> List[Document]:
# #         """Prepare documents from knowledge texts and files."""
# #         documents = []
        
# #         # Add knowledge texts
# #         for text in self.config.knowledge_texts:
# #             documents.append(Document(page_content=text))
        
# #         # Add knowledge files
# #         for file_path in self.config.knowledge_files:
# #             try:
# #                 with open(file_path, 'r', encoding='utf-8') as f:
# #                     content = f.read()
# #                     documents.append(Document(
# #                         page_content=content,
# #                         metadata={"source": str(file_path)}
# #                     ))
# #             except Exception as e:
# #                 print(f"Warning: Could not read file {file_path}: {e}")
        
# #         # Split documents
# #         if documents:
# #             split_docs = text_splitter.split_documents(documents)
# #             return split_docs
        
# #         return []
    
# #     def _is_conversation_question(self, user_input: str) -> bool:
# #         """Determine if the question is about conversation history."""
# #         return any(keyword in user_input.lower() for keyword in self.config.conversation_keywords)
    
# #     def _retrieve_context(self, query: str) -> str:
# #         """Retrieve relevant context for the query."""
# #         if not self.vector_store:
# #             return ""
        
# #         try:
# #             search_results = self.vector_store.similarity_search(
# #                 query, k=self.config.retrieval_k
# #             )
            
# #             context_parts = []
# #             for result in search_results:
# #                 if isinstance(result, tuple):
# #                     # Handle (document, score) tuple format
# #                     doc, score = result
# #                     if self.config.similarity_threshold is None or score >= self.config.similarity_threshold:
# #                         context_parts.append(doc.page_content)
# #                 else:
# #                     # Handle direct document format
# #                     context_parts.append(result.page_content)
            
# #             return "\n".join(context_parts)
# #         except Exception as e:
# #             if self.config.debug:
# #                 print(f"[DEBUG] Error retrieving context: {e}")
# #             return ""
    
# #     def run_chat(self) -> None:
# #         """Start an interactive RAG-enabled chat session."""
# #         if not self.chat_model:
# #             raise RuntimeError("RAG runner not set up. Call setup() first.")
        
# #         print("\n" + "="*50)
# #         print(" Mini-Chain RAG Chat ".center(50, " "))
# #         print("="*50)
# #         print("Enter your message. Type 'exit' or 'quit' to end the session.")
        
# #         history: List[Dict[str, str]] = []
# #         if self.config.system_prompt:
# #             history.append({"role": "system", "content": self.config.system_prompt})
        
# #         while True:
# #             try:
# #                 user_input = input("\n[ You ] -> ")
# #                 if user_input.lower() in ["exit", "quit"]:
# #                     print("\n🤖 Session ended. Goodbye!")
# #                     break
                
# #                 # Determine if we need to retrieve context
# #                 if self._is_conversation_question(user_input):
# #                     if self.config.debug:
# #                         print("[DEBUG] Conversation question detected - using chat history")
# #                     enhanced_input = user_input
# #                 else:
# #                     if self.config.debug:
# #                         print("[DEBUG] Knowledge question detected - retrieving context")
                    
# #                     context = self._retrieve_context(user_input)
# #                     if context:
# #                         if self.config.debug:
# #                             print(f"[DEBUG] Retrieved context: {context[:100]}...")
# #                         enhanced_input = f"Context: {context}\n\nQuestion: {user_input}"
# #                     else:
# #                         enhanced_input = user_input
                
# #                 history.append({"role": "user", "content": enhanced_input})
                
# #                 # Convert to message objects
# #                 messages_for_llm: List[BaseMessage] = [
# #                     SystemMessage(content=msg["content"]) if msg["role"] == "system"
# #                     else HumanMessage(content=msg["content"]) if msg["role"] == "user"
# #                     else AIMessage(content=msg["content"])
# #                     for msg in history
# #                 ]
                
# #                 print("[ AI  ] -> ", end="", flush=True)
                
# #                 # Stream response
# #                 full_response = ""
# #                 for chunk in self.chat_model.stream(messages_for_llm):
# #                     print(chunk, end="", flush=True)
# #                     full_response += chunk
# #                 print()  # newline
                
# #                 history.append({"role": "assistant", "content": full_response})
                
# #                 if self.config.debug:
# #                     print(f"[DEBUG] Conversation has {len(history)} messages")
            
# #             except KeyboardInterrupt:
# #                 print("\n\n🤖 Session ended. Goodbye!")
# #                 break
# #             except Exception as e:
# #                 print(f"\nAn error occurred: {e}")
# #                 if self.config.debug:
# #                     import traceback
# #                     print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
# #                 break


# # # Convenience functions for quick setup

# # def create_rag_from_texts(
# #     knowledge_texts: List[str],
# #     system_prompt: Optional[str] = None,
# #     **kwargs
# # ) -> RAGRunner:
# #     """Create a RAG runner from a list of knowledge texts."""
# #     config = RAGConfig(
# #         knowledge_texts=knowledge_texts,
# #         system_prompt=system_prompt,
# #         **kwargs
# #     )
# #     return RAGRunner(config).setup()


# # def create_rag_from_files(
# #     file_paths: List[Union[str, Path]],
# #     system_prompt: Optional[str] = None,
# #     **kwargs
# # ) -> RAGRunner:
# #     """Create a RAG runner from a list of files."""
# #     config = RAGConfig(
# #         knowledge_files=file_paths,
# #         system_prompt=system_prompt,
# #         **kwargs
# #     )
# #     return RAGRunner(config).setup()


# # def create_rag_from_directory(
# #     directory: Union[str, Path],
# #     file_extensions: List[str] = ['.txt', '.md', '.py'],
# #     system_prompt: Optional[str] = None,
# #     **kwargs
# # ) -> RAGRunner:
# #     """Create a RAG runner from all files in a directory with specified extensions."""
# #     directory = Path(directory)
# #     file_paths = []
    
# #     for ext in file_extensions:
# #         file_paths.extend(directory.glob(f"**/*{ext}"))
    
# #     config = RAGConfig(
# #         knowledge_files=file_paths,
# #         system_prompt=system_prompt,
# #         **kwargs
# #     )
# #     return RAGRunner(config).setup()
