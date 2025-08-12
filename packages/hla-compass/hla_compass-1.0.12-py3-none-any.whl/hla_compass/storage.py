"""
Storage utilities for HLA-Compass modules
"""

import json
import logging
from typing import Any, Optional, Union, BinaryIO
from io import BytesIO
import mimetypes
import pandas as pd

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Storage operation error"""
    pass


class Storage:
    """
    Storage utilities for module results.
    
    Provides simplified access to S3 storage for saving module outputs.
    """
    
    def __init__(self, storage_client):
        """
        Initialize storage utilities.
        
        Args:
            storage_client: Storage client from execution context
        """
        self.client = storage_client
        self.logger = logging.getLogger(f"{__name__}.Storage")
    
    def save_file(self, 
                 filename: str, 
                 content: Union[bytes, str, BinaryIO],
                 content_type: str | None = None,
                 metadata: dict[str, str] | None = None) -> str:
        """
        Save a file to result storage.
        
        Args:
            filename: Name of the file
            content: File content (bytes, string, or file-like object)
            content_type: MIME type (auto-detected if not provided)
            metadata: Additional metadata
            
        Returns:
            URL or identifier of the saved file
        """
        try:
            # Convert content to bytes if needed
            if isinstance(content, str):
                content = content.encode('utf-8')
            elif hasattr(content, 'read'):
                content = content.read()
            
            # Auto-detect content type if not provided
            if content_type is None:
                content_type, _ = mimetypes.guess_type(filename)
                if content_type is None:
                    content_type = 'application/octet-stream'
            
            self.logger.debug(f"Saving file: {filename} ({content_type})")
            
            result = self.client.put_object(
                key=filename,
                body=content,
                content_type=content_type,
                metadata=metadata or {}
            )
            
            self.logger.info(f"File saved successfully: {filename}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to save file {filename}: {e}")
            raise StorageError(f"Failed to save file: {str(e)}")
    
    def save_json(self, 
                 filename: str, 
                 data: Any,
                 indent: int = 2) -> str:
        """
        Save JSON data to storage.
        
        Args:
            filename: Name of the file (should end with .json)
            data: Data to save as JSON
            indent: JSON indentation
            
        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        content = json.dumps(data, indent=indent, default=str)
        return self.save_file(filename, content, 'application/json')
    
    def save_csv(self, 
                filename: str, 
                dataframe,
                index: bool = False) -> str:
        """
        Save pandas DataFrame as CSV.
        
        Args:
            filename: Name of the file (should end with .csv)
            dataframe: Pandas DataFrame
            index: Whether to include index
            
        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        content = dataframe.to_csv(index=index)
        return self.save_file(filename, content, 'text/csv')
    
    def save_excel(self,
                  filename: str,
                  dataframe,
                  sheet_name: str = 'Sheet1',
                  index: bool = False) -> str:
        """
        Save pandas DataFrame as Excel file.
        
        Args:
            filename: Name of the file (should end with .xlsx)
            dataframe: Pandas DataFrame or dict of DataFrames
            sheet_name: Sheet name (if single DataFrame)
            index: Whether to include index
            
        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Create Excel file in memory
        buffer = BytesIO()
        
        if isinstance(dataframe, dict):
            # Multiple sheets
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                for name, df in dataframe.items():
                    df.to_excel(writer, sheet_name=name, index=index)
        else:
            # Single sheet
            dataframe.to_excel(buffer, sheet_name=sheet_name, index=index)
        
        buffer.seek(0)
        return self.save_file(
            filename, 
            buffer.read(),
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    def save_text(self,
                 filename: str,
                 content: str,
                 encoding: str = 'utf-8') -> str:
        """
        Save text content to storage.
        
        Args:
            filename: Name of the file
            content: Text content
            encoding: Text encoding
            
        Returns:
            URL or identifier of the saved file
        """
        return self.save_file(
            filename,
            content.encode(encoding),
            'text/plain'
        )
    
    def save_html(self,
                 filename: str,
                 content: str) -> str:
        """
        Save HTML content to storage.
        
        Args:
            filename: Name of the file (should end with .html)
            content: HTML content
            
        Returns:
            URL or identifier of the saved file
        """
        if not filename.endswith('.html'):
            filename += '.html'
        
        return self.save_file(filename, content, 'text/html')
    
    def save_figure(self,
                   filename: str,
                   figure,
                   format: str = 'png',
                   dpi: int = 150) -> str:
        """
        Save matplotlib figure to storage.
        
        Args:
            filename: Name of the file
            figure: Matplotlib figure object
            format: Image format (png, svg, pdf)
            dpi: Resolution for raster formats
            
        Returns:
            URL or identifier of the saved file
        """
        # Ensure correct extension
        if not filename.endswith(f'.{format}'):
            filename = f"{filename}.{format}"
        
        # Save figure to buffer
        buffer = BytesIO()
        figure.savefig(buffer, format=format, dpi=dpi, bbox_inches='tight')
        buffer.seek(0)
        
        # Determine content type
        content_types = {
            'png': 'image/png',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        content_type = content_types.get(format, 'application/octet-stream')
        
        return self.save_file(filename, buffer.read(), content_type)
    
    def create_download_url(self,
                          filename: str,
                          expires_in: int = 3600) -> str:
        """
        Create a pre-signed download URL.
        
        Args:
            filename: Name of the file
            expires_in: URL expiration time in seconds
            
        Returns:
            Pre-signed download URL
        """
        try:
            return self.client.create_presigned_url(
                key=filename,
                expires_in=expires_in
            )
        except Exception as e:
            self.logger.error(f"Failed to create download URL: {e}")
            raise StorageError(f"Failed to create download URL: {str(e)}")
    
    def list_files(self, prefix: str | None = None) -> list[dict[str, Any]]:
        """
        List files in storage.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file metadata
        """
        try:
            return self.client.list_objects(prefix=prefix)
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            raise StorageError(f"Failed to list files: {str(e)}")
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_object(key=filename)
            self.logger.info(f"Deleted file: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file {filename}: {e}")
            raise StorageError(f"Failed to delete file: {str(e)}")


# Convenience function for working with multiple files
class ResultBundle:
    """
    Helper for bundling multiple result files.
    """
    
    def __init__(self, storage: Storage, prefix: str = "results"):
        """
        Initialize result bundle.
        
        Args:
            storage: Storage instance
            prefix: Prefix for all files in the bundle
        """
        self.storage = storage
        self.prefix = prefix
        self.files = []
    
    def add_json(self, name: str, data: Any) -> str:
        """Add JSON file to bundle"""
        filename = f"{self.prefix}/{name}.json"
        url = self.storage.save_json(filename, data)
        self.files.append({'name': name, 'type': 'json', 'url': url})
        return url
    
    def add_csv(self, name: str, dataframe) -> str:
        """Add CSV file to bundle"""
        filename = f"{self.prefix}/{name}.csv"
        url = self.storage.save_csv(filename, dataframe)
        self.files.append({'name': name, 'type': 'csv', 'url': url})
        return url
    
    def add_figure(self, name: str, figure, format: str = 'png') -> str:
        """Add figure to bundle"""
        filename = f"{self.prefix}/{name}.{format}"
        url = self.storage.save_figure(filename, figure, format)
        self.files.append({'name': name, 'type': format, 'url': url})
        return url
    
    def get_manifest(self) -> dict[str, Any]:
        """Get manifest of all files in bundle"""
        return {
            'prefix': self.prefix,
            'file_count': len(self.files),
            'files': self.files
        }
    
    def save_manifest(self) -> str:
        """Save bundle manifest"""
        return self.storage.save_json(
            f"{self.prefix}/manifest.json",
            self.get_manifest()
        )