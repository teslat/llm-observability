from unittest.mock import MagicMock
from openai import OpenAI

def test_summary():
    client = MagicMock(spec=OpenAI)
    client.chat.completions.create.return_value = MagicMock()
