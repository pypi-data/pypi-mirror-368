# -*- coding: utf-8 -*-
import json
import re
from pydantic import BaseModel, ValidationError
from typing import Type, Dict, Any, Optional


class ParsingError(Exception):
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context if context is not None else {}


class AdaptiveSemanticParser:
    def __init__(self):
        self.json_block_pattern = re.compile(
            r"```(?:json)?\s*\n(.*?)\n\s*```", re.DOTALL)
        self.comment_pattern = re.compile(r"//.*?$|/\*.*?\*/", re.MULTILINE)

    def _repair_and_load(self, json_string: str) -> Dict[str, Any]:
        """
        Tries to load JSON. If it fails, tries to repair and load again.
        This is our new core parsing utility.
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            # Attempt to repair truncated JSON before giving up
            repaired_string = self._repair_truncated_json(json_string)
            return json.loads(repaired_string)

    def _repair_truncated_json(self, s: str) -> str:
        """A more robust function to fix truncated JSON strings."""
        # Find the last valid token
        for i in range(len(s) - 1, -1, -1):
            if s[i] in '{},[]"\'0123456789':
                s = s[:i+1]
                break
        # Balance braces and brackets
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')
        s += ']' * open_brackets
        s += '}' * open_braces
        return s

    def _heal_and_validate(self, data: Dict[str, Any], schema: Type[BaseModel]) -> Dict[str, Any]:
        """
        Tries to validate data. If it fails, it HEALS the data based on the schema
        and tries to validate one last time.
        """
        try:
            validated_model = schema.model_validate(data)
            return validated_model.model_dump()
        except ValidationError as e:
            # Healing logic is triggered ONLY on validation error
            healed_data = self._heal_data(data, schema)
            validated_model = schema.model_validate(healed_data)
            return validated_model.model_dump()

    def _heal_data(self, data: Dict[str, Any], schema: Type[BaseModel]) -> Dict[str, Any]:
        """Tries to fix common semantic errors, like wrong types."""
        healed_data = data.copy()
        for field_name, field_info in schema.model_fields.items():
            if field_name in healed_data:
                # Rule 1: Fix string-to-int for rating (e.g., "1/5" -> 1)
                if field_info.annotation is int and isinstance(healed_data[field_name], str):
                    match = re.search(r'\d+', healed_data[field_name])
                    if match:
                        healed_data[field_name] = int(match.group(0))
                # Rule 2: Flatten nested objects (e.g., "sentiment": {"type": "positive"})
                if field_info.annotation is str and isinstance(healed_data[field_name], dict):
                    nested_val = healed_data[field_name].get(
                        'type') or healed_data[field_name].get('sentiment')
                    if nested_val and isinstance(nested_val, str):
                        healed_data[field_name] = nested_val
        return healed_data

    def parse(self, raw_llm_output: str, expected_schema: Type[BaseModel]) -> Dict[str, Any]:
        """The main method based on the original, robust cascade logic, v2.0"""
        if not raw_llm_output or not raw_llm_output.strip():
            raise ParsingError("Input text is empty.")
        text_to_process = raw_llm_output
        # Layer 1: Markdown Search (Original Logic)
        match = self.json_block_pattern.search(text_to_process)
        if match:
            # We prioritize the content of the markdown block
            text_to_process = match.group(1)
        # Layer 2: Direct Parsing with Repair & Healing
        try:
            # Clean comments and smart quotes
            cleaned_text = text_to_process.replace('“', '"').replace('”', '"')
            cleaned_text = self.comment_pattern.sub('', cleaned_text)
            # Try to load and repair if needed
            data = self._repair_and_load(cleaned_text)
            # Try to validate and heal if needed
            return self._heal_and_validate(data, expected_schema)
        except (json.JSONDecodeError, ValidationError):
            pass  # If it fails, we fall through to the final semantic layer
        # Layer 3: Semantic Extraction (The Final Fallback)
        try:
            # We use the ORIGINAL raw output for semantics, as it has the most context
            return self._parse_semantic_fallback(raw_llm_output, expected_schema)
        except (ParsingError, ValidationError) as e:
            raise ParsingError("Failed after all layers.",
                               context={"final_error": str(e)})

    def _parse_semantic_fallback(self, text: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        """Semantic parser, used as a last resort."""
        # Cleaning "smart" quotes here as well
        text = text.replace('“', '"').replace('”', '"')
        extracted_data: Dict[str, Any] = {}
        schema_fields = schema.model_fields.items()
        for field_name, field_info in schema_fields:
            try:
                pattern_friendly_name = field_name.replace('_', '[\\s_-]*')
                key_pattern = re.compile(
                    f'["\']?{pattern_friendly_name}["\']?\\s*[:=]?', re.IGNORECASE)
                for match in key_pattern.finditer(text):
                    start_index = match.end()
                    potential_value_area = text[start_index:].lstrip()
                    value_to_add = None
                    value_match = re.match(
                        r'(-?\d+(?:\.\d+)?)', potential_value_area)
                    if value_to_add is None and value_match:
                        value_to_add = value_match.group(1)
                    value_match = re.match(
                        r'["\'](.*?)["\']', potential_value_area)
                    if value_to_add is None and value_match:
                        value_to_add = value_match.group(1)
                    value_match = re.match(
                        r'(true|false)', potential_value_area, re.IGNORECASE)
                    if value_to_add is None and value_match:
                        value_to_add = value_match.group(1).lower()
                    value_match = re.match(
                        r'([^\s,}\]]+)', potential_value_area)
                    if value_to_add is None and value_match:
                        value_to_add = value_match.group(1)
                    if value_to_add is not None:
                        value_to_add = value_to_add.rstrip('.,;/\\')
                        extracted_data[field_name] = value_to_add
                        break
            except Exception:
                continue
        if not extracted_data:
            raise ParsingError("Semantic layer couldn't extract any fields.")
        # Applying adaptive typing here as well
        for field_name, field_info in schema.model_fields.items():
            if field_name in extracted_data and field_info.annotation is int:
                if not isinstance(extracted_data[field_name], int):
                    try:
                        extracted_data[field_name] = int(
                            float(extracted_data[field_name]))
                    except (ValueError, TypeError):
                        pass
        validated_model = schema.model_validate(extracted_data)
        return validated_model.model_dump()
