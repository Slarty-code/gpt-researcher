#!/usr/bin/env python3
"""
Archive Document Processor for Legal Enhancement
Handles ZIP, RAR, TAR, and other compressed archives for legal document analysis
"""

import logging
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# Archive processing imports (with fallback handling)
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

class ArchiveProcessor:
    """
    Processes compressed archive files (ZIP, RAR, TAR) for legal document analysis
    """
    
    def __init__(self):
        self.supported_formats = ['.zip', '.rar', '.tar', '.tar.gz', '.tar.bz2', '.7z']
        logger.info(f"Archive Processor initialized - ZIP: {ZIP_PROCESSING_AVAILABLE}, RAR: {RAR_PROCESSING_AVAILABLE}")
    
    def is_available(self) -> bool:
        """Check if archive processing is available"""
        return ZIP_PROCESSING_AVAILABLE or RAR_PROCESSING_AVAILABLE
    
    def can_process_zip(self) -> bool:
        """Check if ZIP processing is available"""
        return ZIP_PROCESSING_AVAILABLE
    
    def can_process_rar(self) -> bool:
        """Check if RAR processing is available"""
        return RAR_PROCESSING_AVAILABLE
    
    async def process_archive_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Process a single archive file (ZIP, RAR, TAR, etc.)
        
        Args:
            file_path: Path to the archive file
            
        Returns:
            Dictionary with processed archive content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archive file not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.zip':
            return await self._process_zip_file(file_path)
        elif file_extension == '.rar':
            return await self._process_rar_file(file_path)
        elif file_extension in ['.tar', '.tar.gz', '.tar.bz2']:
            return await self._process_tar_file(file_path)
        else:
            raise ValueError(f"Unsupported archive format: {file_extension}")
    
    async def _process_zip_file(self, file_path: Path) -> Dict[str, Any]:
        """Process ZIP file"""
        if not ZIP_PROCESSING_AVAILABLE:
            return self._fallback_processing(file_path, "ZIP processing not available")
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # Get file list
                file_list = zip_ref.namelist()
                
                # Extract and process files
                extracted_content = []
                total_size = 0
                
                for file_name in file_list:
                    try:
                        # Skip directories
                        if file_name.endswith('/'):
                            continue
                        
                        # Get file info
                        file_info = zip_ref.getinfo(file_name)
                        file_size = file_info.file_size
                        total_size += file_size
                        
                        # Extract file content
                        with zip_ref.open(file_name) as file:
                            content = file.read()
                            
                            # Try to decode as text
                            try:
                                text_content = content.decode('utf-8', errors='ignore')
                                extracted_content.append({
                                    "filename": file_name,
                                    "content": text_content,
                                    "size": file_size,
                                    "type": "text"
                                })
                            except UnicodeDecodeError:
                                # Binary file
                                extracted_content.append({
                                    "filename": file_name,
                                    "content": f"[Binary file: {file_name}]",
                                    "size": file_size,
                                    "type": "binary"
                                })
                                
                    except Exception as e:
                        logger.warning(f"Failed to process file {file_name} in ZIP: {e}")
                        continue
                
                # Create formatted content
                formatted_content = f"""
ZIP ARCHIVE CONTENTS
===================
Archive: {file_path.name}
Files: {len(file_list)}
Total Size: {total_size} bytes

"""
                
                for item in extracted_content:
                    formatted_content += f"\nFILE: {item['filename']}\n"
                    formatted_content += f"Size: {item['size']} bytes\n"
                    formatted_content += f"Type: {item['type']}\n"
                    formatted_content += f"Content:\n{item['content']}\n"
                    formatted_content += "-" * 50 + "\n"
                
                return {
                    "raw_content": formatted_content,
                    "url": str(file_path),
                    "enhanced_processing": True,
                    "metadata": {
                        "file_type": "zip",
                        "processing_method": "archive_extraction",
                        "file_count": len(file_list),
                        "total_size": total_size,
                        "extracted_files": [item["filename"] for item in extracted_content],
                        "file_size": file_path.stat().st_size,
                        "processed_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.warning(f"Failed to process ZIP file {file_path}: {e}")
            return self._fallback_processing(file_path, f"ZIP processing failed: {e}")
    
    async def _process_rar_file(self, file_path: Path) -> Dict[str, Any]:
        """Process RAR file"""
        if not RAR_PROCESSING_AVAILABLE:
            return self._fallback_processing(file_path, "RAR processing not available")
        
        try:
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                # Get file list
                file_list = rar_ref.namelist()
                
                # Extract and process files
                extracted_content = []
                total_size = 0
                
                for file_name in file_list:
                    try:
                        # Skip directories
                        if file_name.endswith('/'):
                            continue
                        
                        # Get file info
                        file_info = rar_ref.getinfo(file_name)
                        file_size = file_info.file_size
                        total_size += file_size
                        
                        # Extract file content
                        with rar_ref.open(file_name) as file:
                            content = file.read()
                            
                            # Try to decode as text
                            try:
                                text_content = content.decode('utf-8', errors='ignore')
                                extracted_content.append({
                                    "filename": file_name,
                                    "content": text_content,
                                    "size": file_size,
                                    "type": "text"
                                })
                            except UnicodeDecodeError:
                                # Binary file
                                extracted_content.append({
                                    "filename": file_name,
                                    "content": f"[Binary file: {file_name}]",
                                    "size": file_size,
                                    "type": "binary"
                                })
                                
                    except Exception as e:
                        logger.warning(f"Failed to process file {file_name} in RAR: {e}")
                        continue
                
                # Create formatted content
                formatted_content = f"""
RAR ARCHIVE CONTENTS
===================
Archive: {file_path.name}
Files: {len(file_list)}
Total Size: {total_size} bytes

"""
                
                for item in extracted_content:
                    formatted_content += f"\nFILE: {item['filename']}\n"
                    formatted_content += f"Size: {item['size']} bytes\n"
                    formatted_content += f"Type: {item['type']}\n"
                    formatted_content += f"Content:\n{item['content']}\n"
                    formatted_content += "-" * 50 + "\n"
                
                return {
                    "raw_content": formatted_content,
                    "url": str(file_path),
                    "enhanced_processing": True,
                    "metadata": {
                        "file_type": "rar",
                        "processing_method": "archive_extraction",
                        "file_count": len(file_list),
                        "total_size": total_size,
                        "extracted_files": [item["filename"] for item in extracted_content],
                        "file_size": file_path.stat().st_size,
                        "processed_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.warning(f"Failed to process RAR file {file_path}: {e}")
            return self._fallback_processing(file_path, f"RAR processing failed: {e}")
    
    async def _process_tar_file(self, file_path: Path) -> Dict[str, Any]:
        """Process TAR file (including .tar.gz, .tar.bz2)"""
        if not ZIP_PROCESSING_AVAILABLE:  # tarfile is part of zipfile import
            return self._fallback_processing(file_path, "TAR processing not available")
        
        try:
            # Determine compression mode
            if file_path.suffix == '.gz':
                mode = 'r:gz'
            elif file_path.suffix == '.bz2':
                mode = 'r:bz2'
            else:
                mode = 'r'
            
            with tarfile.open(file_path, mode) as tar_ref:
                # Get file list
                file_list = tar_ref.getnames()
                
                # Extract and process files
                extracted_content = []
                total_size = 0
                
                for file_name in file_list:
                    try:
                        # Skip directories
                        if file_name.endswith('/'):
                            continue
                        
                        # Get file info
                        file_info = tar_ref.getmember(file_name)
                        file_size = file_info.size
                        total_size += file_size
                        
                        # Extract file content
                        with tar_ref.extractfile(file_name) as file:
                            if file:
                                content = file.read()
                                
                                # Try to decode as text
                                try:
                                    text_content = content.decode('utf-8', errors='ignore')
                                    extracted_content.append({
                                        "filename": file_name,
                                        "content": text_content,
                                        "size": file_size,
                                        "type": "text"
                                    })
                                except UnicodeDecodeError:
                                    # Binary file
                                    extracted_content.append({
                                        "filename": file_name,
                                        "content": f"[Binary file: {file_name}]",
                                        "size": file_size,
                                        "type": "binary"
                                    })
                                    
                    except Exception as e:
                        logger.warning(f"Failed to process file {file_name} in TAR: {e}")
                        continue
                
                # Create formatted content
                formatted_content = f"""
TAR ARCHIVE CONTENTS
===================
Archive: {file_path.name}
Files: {len(file_list)}
Total Size: {total_size} bytes

"""
                
                for item in extracted_content:
                    formatted_content += f"\nFILE: {item['filename']}\n"
                    formatted_content += f"Size: {item['size']} bytes\n"
                    formatted_content += f"Type: {item['type']}\n"
                    formatted_content += f"Content:\n{item['content']}\n"
                    formatted_content += "-" * 50 + "\n"
                
                return {
                    "raw_content": formatted_content,
                    "url": str(file_path),
                    "enhanced_processing": True,
                    "metadata": {
                        "file_type": "tar",
                        "processing_method": "archive_extraction",
                        "file_count": len(file_list),
                        "total_size": total_size,
                        "extracted_files": [item["filename"] for item in extracted_content],
                        "file_size": file_path.stat().st_size,
                        "processed_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.warning(f"Failed to process TAR file {file_path}: {e}")
            return self._fallback_processing(file_path, f"TAR processing failed: {e}")
    
    def _fallback_processing(self, file_path: Path, reason: str) -> Dict[str, Any]:
        """Fallback processing when archive processing is not available"""
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
    
    async def process_archive_files_batch(self, file_paths: List[Union[str, Path]]) -> List[Dict[str, Any]]:
        """Process multiple archive files in batch"""
        tasks = []
        for file_path in file_paths:
            tasks.append(self.process_archive_file(file_path))
        
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