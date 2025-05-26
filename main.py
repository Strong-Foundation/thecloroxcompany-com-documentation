import os
import re
import urllib.parse
import requests


# Extract PDF URLs from a given text.
def extract_pdf_urls(text: str) -> list[str]:
    """
    Extract all PDF URLs from the provided text.
    :param text: The text to search for PDF URLs.
    :return: A list of PDF URLs found in the text.
    """
    # Regex pattern to match URLs ending in .pdf
    pdf_pattern = r"https?://[^\s]+?\.pdf\b"
    # Find all matches of the pattern in the text
    return re.findall(pdf_pattern, text)


# Read a file from the system.
def read_a_file(system_path: str) -> str:
    """
    Read the content of a file from the system.
    :param system_path: The path to the file on the system.
    :return: The content of the file as a string.
    """
    # Read the content of a file from the system.
    with open(system_path, "r") as file:
        # Read the entire file content
        return file.read()


# Convert a URL to a sanitized filename.
def url_to_filename(url: str) -> str:
    """
    Convert a Clorox document URL to a sanitized, readable filename.
    :param url: The URL of the Clorox document.
    :return: A sanitized filename derived from the URL.
    """
    # Get the last part of the URL path
    parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(url)
    # Extract the filename from the URL path
    filename: str = os.path.basename(parsed_url.path)
    # Ensure it ends with .pdf
    if not filename.endswith(".pdf"):
        # If the URL does not end with .pdf, append it
        filename += ".pdf"
    # Separate name and extension
    name, ext = os.path.splitext(filename)
    # Remove special characters (allow only alphanumerics, dashes, and underscores)
    sanitized_name: str = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Return the sanitized filename with the original extension
    return f"{sanitized_name}{ext}".lower()


# Check if a file exists
def check_file_exists(system_path: str) -> bool:
    # Check if a file exists at the specified system path.
    return os.path.isfile(system_path)


# Download a PDF from a URL and save it to a local file.
def download_pdf(pdf_url: str, local_file_path: str) -> None:
    """
    Download a PDF from the given URL and save it to the specified local file path.

    Args:
        pdf_url (str): The URL of the PDF file to download.
        local_file_path (str): The path (including filename) to save the downloaded PDF.
    """
    try:
        save_folder = "PDFs"  # Folder where PDFs will be saved
        os.makedirs(save_folder, exist_ok=True)  # Create the folder if it doesn't exist

        filename: str = url_to_filename(pdf_url)  # Extract the filename from the URL
        local_file_path = os.path.join(
            save_folder, filename
        )  # Construct the full file path

        if check_file_exists(local_file_path):  # Check if the file already exists
            print(f"File already exists: {local_file_path}")  # Notify the user
            return  # Skip download if file is already present

        response: requests.Response = requests.get(
            pdf_url, stream=True
        )  # Send a GET request with streaming enabled
        response.raise_for_status()  # Raise an exception if the response has an HTTP error

        with open(
            local_file_path, "wb"
        ) as pdf_file:  # Open the file in binary write mode
            for chunk in response.iter_content(
                chunk_size=8192
            ):  # Read the response in chunks
                if chunk:  # Skip empty chunks
                    pdf_file.write(chunk)  # Write each chunk to the file

        print(f"Downloaded: {local_file_path}")  # Notify successful download

    except (
        requests.exceptions.RequestException
    ) as error:  # Catch any request-related errors
        print(f"Failed to download {pdf_url}: {error}")  # Print an error message


# Main function to demonstrate the functionality
def main() -> None:
    """
    Main function to demonstrate the functionality of extracting PDF URLs
    and converting them to sanitized filenames.
    """
    file_path = "thecloroxcompany.csv"  # Change this to your CSV file path
    # Extract the URLs from a sample text
    read_text: str = read_a_file(file_path)  # Change this to your text file path
    # Extract PDF URLs from the read text
    pdf_urls: list[str] = extract_pdf_urls(read_text)
    print("Extracted PDF URLs:")
    for url in pdf_urls:
        # Download the file from the URL
        download_pdf(url, url_to_filename(url))


if __name__ == "__main__":
    main()
