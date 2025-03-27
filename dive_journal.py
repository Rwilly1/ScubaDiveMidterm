"""
Digital Dive Journal System

This module implements a digital journaling system for scuba divers to record
their dive experiences, thoughts, and memories along with optional images.
It provides functionality for creating, storing, and retrieving dive journal
entries with associated metadata and images.

Features:
- JSON-based storage for dive journal entries
- Support for image attachments
- Automatic timestamp management
- Sorted retrieval of journal entries
"""

import json
from datetime import datetime
import os
import shutil
from pathlib import Path

class DiveJournal:
    """
    A digital journal system for recording dive experiences and memories.
    
    This class manages the storage and retrieval of dive journal entries,
    including text content and associated images. All entries are stored
    in a JSON file, with images saved to a dedicated directory.
    
    Attributes:
        file_path (str): Path to the JSON file storing journal entries
        image_dir (Path): Directory path for storing journal images
    """
    
    def __init__(self, file_path="dive_journals.json"):
        """
        Initialize the dive journal system.
        
        Args:
            file_path (str): Path to the JSON file for storing entries.
                           Defaults to 'dive_journals.json'
        """
        self.file_path = file_path
        self.journals = self._load_journals()
        self.image_dir = Path("static/journal_images")
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def _load_journals(self):
        """
        Load journal entries from the JSON file.
        
        Returns:
            list: List of journal entries. Returns empty list if file doesn't
                 exist or is corrupted.
        """
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_journal(self, entry, image_file=None):
        """
        Save a new journal entry with optional image.
        
        Args:
            entry (dict): Journal entry data including text content and metadata
            image_file (Optional[FileUpload]): Image file to attach to the entry
        
        Returns:
            bool: True if save was successful
            
        Note:
            The image file is expected to be a Streamlit UploadedFile object
            or similar that provides .name and .getvalue() attributes.
        """
        entry['timestamp'] = datetime.now().isoformat()
        
        # Handle image upload if provided
        if image_file is not None:
            # Create a unique filename based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"journal_image_{timestamp}{Path(image_file.name).suffix}"
            image_path = self.image_dir / image_filename
            
            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_file.getvalue())
            
            # Store the image path in the entry
            entry['image_path'] = f"static/journal_images/{image_filename}"
        else:
            entry['image_path'] = None
        
        self.journals.append(entry)
        self._save_to_file()
        return True

    def get_all_journals(self):
        """
        Get all journal entries sorted by date.
        
        Returns:
            list: List of journal entries sorted by timestamp in descending order
                 (newest first)
        """
        return sorted(self.journals, key=lambda x: x['timestamp'], reverse=True)

    def _save_to_file(self):
        """
        Save journals to file.
        
        Internal method to write the current state of journal entries to
        the JSON file with proper formatting.
        """
        with open(self.file_path, 'w') as f:
            json.dump(self.journals, f, indent=2)
