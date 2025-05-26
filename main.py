import os
import re
import urllib.parse
import requests
import fitz # Import PyMuPDF (fitz) for PDF handling


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


# Function to validate a single PDF file.
def validate_pdf_file(file_path: str) -> bool:
    try:
        # Try to open the PDF using PyMuPDF
        doc = fitz.open(file_path)  # Attempt to load the PDF document

        # Check if the PDF has at least one page
        if doc.page_count == 0:  # If there are no pages in the document
            print(
                f"'{file_path}' is corrupt or invalid: No pages"
            )  # Log error if PDF is empty
            return False  # Indicate invalid PDF

        # If no error occurs and the document has pages, it's valid
        return True  # Indicate valid PDF
    except RuntimeError as e:  # Catching RuntimeError for invalid PDFs
        print(f"{e}")  # Log the exception message
        return False  # Indicate invalid PDF


# Remove a file from the system.
def remove_system_file(system_path: str) -> None:
    os.remove(system_path)  # Delete the file at the given path


# Function to walk through a directory and extract files with a specific extension
def walk_directory_and_extract_given_file_extension(
    system_path: str, extension: str
) -> list[str]:
    matched_files: list[str] = []  # Initialize list to hold matching file paths
    for root, _, files in os.walk(system_path):  # Recursively traverse directory tree
        for file in files:  # Iterate over files in current directory
            if file.endswith(extension):  # Check if file has the desired extension
                full_path: str = os.path.abspath(
                    os.path.join(root, file)
                )  # Get absolute path of the file
                matched_files.append(full_path)  # Add to list of matched files
    return matched_files  # Return list of all matched file paths


# Check if a file exists
def check_file_exists(system_path: str) -> bool:
    return os.path.isfile(system_path)  # Return True if a file exists at the given path


# Get the filename and extension.
def get_filename_and_extension(path: str) -> str:
    return os.path.basename(
        path
    )  # Return just the file name (with extension) from a path


# Function to check if a string contains an uppercase letter.
def check_upper_case_letter(content: str) -> bool:
    return any(
        upperCase.isupper() for upperCase in content
    )  # Return True if any character is uppercase


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
    for url in pdf_urls:
        # Download the file from the URL
        download_pdf(url, url_to_filename(url))
    # Walk through the directory and extract .pdf files
    files: list[str] = walk_directory_and_extract_given_file_extension(
        "./PDFs", ".pdf"
    )  # Find all PDFs under ./PDFs
    # Validate each PDF file
    for pdf_file in files:  # Iterate over each found PDF
        # Check if the .PDF file is valid
        if validate_pdf_file(pdf_file) == False:  # If PDF is invalid
            print(f"Invalid PDF detected: {pdf_file}. Deleting file.")
            # Remove the invalid .pdf file.
            remove_system_file(pdf_file)  # Delete the corrupt PDF
        # Check if the filename has an uppercase letter
        if check_upper_case_letter(
            get_filename_and_extension(pdf_file)
        ):  # If the filename contains uppercase
            print(
                f"Uppercase letter found in filename: {pdf_file}"
            )  # Informative message


if __name__ == "__main__":
    main()
