#!/usr/bin/env python3
"""
Email Document Processor for Legal Enhancement
Handles MSG, EML, and PST files for legal document analysis
"""

import logging
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Email processing imports (with fallback handling)
try:
    import email
    import email.mime.text
    import email.mime.multipart
    from email.header import decode_header
    import quopri
    import base64
    EMAIL_PROCESSING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Email processing dependencies not available: {e}")
    EMAIL_PROCESSING_AVAILABLE = False

# PST file processing (optional, heavy dependency)
try:
    import pypff
    PST_PROCESSING_AVAILABLE = True
except ImportError:
    logger.warning("PST processing not available. Install pypff for PST support.")
    PST_PROCESSING_AVAILABLE = False

# Archive processing (ZIP/RAR support)
try:
    import zipfile
    import tarfile
    ZIP_PROCESSING_AVAILABLE = True
except ImportError:
    logger.warning("ZIP processing not available.")
    ZIP_PROCESSING_AVAILABLE = False

try:
    import rarfile
    RAR_PROCESSING_AVAILABLE = True
except ImportError:
    logger.warning("RAR processing not available. Install rarfile for RAR support.")
    RAR_PROCESSING_AVAILABLE = False

class EmailProcessor:
    """
    Processes email files (MSG, EML, PST) for legal document analysis
    """
    
    def __init__(self):
        self.supported_formats = ['.msg', '.eml', '.pst']
        logger.info(f"Email Processor initialized - Email processing: {EMAIL_PROCESSING_AVAILABLE}, PST processing: {PST_PROCESSING_AVAILABLE}")
    
    def is_available(self) -> bool:
        """Check if email processing is available"""
        return EMAIL_PROCESSING_AVAILABLE
    
    def can_process_pst(self) -> bool:
        """Check if PST processing is available"""
        return PST_PROCESSING_AVAILABLE
    
    async def process_email_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a single email file (MSG, EML, or PST)
        
        Args:
            file_path: Path to the email file
            
        Returns:
            Dictionary with processed email content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Email file not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.msg':
            return await self._process_msg_file(file_path)
        elif file_extension == '.eml':
            return await self._process_eml_file(file_path)
        elif file_extension == '.pst':
            return await self._process_pst_file(file_path)
        else:
            raise ValueError(f"Unsupported email format: {file_extension}")
    
    async def _process_msg_file(self, file_path: Path) -> Dict[str, Any]:
        """Process MSG file (Outlook message format)"""
        if not EMAIL_PROCESSING_AVAILABLE:
            return self._fallback_processing(file_path, "MSG file processing not available")
        
        try:
            # MSG files are actually OLE2 compound documents
            # We'll use a simple text extraction approach
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Extract text content (basic approach)
            text_content = self._extract_text_from_binary(content)
            
            return {
                "raw_content": text_content,
                "url": str(file_path),
                "enhanced_processing": True,
                "metadata": {
                    "file_type": "msg",
                    "processing_method": "email_extraction",
                    "file_size": file_path.stat().st_size,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to process MSG file {file_path}: {e}")
            return self._fallback_processing(file_path, f"MSG processing failed: {e}")
    
    async def _process_eml_file(self, file_path: Path) -> Dict[str, Any]:
        """Process EML file (email message format)"""
        if not EMAIL_PROCESSING_AVAILABLE:
            return self._fallback_processing(file_path, "EML file processing not available")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                msg = email.message_from_file(f)
            
            # Extract email content
            subject = self._decode_header(msg.get('Subject', ''))
            sender = self._decode_header(msg.get('From', ''))
            recipient = self._decode_header(msg.get('To', ''))
            date = msg.get('Date', '')
            
            # Extract body content
            body = self._extract_email_body(msg)
            
            # Extract attachments
            attachments = self._extract_attachments(msg)
            
            # Create formatted content
            formatted_content = f"""
EMAIL MESSAGE
=============
Subject: {subject}
From: {sender}
To: {recipient}
Date: {date}

{body}
"""
            
            # Add attachments to content
            if attachments:
                formatted_content += "\n\nATTACHMENTS\n===========\n"
                for i, attachment in enumerate(attachments, 1):
                    formatted_content += f"\nAttachment {i}: {attachment['filename']}\n"
                    formatted_content += f"Type: {attachment['content_type']}\n"
                    formatted_content += f"Size: {attachment['size']} bytes\n"
                    formatted_content += f"Content:\n{attachment['content']}\n"
                    formatted_content += "-" * 50 + "\n"
            
            return {
                "raw_content": formatted_content,
                "url": str(file_path),
                "enhanced_processing": True,
                "metadata": {
                    "file_type": "eml",
                    "processing_method": "email_parsing",
                    "subject": subject,
                    "sender": sender,
                    "recipient": recipient,
                    "date": date,
                    "attachments": len(attachments),
                    "attachment_files": [att["filename"] for att in attachments],
                    "file_size": file_path.stat().st_size,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to process EML file {file_path}: {e}")
            return self._fallback_processing(file_path, f"EML processing failed: {e}")
    
    async def _process_pst_file(self, file_path: Path) -> Dict[str, Any]:
        """Process PST file (Outlook Personal Storage Table)"""
        if not PST_PROCESSING_AVAILABLE:
            return self._fallback_processing(file_path, "PST file processing not available")
        
        try:
            pst = pypff.file()
            pst.open(str(file_path))
            
            # Extract all messages from PST
            messages = []
            self._extract_pst_messages(pst.root_folder, messages)
            
            # Format all messages
            formatted_content = "OUTLOOK PST FILE - ALL MESSAGES\n"
            formatted_content += "=" * 50 + "\n\n"
            
            for i, msg in enumerate(messages, 1):
                formatted_content += f"MESSAGE {i}\n"
                formatted_content += "-" * 20 + "\n"
                formatted_content += f"Subject: {msg.get('subject', 'N/A')}\n"
                formatted_content += f"From: {msg.get('sender', 'N/A')}\n"
                formatted_content += f"To: {msg.get('recipient', 'N/A')}\n"
                formatted_content += f"Date: {msg.get('date', 'N/A')}\n"
                formatted_content += f"Body: {msg.get('body', 'N/A')}\n\n"
            
            pst.close()
            
            return {
                "raw_content": formatted_content,
                "url": str(file_path),
                "enhanced_processing": True,
                "metadata": {
                    "file_type": "pst",
                    "processing_method": "pst_extraction",
                    "message_count": len(messages),
                    "file_size": file_path.stat().st_size,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.warning(f"Failed to process PST file {file_path}: {e}")
            return self._fallback_processing(file_path, f"PST processing failed: {e}")
    
    def _extract_pst_messages(self, folder, messages: List[Dict], level: int = 0):
        """Recursively extract messages from PST folder"""
        try:
            for item in folder.sub_items:
                if hasattr(item, 'message_class') and 'IPM.Note' in str(item.message_class):
                    # This is a message
                    try:
                        msg_data = {
                            'subject': str(item.subject) if hasattr(item, 'subject') else 'N/A',
                            'sender': str(item.sender_name) if hasattr(item, 'sender_name') else 'N/A',
                            'recipient': str(item.display_to) if hasattr(item, 'display_to') else 'N/A',
                            'date': str(item.delivery_time) if hasattr(item, 'delivery_time') else 'N/A',
                            'body': str(item.plain_text_body) if hasattr(item, 'plain_text_body') else 'N/A'
                        }
                        messages.append(msg_data)
                    except Exception as e:
                        logger.warning(f"Failed to extract message: {e}")
                
                # Recursively process subfolders
                if hasattr(item, 'sub_items'):
                    self._extract_pst_messages(item, messages, level + 1)
                    
        except Exception as e:
            logger.warning(f"Failed to process PST folder: {e}")
    
    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""
        
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except Exception:
            return str(header)
    
    def _extract_email_body(self, msg) -> str:
        """Extract body content from email message"""
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode('utf-8', errors='ignore')
                elif content_type == "text/html":
                    # Extract text from HTML
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_content = payload.decode('utf-8', errors='ignore')
                        # Simple HTML tag removal
                        body += re.sub(r'<[^>]+>', '', html_content)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def _extract_attachments(self, msg) -> List[Dict[str, Any]]:
        """Extract attachments from email message"""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = part.get("Content-Disposition", "")
                content_type = part.get_content_type()
                
                # Check if this is an attachment
                if "attachment" in content_disposition or (
                    content_type not in ["text/plain", "text/html"] and 
                    part.get_filename()
                ):
                    filename = part.get_filename()
                    if filename:
                        # Decode filename if needed
                        filename = self._decode_header(filename)
                        
                        # Get attachment content
                        payload = part.get_payload(decode=True)
                        if payload:
                            # For text attachments, extract content
                            if content_type.startswith("text/"):
                                try:
                                    content = payload.decode('utf-8', errors='ignore')
                                    attachments.append({
                                        "filename": filename,
                                        "content_type": content_type,
                                        "content": content,
                                        "size": len(payload)
                                    })
                                except Exception as e:
                                    logger.warning(f"Failed to decode text attachment {filename}: {e}")
                            else:
                                # For binary attachments, just note them
                                attachments.append({
                                    "filename": filename,
                                    "content_type": content_type,
                                    "content": f"[Binary attachment: {filename}]",
                                    "size": len(payload)
                                })
        
        return attachments
    
    def _extract_text_from_binary(self, content: bytes) -> str:
        """Extract text from binary content (basic approach)"""
        try:
            # Convert bytes to string and extract readable text
            text = content.decode('utf-8', errors='ignore')
            # Remove non-printable characters
            text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception:
            return "Binary content could not be decoded"
    
    def _fallback_processing(self, file_path: Path, reason: str) -> Dict[str, Any]:
        """Fallback processing when email processing is not available"""
        try:
            # Try to read as text file
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return {
                "raw_content": content,
                "url": str(file_path),
                "enhanced_processing": False,
                "metadata": {
                    "file_type": file_path.suffix.lower(),
                    "processing_method": "fallback",
                    "reason": reason,
                    "file_size": file_path.stat().st_size,
                    "processed_at": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Fallback processing failed for {file_path}: {e}")
            return {
                "raw_content": f"Could not process {file_path.name}: {reason}",
                "url": str(file_path),
                "enhanced_processing": False,
                "metadata": {
                    "file_type": file_path.suffix.lower(),
                    "processing_method": "error",
                    "error": str(e),
                    "file_size": file_path.stat().st_size,
                    "processed_at": datetime.now().isoformat()
                }
            }
    
    async def process_email_files_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """Process multiple email files in batch"""
        tasks = []
        for file_path in file_paths:
            tasks.append(self.process_email_file(file_path))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process {file_paths[i]}: {result}")
                processed_results.append({
                    "raw_content": f"Error processing {file_paths[i]}: {result}",
                    "url": str(file_paths[i]),
                    "enhanced_processing": False,
                    "metadata": {
                        "file_type": Path(file_paths[i]).suffix.lower(),
                        "processing_method": "error",
                        "error": str(result)
                    }
                })
            else:
                processed_results.append(result)
        
        return processed_results