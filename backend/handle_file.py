from pathlib import Path
import os
from config_loader import AppConfig
from read_pdf_file import PDFReader
from ask_llm_model import LanguageProcessing


class FileProcessor:
    def __init__(self):
        self.config = AppConfig()
        self.lang_processor = LanguageProcessing()

    def process_file(self, file_path, query):
        file_path = Path(file_path)
        ext = file_path.suffix.lower()
        print(f"The extension of the file is: '{ext}'")

        if ext == '.pdf':
            response = self.get_pdf_file_result(file_path, query)
        else:
            print("This type of file is not supported now")
            return None

        return response

    def get_pdf_file_result(self, file_path, query):
        return self._get_file_result(PDFReader, file_path, query)

    def _get_file_result(self, reader_class, file_path, query):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"No such file: '{file_path}'")

        actual_size = os.path.getsize(file_path) / 1024
        if actual_size > float(self.config.pdf_file_expected_size):
            raise Exception("File size is greater than expected")

        task_type = self.lang_processor.predict_task_type(file_path.suffix.lower(), query)

        match task_type:
            case 'Question Answering':
                reader = reader_class(file_path)
                content_chunks = reader.read_file()
                if content_chunks == None:
                    return "File could not be read"
                vector_db = self.lang_processor.do_embedding(content_chunks)

                return self.lang_processor.question_answering(vector_db, query)
            case 'Summarization':
                reader = reader_class(file_path)
                content_chunks = reader.read_file()
                if content_chunks == None:
                    return "File could not be read"
                return self.lang_processor.summarize_text(content_chunks, query)
            case 'Translation':
                reader = reader_class(file_path)
                content_chunks = reader.read_file()
                if content_chunks == None:
                    return "File could not be read"
                return self.lang_processor.language_translation(content_chunks, query)

            case _:
                return "Currently, this type of task is not supported"
