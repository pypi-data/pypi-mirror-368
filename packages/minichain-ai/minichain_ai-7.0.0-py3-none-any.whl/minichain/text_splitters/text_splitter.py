# # src/minichain/text_splitters/recursive.py

# import re
# import copy
# from typing import List, Optional, Callable, Any, Iterable

# from minichain.core.types import Document

# # This is a direct port of LangChain's robust helper function.
# def _split_text_with_regex(text: str, separator: str, keep_separator: bool) -> List[str]:
#     """Splits a string with a regex separator."""
#     if separator:
#         if keep_separator:
#             # The parentheses in the pattern keep the delimiters in the result.
#             splits = re.split(f"({separator})", text)
#             # Group the separator with the text before it.
#             grouped_splits = [splits[i] + splits[i + 1] for i in range(0, len(splits) - 1, 2)]
#             # Handle the last chunk if it exists
#             if len(splits) % 2 == 1:
#                 grouped_splits.append(splits[-1])
#             return grouped_splits
#         else:
#             splits = re.split(separator, text)
#     else:
#         splits = list(text)
#     return [s for s in splits if s]


# class RecursiveCharacterTextSplitter:
#     """
#     A lightweight and correct port of LangChain's RecursiveCharacterTextSplitter.

#     This class contains all necessary logic and does not rely on a complex base class.
#     """

#     def __init__(
#         self,
#         separators: Optional[List[str]] = None,
#         keep_separator: bool = True,
#         is_separator_regex: bool = False,
#         chunk_size: int = 1000,
#         chunk_overlap: int = 200,
#         length_function: Callable[[str], int] = len,
#     ):
#         if chunk_overlap > chunk_size:
#             raise ValueError(f"Chunk overlap ({chunk_overlap}) is larger than chunk size ({chunk_size}).")
        
#         self._separators = separators or ["\n\n", "\n", " ", ""]
#         self._keep_separator = keep_separator
#         self._is_separator_regex = is_separator_regex
#         self._chunk_size = chunk_size
#         self._chunk_overlap = chunk_overlap
#         self._length_function = length_function

#     def _join_docs(self, docs: List[str], separator: str) -> Optional[str]:
#         """Helper to join a list of strings."""
#         text = separator.join(docs).strip()
#         return text if text else None

#     def _merge_splits(self, splits: Iterable[str], separator: str) -> List[str]:
#         """The robust merging logic from LangChain."""
#         separator_len = self._length_function(separator)
#         docs: List[str] = []
#         current_doc: List[str] = []
#         total = 0
        
#         for s in splits:
#             _len = self._length_function(s)
#             if total + _len + (separator_len if current_doc else 0) > self._chunk_size:
#                 if total > self._chunk_size:
#                     # Optional: a warning for debugging oversized chunks
#                     pass
#                 if current_doc:
#                     doc = self._join_docs(current_doc, separator)
#                     if doc:
#                         docs.append(doc)
                    
#                     while total > self._chunk_overlap or (
#                         total + _len + (separator_len if current_doc else 0) > self._chunk_size and total > 0
#                     ):
#                         total -= self._length_function(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
#                         current_doc.pop(0)

#             current_doc.append(s)
#             total += _len + (separator_len if len(current_doc) > 1 else 0)

#         doc = self._join_docs(current_doc, separator)
#         if doc:
#             docs.append(doc)
            
#         return docs

#     def _split_text(self, text: str, separators: List[str]) -> List[str]:
#         """The core recursive splitting logic from LangChain."""
#         final_chunks: List[str] = []
        
#         separator = separators[-1]
#         next_separators = []
#         for i, s in enumerate(separators):
#             _separator = s if self._is_separator_regex else re.escape(s)
#             if s == "":
#                 separator = s
#                 break
#             if re.search(_separator, text):
#                 separator = s
#                 next_separators = separators[i + 1:]
#                 break

#         _separator = separator if self._is_separator_regex else re.escape(separator)
#         splits = _split_text_with_regex(text, _separator, self._keep_separator)

#         merging_separator = "" if self._keep_separator else separator
        
#         good_splits: List[str] = []
#         for s in splits:
#             if self._length_function(s) < self._chunk_size:
#                 good_splits.append(s)
#             else:
#                 if good_splits:
#                     merged = self._merge_splits(good_splits, merging_separator)
#                     final_chunks.extend(merged)
#                     good_splits = []
                
#                 if not next_separators:
#                     final_chunks.append(s)
#                 else:
#                     other_chunks = self._split_text(s, next_separators)
#                     final_chunks.extend(other_chunks)
        
#         if good_splits:
#             merged = self._merge_splits(good_splits, merging_separator)
#             final_chunks.extend(merged)
            
#         return final_chunks

#     def split_text(self, text: str) -> List[str]:
#         """The main public method that kicks off the splitting process."""
#         return self._split_text(text, self._separators)

#     def create_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> List[Document]:
#         """Create documents from a list of texts."""
#         _metadatas = metadatas or [{}] * len(texts)
#         documents: List[Document] = []
#         for i, text in enumerate(texts):
#             for chunk in self.split_text(text):
#                 metadata = copy.deepcopy(_metadatas[i])
#                 new_doc = Document(page_content=chunk, metadata=metadata)
#                 documents.append(new_doc)
#         return documents