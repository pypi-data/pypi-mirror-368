import requests
import json

def generate_prompt(api_key: str, api_url: str, raw_input: str,
                    language_code: str = "en-US",
                    prompt_mode: str = "text",
                    category: str = None,
                    subcategory: str = None,
                    persona: str = None,
                    timeout: int = 10):
    """
    Makes a POST request to the prompts-testing API to generate content.

    Args:
        api_key (str): The user's API key.
        api_url (str): The URL of the API endpoint.
        raw_input (str): The raw text input for the API.
        language_code (str, optional): The language code for the input. Defaults to "en-US".
        prompt_mode (str, optional): The mode for prompt generation ('text', 'image_gen', 'video_gen'). Defaults to "text".
        category (str, optional): The category for the prompt.
        subcategory (str, optional): The subcategory for the prompt.
        persona (str, optional): The persona for the prompt.
        timeout (int, optional): The request timeout in seconds. Defaults to 10.

    Returns:
        dict: The JSON response from the API if successful.
        None: If an error occurs.
    """
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "raw_input": raw_input,
        "language_code": language_code,
        "prompt_mode": prompt_mode
    }

    # Conditionally add category, subcategory, and persona if they are provided
    if category:
        payload["category"] = category
    if subcategory:
        payload["subcategory"] = subcategory
    if persona:
        payload["persona"] = persona

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response body: {response.text}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    return None

def reverse_prompt(api_key: str, api_url: str, input_text: str,
                   language_code: str = "en-US",
                   prompt_mode: str = "text",
                   timeout: int = 10):
    """
    Makes a POST request to the prompts-testing API to infer content.

    Args:
        api_key (str): The user's API key.
        api_url (str): The URL of the API endpoint.
        input_text (str): The text or code input for the API to infer from.
        language_code (str, optional): The language code for the input. Defaults to "en-US".
        prompt_mode (str, optional): The mode for prompt generation ('text', 'image_gen', 'video_gen'). Defaults to "text".
        timeout (int, optional): The request timeout in seconds. Defaults to 10.

    Returns:
        dict: The JSON response from the API if successful.
        None: If an error occurs.
    """
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "input_text": input_text,
        "language_code": language_code,
        "prompt_mode": prompt_mode
    }

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        print(f"Response body: {response.text}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")

    return None
