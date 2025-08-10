# Phoenix: A Resilient Semantic Parser for LLM Output

[![PyPI Version](https://img.shields.io/pypi/v/phoenix-parser.svg)](https://pypi.org/project/phoenix-parser/)
[![License](https://img.shields.io/pypi/l/phoenix-parser.svg)](https://github.com/shalyhinpavel/phoenix/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/phoenix-parser.svg)](https://pypi.org/project/phoenix-parser/)

Getting reliable structured data from Large Language Models (LLMs) is a fundamental engineering challenge. When an LLM's output deviates even slightly from a strict JSON format, traditional parsers fail.

Phoenix is a lightweight, dependency-free library that intelligently extracts structured data from messy or incomplete LLM outputs. It doesn't just follow rules—it understands and recovers.

---

## Key Features

*   **Resilience Cascade:** A three-layer defense system to ensure you always get a result.
*   **Intelligent Cleaning:** Automatically handles common LLM errors like comments, trailing commas, and "smart" quotes.
*   **Semantic Recovery:** As a last resort, it scans unstructured text to find key-value pairs and rebuilds the data from scratch.
*   **Pydantic Integration:** Leverages Pydantic for robust validation of the final output.
*   **Lightweight & Fast:** Zero dependencies besides Pydantic, ensuring easy integration.

---

## How It Works: The Resilience Cascade

Phoenix processes LLM output through three layers of defense:

1.  **Markdown Search:** It first looks for JSON inside standard ```json ... ``` code blocks.
2.  **Direct Parsing & Cleaning:** It then attempts to parse the output as clean JSON, automatically removing common syntax errors like comments.
3.  **Semantic Extraction:** If all else fails, Phoenix activates its superpower: it analyzes the raw, unstructured text, finds `key: value` pairs, and reconstructs the data.

---

## Installation

```bash
pip install phoenix-parser
```

---

## Quickstart

Here's how to use Phoenix to reliably parse data from a messy LLM output.

```python
from phoenix_parser import AdaptiveSemanticParser, ParsingError
from pydantic import BaseModel, Field

# 1. Define your desired data structure using Pydantic
class UserProfile(BaseModel):
    user_name: str = Field(description="The full name of the user.")
    user_id: int = Field(description="The unique user identifier.")
    is_active: bool = Field(description="The active status of the user account.")

# 2. Get a messy, real-world output from an LLM
messy_llm_output = """
Here are the user details you requested.
// User is confirmed active.
```json
{
  “user_name”: “Alice”,
  “user_id”: "123", // ID is a string, needs to be an int!
  “is_active”: true, // Trailing comma...
}
```
Let me know if you need anything else!
"""

# 3. Create a parser instance and parse the data
parser = AdaptiveSemanticParser()

try:
    # Phoenix will automatically clean, parse, and validate the data
    validated_data = parser.parse(messy_llm_output, UserProfile)
    
    print("✅ Successfully parsed and validated!")
    print(validated_data)
    # Output: {'user_name': 'Alice', 'user_id': 123, 'is_active': True}
    
    assert isinstance(validated_data['user_id'], int)
    
except ParsingError as e:
    print(f"❌ Failed to parse data: {e}")

```

---

## Comparison with Classic Parsers

| Feature               | Classic Parsers (e.g., `json.loads`)                      | The Phoenix Parser                                       |
|-----------------------|-----------------------------------------------------------|----------------------------------------------------------|
| **Technology**        | Rigid grammars                                            | Hybrid: Direct parsing + Semantic understanding          |
| **Flexibility**       | Low (breaks on syntax errors)                             | High (handles messy structures, comments, etc.)          |
| **Failure Response**  | Hard `JSONDecodeError`                                    | Semantic data recovery                                   |
| **Paradigm**          | "Fixing chaos with rules."                                | "Using intelligence to understand chaos."                |

---

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.
