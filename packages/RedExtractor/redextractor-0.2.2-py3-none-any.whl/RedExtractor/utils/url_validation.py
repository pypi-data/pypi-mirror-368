import requests

def get_headers(url: str) -> dict:
    """
    Abstract method to retrieve the HTTP headers required for the download.

    :return: A dictionary of headers needed for the download.
    """
    try:
        # Send a HEAD request to the URL
        response = requests.head(url, allow_redirects=True, timeout=5)

        # Check if the status code indicates success (2xx)
        if response.status_code >= 200 and response.status_code < 400:
            return response.headers
        else:
            print(f"URL is not accessible. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def validate_url(url: str) -> bool:
    """
    Abstract method to validate the URL before attempting to download.

    :param url: The URL to be validated.
    :return: True if the URL is valid, False otherwise.
    """

    try:
        # Send a HEAD request to the URL
        response = requests.head(url, allow_redirects=True, timeout=5)
        
        # Check if the status code indicates success (2xx)
        return response.status_code >= 200 and response.status_code < 400
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False