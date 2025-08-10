# -*- coding: utf-8 -*-
import json
import re
from pydantic import BaseModel, ValidationError
from typing import Type, Dict, Any, Optional, List


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
        """Tries to load JSON. If it fails, tries to repair and load again."""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            repaired_string = self._repair_truncated_json(json_string)
            return json.loads(repaired_string)

    def _repair_truncated_json(self, s: str) -> str:
        """A more robust function to fix truncated JSON strings."""
        # Find the last valid token by searching backwards
        last_token_pos = -1
        for i in range(len(s) - 1, -1, -1):
            if s[i] in '{},[]"\'0123456789':
                last_token_pos = i + 1
                break
        if last_token_pos != -1:
            s = s[:last_token_pos]
        # Balance braces and brackets
        open_braces = s.count('{') - s.count('}')
        open_brackets = s.count('[') - s.count(']')
        s += ']' * open_brackets
        s += '}' * open_braces
        return s

    def _heal_and_validate(self, data: Dict[str, Any], schema: Type[BaseModel]) -> Dict[str, Any]:
        """Tries to validate data. If it fails, it HEALS the data and tries again."""
        try:
            validated_model = schema.model_validate(data)
            return validated_model.model_dump()
        except ValidationError:
            healed_data = self._heal_data(data, schema)
            validated_model = schema.model_validate(healed_data)
            return validated_model.model_dump()

    def _heal_data(self, data: Dict[str, Any], schema: Type[BaseModel]) -> Dict[str, Any]:
        """The ultimate healing function based on all our findings."""
        healed_data = data.copy()
        for field_name, field_info in schema.model_fields.items():
            if field_name not in healed_data:
                continue
            expected_type = field_info.annotation
            current_value = healed_data[field_name]
            # Rule 1: Fix WRONG TYPES
            if expected_type is int and not isinstance(current_value, int):
                num_str = str(current_value)
                # Handles positive/negative integers
                match = re.search(r'[-+]?\d+', num_str)
                if match:
                    try:
                        healed_data[field_name] = int(match.group(0))
                    except (ValueError, TypeError):
                        pass
            # Rule 2: FLATTEN NESTED OBJECTS
            if expected_type in [str, int, float, bool] and isinstance(current_value, dict):
                # Intelligent search for a meaningful value inside the nested dict
                for key in ['value', 'data', 'text', 'result', 'overall', 'type', 'sentiment', 'name']:
                    if key in current_value:
                        healed_data[field_name] = current_value[key]
                        break  # Found a good key, stop searching
        return healed_data

    def parse(self, raw_llm_output: str, expected_schema: Type[BaseModel]) -> Dict[str, Any]:
        """The main method, v5.0. Simple, robust, and non-greedy."""
        if not raw_llm_output or not raw_llm_output.strip():
            raise ParsingError("Input text is empty.")

        # --- THE FINAL CASCADE ---

        # Step 1: Find the most likely JSON candidate string.
        # We don't parse yet, we just find the best possible text.
        json_candidate = None

        # 1a: Look for a Markdown block. It's the highest priority.
        match = self.json_block_pattern.search(raw_llm_output)
        if match:
            json_candidate = match.group(1)

        # 1b: If no block, find the largest substring between '{' and '}'.
        if not json_candidate:
            start = raw_llm_output.find('{')
            end = raw_llm_output.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_candidate = raw_llm_output[start: end + 1]

        # Step 2: If we found a JSON-like candidate, try to parse and heal it.
        if json_candidate:
            try:
                # Clean comments and smart quotes
                cleaned_text = json_candidate.replace(
                    '“', '"').replace('”', '"')
                cleaned_text = self.comment_pattern.sub('', cleaned_text)

                # Try to load (and repair if truncated)
                data = self._repair_and_load(cleaned_text)

                # Try to validate (and heal if types are wrong)
                return self._heal_and_validate(data, expected_schema)
            except (json.JSONDecodeError, ValidationError):
                # If our BEST candidate failed, it's time for the last resort.
                pass

        # Step 3: Semantic Extraction (The True Final Fallback)
        # This only runs if we couldn't parse any structured JSON.
        try:
            semantic_data = self._parse_semantic_fallback(
                raw_llm_output, expected_schema)
            # We trust the semantic parser's validation, but run it through heal just in case
            return self._heal_and_validate(semantic_data, expected_schema)
        except (ParsingError, ValidationError) as e:
            raise ParsingError("Failed after all layers.",
                               context={"final_error": str(e)})

    def _parse_semantic_fallback(self, text: str, schema: Type[BaseModel]) -> Dict[str, Any]:
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
        for field_name, field_info in schema_fields:
            if field_name in extracted_data and field_info.annotation is int:
                if not isinstance(extracted_data[field_name], int):
                    try:
                        extracted_data[field_name] = int(
                            float(extracted_data[field_name]))
                    except (ValueError, TypeError):
                        pass
        # We don't return directly, we return it to the main parse function for a final heal/validation
        return extracted_data
