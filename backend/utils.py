import aiofiles
import mistune
import os

async def write_to_file(filename: str, text: str) -> None:
    """Asynchronously write text to a file in UTF-8 encoding.

    Args:
        filename (str): The filename to write to.
        text (str): The text to write.
    """
    # Ensure text is a string
    if not isinstance(text, str):
        text = str(text)

    # Convert text to UTF-8, replacing any problematic characters
    text_utf8 = text.encode('utf-8', errors='replace').decode('utf-8')

    async with aiofiles.open(filename, "w", encoding='utf-8') as file:
        await file.write(text_utf8)

async def write_text_to_md(text: str, filename: str = "") -> str:
    """Writes text to a Markdown file and returns the file path.

    Args:
        text (str): Text to write to the Markdown file.

    Returns:
        str: The file path of the generated Markdown file.
    """
    file_path = f"outputs/{filename[:60]}.md"
    await write_to_file(file_path, text)
    return file_path

async def write_md_to_pdf(text: str, filename: str = "") -> str:
    """Converts Markdown text to a PDF file and returns the file path.
    
    Tries WeasyPrint (via md2pdf) first, falls back to reportlab on Windows
    if GTK+ libraries are missing.

    Args:
        text (str): Markdown text to convert.

    Returns:
        str: The encoded file path of the generated PDF, or empty string on failure.
    """
    file_path = f"outputs/{filename[:60]}.pdf"

    # Try WeasyPrint (md2pdf) first - best formatting
    try:
        # Resolve css path relative to this backend module to avoid
        # dependency on the current working directory.
        current_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(current_dir, "styles", "pdf_styles.css")

        from md2pdf.core import md2pdf
        md2pdf(file_path,
               md_content=text,
               css_file_path=css_path,
               base_url=None)
        print(f"Report written to {file_path}")
        return file_path
    except Exception as e:
        error_msg = str(e).lower()
        # Check if it's a WeasyPrint/GTK library error (common on Windows)
        is_weasyprint_error = any(keyword in error_msg for keyword in [
            'libgobject', 'gobject', 'weasyprint', 'gtk', 'cairo', 'pango',
            'cannot load library', 'error 0x7e'
        ])
        
        if is_weasyprint_error:
            print(f"WeasyPrint/GTK error (common on Windows): {e}")
            print("Attempting fallback PDF generation with reportlab...")
            
            # Fallback: Use reportlab for basic PDF (Windows-friendly)
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.enums import TA_LEFT
                import re
                
                # Convert markdown to plain text with basic formatting
                # Remove markdown syntax but keep structure
                plain_text = text
                # Remove headers but keep text
                plain_text = re.sub(r'^#+\s+(.+)$', r'\1', plain_text, flags=re.MULTILINE)
                # Remove bold/italic markers
                plain_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', plain_text)
                plain_text = re.sub(r'\*([^*]+)\*', r'\1', plain_text)
                # Remove links but keep text
                plain_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', plain_text)
                
                # Create PDF
                doc = SimpleDocTemplate(file_path, pagesize=letter,
                                       rightMargin=72, leftMargin=72,
                                       topMargin=72, bottomMargin=18)
                story = []
                styles = getSampleStyleSheet()
                
                # Custom style for body text
                body_style = ParagraphStyle(
                    'CustomBody',
                    parent=styles['Normal'],
                    fontSize=11,
                    leading=14,
                    alignment=TA_LEFT,
                    spaceAfter=12,
                )
                
                # Split into paragraphs and add to story
                paragraphs = plain_text.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        # Handle line breaks within paragraphs
                        para = para.replace('\n', '<br/>')
                        story.append(Paragraph(para, body_style))
                        story.append(Spacer(1, 0.2*inch))
                
                doc.build(story)
                print(f"Report written to {file_path} (using reportlab fallback)")
                return file_path
            except ImportError:
                print("reportlab not installed. Install with: pip install reportlab")
                print("Or install GTK+ runtime for WeasyPrint: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows")
            except Exception as fallback_error:
                print(f"Fallback PDF generation also failed: {fallback_error}")
        else:
            print(f"Error in converting Markdown to PDF: {e}")
        
        return ""

async def write_md_to_word(text: str, filename: str = "") -> str:
    """Converts Markdown text to a DOCX file and returns the file path.

    Args:
        text (str): Markdown text to convert.

    Returns:
        str: The encoded file path of the generated DOCX.
    """
    file_path = f"outputs/{filename[:60]}.docx"

    try:
        from docx import Document
        from htmldocx import HtmlToDocx
        # Convert report markdown to HTML
        html = mistune.html(text)
        # Create a document object
        doc = Document()
        # Convert the html generated from the report to document format
        HtmlToDocx().add_html_to_document(html, doc)

        # Saving the docx document to file_path
        doc.save(file_path)

        print(f"Report written to {file_path}")

        return file_path

    except Exception as e:
        print(f"Error in converting Markdown to DOCX: {e}")
        return ""