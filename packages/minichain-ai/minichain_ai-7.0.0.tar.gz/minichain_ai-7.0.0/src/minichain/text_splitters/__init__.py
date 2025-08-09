# src/minichain/text_splitters/__init__.py

"""
This module re-exports the robust and battle-tested text splitters, helpers,
and enums from the lightweight `langchain-text-splitters` package.

This provides a rich, consistent, and powerful text splitting API for users 
of `minichain` without reinventing the wheel. Users can now access a wide
variety of splitters for different languages and document types.
"""

# Import all the desired classes, enums, and helpers directly from the real library.
from langchain_text_splitters import (
    # Core Classes
    TextSplitter,
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    
    # Language-Specific Splitters
    PythonCodeTextSplitter,
    MarkdownTextSplitter,
    LatexTextSplitter,
    KonlpyTextSplitter,
    NLTKTextSplitter,
    SpacyTextSplitter,
    JSFrameworkTextSplitter,
    
    # Document-Type-Specific Splitters
    HTMLHeaderTextSplitter,
    HTMLSectionSplitter,
    HTMLSemanticPreservingSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter,
    ExperimentalMarkdownSyntaxTextSplitter,

    # Tokenizer-Specific Splitters
    SentenceTransformersTokenTextSplitter,
    
    # Helper Enums and Functions
    Language,
    Tokenizer,
    ElementType,
    HeaderType,
    LineType,
    split_text_on_tokens,
)

# This __all__ list defines the public API of this module.
# It's a direct copy from the langchain-text-splitters __all__ list you provided,
# ensuring we expose everything.
__all__ = [
    "CharacterTextSplitter",
    "ElementType",
    "ExperimentalMarkdownSyntaxTextSplitter",
    "HTMLHeaderTextSplitter",
    "HTMLSectionSplitter",
    "HTMLSemanticPreservingSplitter",
    "HeaderType",
    "JSFrameworkTextSplitter",
    "KonlpyTextSplitter",
    "Language",
    "LatexTextSplitter",
    "LineType",
    "MarkdownHeaderTextSplitter",
    "MarkdownTextSplitter",
    "NLTKTextSplitter",
    "PythonCodeTextSplitter",
    "RecursiveCharacterTextSplitter",
    "RecursiveJsonSplitter",
    "SentenceTransformersTokenTextSplitter",
    "SpacyTextSplitter",
    "TextSplitter",
    "TokenTextSplitter",
    "Tokenizer",
    "split_text_on_tokens",
]
# # src/minichain/text_splitters/__init__.py

# from .base import BaseTextSplitter
# from .text_splitter import RecursiveCharacterTextSplitter

# __all__ = [
#     "BaseTextSplitter",
#     "RecursiveCharacterTextSplitter",
# ]
# # # src/minichain/text_splitters/__init__.py
# # """
# # This module provides classes for splitting text into smaller chunks.
# # The TokenTextSplitter is available as an optional dependency.
# # """
# # from .base import BaseTextSplitter
# # from .character import RecursiveCharacterTextSplitter


# # __all__ = [
# #     "BaseTextSplitter",
# #     "RecursiveCharacterTextSplitter",
    
   
# # ]

# # # --- Graceful import for TokenTextSplitter ---
# # try:
# #     from .token import TokenTextSplitter # type: ignore
# #     __all__.append("TokenTextSplitter")
# # except ImportError:
# #     class TokenTextSplitter:
# #         def __init__(self, *args, **kwargs):
# #             raise ImportError(
# #                 "TikToken dependency not found. Please run `pip install minichain-ai[token_splitter]` "
# #                 "to use TokenTextSplitter."
# #             )
# # # """
# # # This module provides classes for splitting large pieces of text into smaller,
# # # semantically meaningful chunks. This is a crucial preprocessing step for
# # # many RAG (Retrieval-Augmented Generation) applications.

# # # The key components exposed are:
# # #     - TokenTextSplitter: The recommended, modern splitter that operates on
# # #       language model tokens. It is language-agnostic and respects model
# # #       context window limits accurately.
# # #     - RecursiveCharacterTextSplitter: A flexible splitter that operates on
# # #       characters, attempting to split on semantic boundaries like paragraphs
# # #       and sentences first.
# # # """
# # # from .base import BaseTextSplitter
# # # from .character import RecursiveCharacterTextSplitter
# # # from .token import TokenTextSplitter
# # # from .streaming import StreamingArabicSentenceSplitter
# # # __all__ = [
# # #     "BaseTextSplitter",
# # #     "RecursiveCharacterTextSplitter",
# # #     "TokenTextSplitter",
# # #     "StreamingArabicSentenceSplitter",
# # # ]