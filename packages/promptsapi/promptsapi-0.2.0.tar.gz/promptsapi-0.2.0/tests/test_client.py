import pytest
from promptsapi import generate_prompt, reverse_prompt

def test_generate_prompt_exists():
    """
    Test that the generate_prompt function can be imported and exists.
    """
    assert callable(generate_prompt)

def test_reverse_prompt_exists():
    """
    Test that the reverse_prompt function can be imported and exists.
    """
    assert callable(reverse_prompt)
