import fitz
import io
import easyocr
from PIL import Image
import numpy as np
from typing import Optional
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config_loader import AppConfig

config=AppConfig()

class PDFReader:
    def __init__(self, filepath: str,chunk_size=config.chunk_size,chunk_overlap_size=config.chunk_overlap_size):
        """Initialize the PDFReader with a path to the PDF file."""
        self.filepath = filepath
        self.chunk_size=int(chunk_size)
        self.chunk_overlap_size=int(chunk_overlap_size)
        self.reader = easyocr.Reader(['en'], gpu=False)  # Set to True if GPU is available

    def extract_images_and_convert_to_text(self, page: fitz.Page) -> str:
        """Extract images from the given page and use OCR to convert them to text."""
        text = ""
        try:
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                if pix.n - pix.alpha < 4:  # this ensures we do not have an alpha channel
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                img_bytes = pix.tobytes("ppm")
                pil_image = Image.open(io.BytesIO(img_bytes))
                pil_image.convert('RGB')
                ocr_result = self.reader.readtext(np.array(pil_image), detail=0, paragraph=True)
                text += '\n' + ' '.join(ocr_result)
                pix = None  # drop Pixmap resources
        except Exception as e:
            print(f"Error occurred while extracting images from page: {e}")
        return text
    def read_file(self) -> Optional[str]:
        """Reads a PDF file, extracts text and images, and returns them."""
        try:
            doc = fitz.open(self.filepath)
            full_text = ""
            for page_index in range(len(doc)):
                page = doc[page_index]
                if page.get_text("text"):  # Check if the page is text-based
                    # Extract readable text from the page
                    text = page.get_text("text")
                    full_text += text
                else:  # The page is image-based
                    # Extract text from images
                    full_text += self.extract_images_and_convert_to_text(page)

            doc.close()
            if full_text.strip():
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size,
                                                               chunk_overlap=self.chunk_overlap_size)
                chunks = text_splitter.create_documents([full_text])
                return chunks
            else:
                return None
        except Exception as e:
            print(f"Error occurred while reading the PDF file: {e}")
            return None