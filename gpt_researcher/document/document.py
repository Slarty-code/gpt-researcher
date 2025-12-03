import asyncio
import os
from typing import List, Union
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredCSVLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader
)
from langchain_community.document_loaders import BSHTMLLoader

# Apache Tika imports with fallback handling
try:
    import requests
    import os
    TIKA_AVAILABLE = True
except ImportError as e:
    print(f"Tika dependencies not available: {e}")
    TIKA_AVAILABLE = False
    requests = None


class DocumentLoader:

    def __init__(self, path: Union[str, List[str]]):
        self.path = path

    async def load(self) -> list:
        tasks = []
        if isinstance(self.path, list):
            for file_path in self.path:
                if os.path.isfile(file_path):  # Ensure it's a valid file
                    filename = os.path.basename(file_path)
                    file_name, file_extension_with_dot = os.path.splitext(filename)
                    file_extension = file_extension_with_dot.strip(".").lower()
                    tasks.append(self._load_document(file_path, file_extension))
                    
        elif isinstance(self.path, (str, bytes, os.PathLike)):
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_name, file_extension_with_dot = os.path.splitext(file)
                    file_extension = file_extension_with_dot.strip(".").lower()
                    tasks.append(self._load_document(file_path, file_extension))
                    
        else:
            raise ValueError("Invalid type for path. Expected str, bytes, os.PathLike, or list thereof.")

        # for root, dirs, files in os.walk(self.path):
        #     for file in files:
        #         file_path = os.path.join(root, file)
        #         file_name, file_extension_with_dot = os.path.splitext(file_path)
        #         file_extension = file_extension_with_dot.strip(".")
        #         tasks.append(self._load_document(file_path, file_extension))

        docs = []
        for pages in await asyncio.gather(*tasks):
            for page in pages:
                if page.page_content:
                    docs.append({
                        "raw_content": page.page_content,
                        "url": os.path.basename(page.metadata['source'])
                    })
                    
        if not docs:
            raise ValueError("🤷 Failed to load any documents!")

        return docs

    async def _load_document(self, file_path: str, file_extension: str) -> list:
        ret_data = []
        try:
            # Special handling for PDFs - try Tika first, fallback to PyMuPDF
            if file_extension == "pdf" and TIKA_AVAILABLE:
                ret_data = await self._load_pdf_with_tika(file_path)
            else:
                # Use standard loaders for other file types
                loader_dict = {
                    "pdf": PyMuPDFLoader(file_path),
                    "txt": TextLoader(file_path),
                    "doc": UnstructuredWordDocumentLoader(file_path),
                    "docx": UnstructuredWordDocumentLoader(file_path),
                    "pptx": UnstructuredPowerPointLoader(file_path),
                    "csv": UnstructuredCSVLoader(file_path, mode="elements"),
                    "xls": UnstructuredExcelLoader(file_path, mode="elements"),
                    "xlsx": UnstructuredExcelLoader(file_path, mode="elements"),
                    "md": UnstructuredMarkdownLoader(file_path),
                    "html": BSHTMLLoader(file_path),
                    "htm": BSHTMLLoader(file_path)
                }

                loader = loader_dict.get(file_extension, None)
                if loader:
                    try:
                        ret_data = loader.load()
                    except Exception as e:
                        print(f"Failed to load document: {file_path}")
                        print(e)

        except Exception as e:
            print(f"Failed to load document : {file_path}")
            print(e)

        return ret_data

    async def _load_pdf_with_tika(self, file_path: str) -> list:
        """Load PDF using Apache Tika for better OCR support."""
        try:
            # First try standard PyMuPDF loader
            loader = PyMuPDFLoader(file_path)
            pages = loader.load()
            
            # Check if the PDF has extractable text
            has_text = any(page.page_content.strip() for page in pages)
            
            if has_text:
                print(f"PDF has extractable text: {file_path}")
                return pages
            else:
                print(f"PDF appears to be scanned, using Tika: {file_path}")
                return await self._process_with_tika(file_path)
                
        except Exception as e:
            print(f"Standard PDF loading failed, trying Tika: {file_path} - {e}")
            return await self._process_with_tika(file_path)

    async def _process_with_tika(self, file_path: str) -> list:
        """Extract text from document using Apache Tika."""
        if not TIKA_AVAILABLE:
            print("Tika not available, returning empty pages")
            return []
            
        try:
            # Get Tika server URL from environment
            tika_url = os.getenv('TIKA_SERVER_URL', 'http://localhost:9998')
            
            # Read the file
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            # Send to Tika for text extraction
            response = requests.post(
                f"{tika_url}/tika",
                data=file_data,
                headers={'Content-Type': 'application/octet-stream'},
                timeout=60  # 60 second timeout for large files
            )
            
            if response.status_code == 200:
                text = response.text
                
                # Create a document page
                from langchain_core.documents import Document
                page = Document(
                    page_content=text,
                    metadata={
                        'source': file_path,
                        'processing_method': 'tika',
                        'tika_server': tika_url
                    }
                )
                
                print(f"Successfully processed with Tika: {file_path}")
                return [page]
            else:
                print(f"Tika processing failed for {file_path}: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Tika processing failed for {file_path}: {e}")
            return []
