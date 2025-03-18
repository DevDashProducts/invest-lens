from fpdf import FPDF
import os
import boto3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def text_to_pdf(text_file, pdf_file):
    """
    Convert a text file into a PDF document.

    Parameters
    ----------
    text_file : str
        The path to the input text file.
    pdf_file : str
        The path where the output PDF file will be saved.

    Returns
    -------
    bool
        True if the PDF was successfully created, False otherwise.
    """
    # Initialize PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Read and write text
    try:
        with open(text_file, "r", encoding="utf-8") as file:
            for line in file:
                # Write each line to the PDF, handling special characters
                pdf.cell(0, 10, line.strip(), ln=True)

        # Save the PDF document to the specified file
        pdf.output(pdf_file)
        return True
    except Exception as e:
        # Print error message if an exception occurs
        print(f"Error: {e}")
        return False


def save_to_pdf(
    executive_summary: str,
    company_overview: str,
    financial_overview: str,
    client_id: str,
) -> None:
    """
    Save the generated text to a PDF file and upload it to S3.

    :param executive_summary: Text for the Executive Summary section
    :param company_overview: Text for the Company Overview section
    :param financial_overview: Text for the Financial Overview section
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Function to clean the content by removing filler text before the actual content
    def clean_content(content: str) -> str:
        """
        Clean the content by removing filler text before the actual content.

        The function searches for the first occurrence of "1." in the content and
        returns the substring starting from that index. If "1." is not found, the
        function returns the original content.

        Parameters
        ----------
        content : str
            The content to be cleaned

        Returns
        -------
        str
            The cleaned content
        """
        start_index = content.find("1.")
        if start_index != -1:
            return content[start_index:]
        return content

    # Function to add a section with a title
    def add_section(pdf, title, content):
        pdf.set_font("Arial", "B", 16)  # 'B' for Bold
        pdf.cell(200, 10, txt=title, ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)  # Reset to normal
        cleaned_content = clean_content(
            content.replace("**", "")
        )  # Remove ** and clean content
        add_formatted_content(pdf, cleaned_content)

    # Function to add formatted content
    def add_formatted_content(pdf, content):
        lines = content.split("\n")
        for line in lines:
            if (
                line.startswith("1.")
                or line.startswith("2.")
                or line.startswith("3.")
                or line.startswith("4.")
                or line.startswith("5.")
                or line.startswith("6.")
                or line.startswith("6.")
                or line.startswith("7.")
            ):
                pdf.set_font("Arial", "B", 12)
                pdf.multi_cell(0, 10, line)
                pdf.set_font("Arial", "", 12)
            elif line.startswith("-"):
                pdf.cell(10)
                pdf.multi_cell(0, 10, line)
            elif line.startswith("   -"):
                pdf.cell(20)
                pdf.multi_cell(0, 10, line)
            elif line.strip().endswith(":"):
                pdf.set_font("Arial", "B", 12)
                pdf.multi_cell(0, 10, line)
                pdf.set_font("Arial", "", 12)
            else:
                pdf.multi_cell(0, 10, line)
        pdf.ln(5)

    # Add the Executive Summary section
    add_section(pdf, "Executive Summary", executive_summary)

    # Add the Company Overview section
    pdf.add_page()
    add_section(pdf, "Company Overview", company_overview)

    # Add the Financial Overview section
    pdf.add_page()
    add_section(pdf, "Financial Overview", financial_overview)

    # Save the PDF to a temporary file
    pdf_file_path = "/tmp/IC_Deck.pdf"
    pdf.output(pdf_file_path)
    # pdf.output('IC_Deck.pdf') # uncomment this line only if you are running locally

    # Upload the PDF to S3
    s3_client = boto3.client("s3")
    # Get bucket name from environment variables
    output_bucket_name = os.getenv("OUTPUT_BUCKET_NAME")

    # Generate timestamp for filename for avoiding overwriting

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"IC_deck_{client_id}_{timestamp}.pdf"
    s3_key = f"output/{filename}"

    # Upload the PDF to S3
    try:
        s3_client.upload_file(pdf_file_path, output_bucket_name, s3_key)
        print(f"PDF successfully uploaded to s3://{output_bucket_name}/{s3_key}")
    except Exception as e:
        print(f"Error uploading PDF to S3: {str(e)}")
