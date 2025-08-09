# src/minichain/output_parsers/pydantic_parser.py

import json
from typing import Any, Type, TypeVar, Generic
from pydantic import BaseModel, ValidationError

from .base import BaseOutputParser
from ..utils.json_utils import parse_json_markdown

T = TypeVar("T", bound=BaseModel)

class PydanticOutputParser(BaseOutputParser, Generic[T]):
    """
    Parses LLM output into a Pydantic model using a robust JSON extractor.
    """
    pydantic_object: Type[T]

    def __init__(self, pydantic_object: Type[T]):
        self.pydantic_object = pydantic_object

    def get_format_instructions(self) -> str:
        """Generates clear instructions for the LLM, including the JSON schema."""
        schema = self.pydantic_object.model_json_schema()
        # Clean up the schema for a clearer prompt
        if "title" in schema: del schema["title"]
        if "type" in schema: del schema["type"]
        schema_str = json.dumps(schema)

        return (
            f"Your response MUST be a valid JSON object conforming to the following JSON schema.\n"
            f"Enclose the JSON in a single ```json markdown code block.\n"
            f"Schema:\n{schema_str}"
        )

    def parse(self, text: str) -> T:
        """
        Parses the string output and validates it with the Pydantic model.
        """
        try:
            # Use our new, robust utility to get the JSON dictionary
            json_dict = parse_json_markdown(text)
            
            # Validate the dictionary with the Pydantic model
            return self.pydantic_object.model_validate(json_dict)
        
        except (ValueError, ValidationError) as e:
            # If parsing or validation fails, raise a detailed error
            raise ValueError(
                f"Failed to parse Pydantic model '{self.pydantic_object.__name__}'. Error: {e}\n"
                f"Raw LLM output:\n---\n{text}\n---"
            )
# # src/minichain/output_parsers/pydantic_parser.py

# import json
# import re
# from typing import Any, Type, TypeVar, Generic
# from pydantic import BaseModel, ValidationError

# from .base import BaseOutputParser
# # We need to import the chat model to perform the retry
# from ..chat_models.base import BaseChatModel
# # Import the robust JSON parsing utility
# from ..utils.json_utils import parse_json_markdown


# T = TypeVar("T", bound=BaseModel)

# class PydanticOutputParser(BaseOutputParser, Generic[T]):
#     """
#     Parses LLM output into a Pydantic model and can self-correct
#     by re-prompting an LLM if the initial output is not valid.
#     """
#     pydantic_object: Type[T]
#     retry_llm: BaseChatModel | None = None

#     def __init__(self, pydantic_object: Type[T], retry_llm: BaseChatModel | None = None):
#         self.pydantic_object = pydantic_object
#         self.retry_llm = retry_llm

#     def get_format_instructions(self) -> str:
#         """Generates instructions for the LLM, including the JSON schema."""
#         schema = self.pydantic_object.model_json_schema()
#         # Clean up the schema for the prompt
#         if "title" in schema: del schema["title"]
#         if "type" in schema: del schema["type"]
#         schema_str = json.dumps(schema, indent=2)

#         # Create a sample instance to show the expected format
#         sample_data = {}
#         if "properties" in schema:
#             for field_name, field_schema in schema["properties"].items():
#                 if field_schema.get("type") == "string":
#                     sample_data[field_name] = f"example_{field_name}"
#                 elif field_schema.get("type") == "array":
#                     sample_data[field_name] = ["example1", "example2"]
#                 elif field_schema.get("type") == "integer":
#                     sample_data[field_name] = 42
#                 else:
#                     sample_data[field_name] = f"example_{field_name}"
        
#         sample_json = json.dumps(sample_data, indent=2)

#         return (
#             f"The output should be formatted as a JSON instance that conforms to the JSON schema below.\n"
#             f"Respond with ONLY the JSON object, no additional text or markdown fences.\n\n"
#             f"Schema:\n{schema_str}\n\n"
#             f"Example format:\n{sample_json}"
#         )

#     def parse(self, text: str) -> T:
#         """
#         Parses the string output and validates it with the Pydantic model.
#         If parsing fails, it uses the `retry_llm` to attempt a correction.
#         """
#         try:
#             # First attempt: parse the original text
#             json_dict = parse_json_markdown(text)
#             return self.pydantic_object.model_validate(json_dict)
#         except (ValueError, ValidationError) as e:
#             # If parsing fails and we don't have a retry model, we must fail.
#             if not self.retry_llm:
#                 raise ValueError(
#                     f"Failed to parse Pydantic model '{self.pydantic_object.__name__}' and no retry LLM was provided. Error: {e}\n"
#                     f"Raw output:\n---\n{text}\n---"
#                 )
            
#             # --- SELF-CORRECTION LOGIC ---
#             print("\n[Parser] Initial parsing failed. Attempting self-correction with the LLM...")
            
#             # Get the current schema and expected format
#             schema = self.pydantic_object.model_json_schema()
#             schema_str = json.dumps(schema, indent=2)
            
#             correction_prompt = f"""The following output did not conform to the required JSON format.
# Your task is to correct the output so that it is a valid JSON object that matches the requested schema.

# Required schema:
# {schema_str}

# Original invalid output:
# ---
# {text}
# ---

# Please provide ONLY the corrected JSON object that matches the schema above. Do not include any explanations, markdown fences, or additional text."""

#             # Use the retry_llm to fix the broken output
#             corrected_text = self.retry_llm.invoke(correction_prompt)
            
#             try:
#                 # Second and final attempt: parse the corrected text
#                 json_dict = parse_json_markdown(corrected_text)
#                 return self.pydantic_object.model_validate(json_dict)
#             except (ValueError, ValidationError) as final_e:
#                 # If it fails again, raise the final, detailed error
#                 raise ValueError(
#                     f"Failed to parse LLM output even after self-correction. Error: {final_e}\n"
#                     f"Original output:\n---\n{text}\n---\n"
#                     f"Corrected output from LLM:\n---\n{corrected_text}\n---"
#                 )
# # # src/minichain/output_parsers/pydantic_parser.py
# # """
# # An output parser that uses Pydantic for type-safe parsing.
# # """
# # import json
# # import re
# # from typing import Any, Type, TypeVar, Generic
# # from pydantic import BaseModel, ValidationError
# # from .base import BaseOutputParser

# # T = TypeVar("T", bound=BaseModel)

# # class PydanticOutputParser(BaseOutputParser, Generic[T]):
# #     """
# #     A generic class that parses LLM string output into a specific
# #     Pydantic model instance, T.
# #     """
# #     pydantic_object: Type[T]

# #     def __init__(self, pydantic_object: Type[T]):
# #         self.pydantic_object = pydantic_object

# #     def get_format_instructions(self) -> str:
# #         """
# #         Generates clear, human-readable instructions for the LLM on how to
# #         format its output as JSON, focusing on the required keys and their purpose.
# #         """
# #         schema = self.pydantic_object.model_json_schema()

# #         # Create a dictionary of { "field_name": "field_description" }
# #         # This is much clearer for the LLM than a full JSON schema.
# #         field_descriptions = {
# #             k: v.get("description", "")
# #             for k, v in schema.get("properties", {}).items()
# #         }

# #         # Build a robust instruction string that is less likely to be misinterpreted.
# #         instructions = [
# #             "Your response must be a single, valid JSON object.",
# #             "Do not include any other text, explanations, or markdown code fences.",
# #             "The JSON object must have the following keys:",
# #         ]
# #         for name, desc in field_descriptions.items():
# #             instructions.append(f'- "{name}": (Description: {desc})')
        
# #         instructions.append("\nPopulate the string values for these keys based on the user's query.")
# #         return "\n".join(instructions)


# #     def parse(self, text: str) -> T:
# #         """
# #         Parses the string output from an LLM into an instance of the target
# #         Pydantic model (T).
# #         """
# #         try:
# #             # Use regex to find the first '{' and last '}' to isolate the JSON blob.
# #             match = re.search(r"\{.*\}", text, re.DOTALL)
# #             if not match:
# #                 raise json.JSONDecodeError("No JSON object found in the output.", text, 0)

# #             json_string = match.group(0)
# #             json_object = json.loads(json_string)
            
# #             return self.pydantic_object.model_validate(json_object)
# #         except (json.JSONDecodeError, ValidationError) as e:
# #             raise ValueError(
# #                 f"Failed to parse LLM output into {self.pydantic_object.__name__}. Error: {e}\n"
# #                 f"Raw output:\n---\n{text}\n---"
# #             )
# #     def invoke(self, input: str, **kwargs: Any) -> T:
# #         return self.parse(input)
