# # src/minichain/text_splitters/character.py

# import re
# from typing import List, Optional, Callable, Any

# from .base import BaseTextSplitter

# def _split_text_with_regex(
#     text: str, separator: str, keep_separator: bool
# ) -> List[str]:
#     """A helper function to split text with a regex separator."""
#     if separator:
#         if keep_separator:
#             # The parentheses in the pattern keep the delimiters in the result.
#             splits = re.split(f"({separator})", text)
#             # Group the separator with the text before it.
#             # e.g., ["text1", "\n\n", "text2"] -> ["text1\n\n", "text2"]
#             grouped_splits = []
#             for i in range(0, len(splits), 2):
#                 chunk = splits[i]
#                 # Don't add the separator if the chunk is empty
#                 if chunk and i + 1 < len(splits):
#                     chunk += splits[i+1]
#                 if chunk:
#                     grouped_splits.append(chunk)
#             return grouped_splits
#         else:
#             splits = re.split(separator, text)
#     else:
#         # If no separator, split by character
#         splits = list(text)
    
#     # Filter out any empty strings
#     return [s for s in splits if s]


# class RecursiveCharacterTextSplitter(BaseTextSplitter):
#     """
#     Splits text by recursively trying different separators.

#     This is a direct, lightweight, and correct port of LangChain's
#     battle-tested recursive algorithm.
#     """

#     def __init__(
#         self,
#         separators: Optional[List[str]] = None,
#         is_separator_regex: bool = False,
#         keep_separator: bool = True,
#         chunk_size: int = 1000,
#         chunk_overlap: int = 200,
#         length_function: Callable[[str], int] = len,
#         add_start_index: bool = False,
#         strip_whitespace: bool = True,
#     ) -> None:
#         super().__init__(
#             chunk_size=chunk_size,
#             chunk_overlap=chunk_overlap,
#             length_function=length_function,
#             keep_separator=keep_separator,
#             add_start_index=add_start_index,
#             strip_whitespace=strip_whitespace,
#         )
#         self._separators = separators or ["\n\n", "\n", " ", ""]
#         self._is_separator_regex = is_separator_regex

#     def _split_text(self, text: str, separators: List[str]) -> List[str]:
#         """The core recursive splitting logic from LangChain."""
#         final_chunks: List[str] = []
        
#         # Find the highest-priority separator that exists in the text.
#         separator = separators[-1]  # Start with the last one as a fallback
#         for i, s in enumerate(separators):
#             _separator = s if self._is_separator_regex else re.escape(s)
#             if s == "":
#                 separator = s
#                 break
#             if re.search(_separator, text):
#                 separator = s
#                 break
        
#         # Split the text by the best separator found.
#         _separator = separator if self._is_separator_regex else re.escape(separator)
#         splits = _split_text_with_regex(text, _separator, self._keep_separator)

#         # Now, recursively process the splits.
#         good_splits: List[str] = []
#         # The separator for merging is the one we used for splitting.
#         merging_separator = "" if self._keep_separator else separator
        
#         for s in splits:
#             if self._length_function(s) < self._chunk_size:
#                 good_splits.append(s)
#             else:
#                 # If we have some good splits, merge them first
#                 if good_splits:
#                     merged_text = self._merge_splits(good_splits, merging_separator)
#                     final_chunks.extend(merged_text)
#                     good_splits = []
                
#                 # Now, recurse on the oversized chunk with the remaining separators
#                 next_separators = separators[separators.index(separator) + 1:]
#                 if not next_separators:
#                     # If we're out of separators, we have to add the oversized chunk as is.
#                     final_chunks.append(s)
#                 else:
#                     # Otherwise, recurse!
#                     other_chunks = self._split_text(s, next_separators)
#                     final_chunks.extend(other_chunks)

#         # Merge any final remaining good splits
#         if good_splits:
#             merged_text = self._merge_splits(good_splits, merging_separator)
#             final_chunks.extend(merged_text)
            
#         return final_chunks

#     def split_text(self, text: str) -> List[str]:
#         """The main public method that kicks off the splitting process."""
#         return self._split_text(text, self._separators)
# # from __future__ import annotations
# # import re
# # from typing import List, Optional, Callable, Any
# # from minichain.text_splitters.base import BaseTextSplitter


# # class RecursiveCharacterTextSplitter(BaseTextSplitter):
# #     """
# #     A character-based text splitter that recursively splits text and then
# #     merges it back together.

# #     This is a direct, simplified adaptation of LangChain's battle-tested
# #     splitter, inheriting its robust `_merge_splits` logic from our Base class.
# #     """

# #     def __init__(
# #         self,
# #         separators: Optional[List[str]] = None,
# #         keep_separator: bool = True,
# #         # Explicitly define ALL possible parent arguments for robust subclassing
# #         chunk_size: int = 1000,
# #         chunk_overlap: int = 200,
# #         length_function: Callable[[str], int] = len,
# #         add_start_index: bool = False,
# #         strip_whitespace: bool = True,
# #     ) -> None:
# #         super().__init__(
# #             chunk_size=chunk_size,
# #             chunk_overlap=chunk_overlap,
# #             length_function=length_function,
# #             keep_separator=keep_separator,
# #             add_start_index=add_start_index,
# #             strip_whitespace=strip_whitespace,
# #         )
# #         self._separators = separators or ["\n\n", "\n", " ", ""]

# #     def _split_text(self, text: str, separators: List[str]) -> List[str]:
# #         """The core recursive splitting logic."""
# #         final_chunks: List[str] = []
        
# #         # Find the highest-priority separator that exists in the text.
# #         separator = separators[-1] # Fallback to the last separator
# #         for s in separators:
# #             if s == "":
# #                 separator = s
# #                 break
# #             if s in text:
# #                 separator = s
# #                 break
        
# #         # Split the text by the best separator.
# #         # Use re.split to handle keeping the separator correctly.
# #         if separator:
# #             # The parentheses in the pattern keep the delimiters in the result.
# #             splits = re.split(f"({re.escape(separator)})", text)
# #             # Group the separator with the text before it.
# #             # e.g., ["text1", "\n\n", "text2"] -> ["text1\n\n", "text2"]
# #             grouped_splits = []
# #             for i in range(0, len(splits), 2):
# #                 chunk = splits[i]
# #                 if i + 1 < len(splits):
# #                     chunk += splits[i+1]
# #                 if chunk:
# #                     grouped_splits.append(chunk)
# #             splits = grouped_splits
# #         else:
# #             splits = list(text)
        
# #         # Now, recursively process any split that is still too large
# #         good_splits: List[str] = []
# #         for s in splits:
# #             if self._length_function(s) < self._chunk_size:
# #                 good_splits.append(s)
# #             else:
# #                 if good_splits:
# #                     # Merge the "good" splits before handling the oversized one
# #                     merged = self._merge_splits(good_splits, "") # Don't add extra separators
# #                     final_chunks.extend(merged)
# #                     good_splits = []
                
# #                 # Recurse on the oversized chunk
# #                 next_separators = separators[separators.index(separator) + 1:]
# #                 other_chunks = self._split_text(s, next_separators)
# #                 final_chunks.extend(other_chunks)
        
# #         # Merge any final remaining good splits
# #         if good_splits:
# #             merged = self._merge_splits(good_splits, "")
# #             final_chunks.extend(merged)
            
# #         return final_chunks

# #     def split_text(self, text: str) -> List[str]:
# #         """The main public method that kicks off the splitting process."""
# #         # The `_split_text` method breaks the text into small pieces.
# #         # The `_merge_splits` from the base class does the final, robust chunking.
# #         splits = self._split_text(text, self._separators)
# #         return self._merge_splits(splits, "")
