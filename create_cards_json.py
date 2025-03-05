import json
import fitz  # PyMuPDF
import llm

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def convert_pdf_to_images_binary(pdf_path, dpi=300):
    """
    Converts a PDF to a list of binary image data.

    Args:
        pdf_path (str): Path to the PDF file
        dpi (int): Resolution of the output images

    Returns:
        list: List of binary image data
    """
    # Open the PDF
    pdf_document = fitz.open(pdf_path)

    # List to store binary data
    binary_images = []

    # Calculate zoom factor based on DPI (72 is the base DPI for PDF)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)

    # Process each page
    for page_num in range(len(pdf_document)):
        # Get the page
        page = pdf_document.load_page(page_num)

        # Render page to an image
        pix = page.get_pixmap(matrix=matrix)

        # Convert to PNG binary data
        img_binary = pix.tobytes("png")

        # Add to list
        binary_images.append(img_binary)

    # Close the document
    pdf_document.close()

    return binary_images
model = llm.get_model("gemini-2.0-flash")
schema=llm.schema_dsl("question, answer", multi=True)
system_prompt = "You are helping a student prepare flashcards to study based on lecture slides. \
Each user prompt will contain the text of a slide and an image of the slide. \
If the image of the slide contains a diagram that would be helpful to include in a question or answer, \
you should include it as ascii art."
prompt = "Create flashcards based on the following slide text and image. Generate at least 1 flashcard. \n"
file_path = '/net/scratch2/muchane/olmocr/144_lecs/results/output_a6bcd01631b4cc09e140b19cea9349e6e42fda00.jsonl'
data_list = load_jsonl(file_path)
cards_dict = {}
for slideshow in data_list:
    file_source = slideshow["metadata"]["Source-File"]
    slideshow_name = file_source.split("/")[-1]
    cards_dict[slideshow_name] = []
    pages = slideshow["attributes"]["pdf_page_numbers"]
    images = convert_pdf_to_images_binary(file_source)
    all_text = slideshow["text"]
    for i, image in enumerate(images):
        attachment = llm.Attachment(type="image/png", content=image)
        if i >= len(pages):
            continue
        start, end, page_num = pages[i]
        slide_text = all_text[start:end]
        response = model.prompt(
            prompt + slide_text,
            system=system_prompt,
            attachments=[attachment],
            schema=schema
        )
        try:
            response_json = json.loads(response.text())["items"]
        except:
            continue
        cards_dict[slideshow_name].extend(response_json)
with open("out.json", 'w') as file:
    json.dump(cards_dict, file, indent=4)
