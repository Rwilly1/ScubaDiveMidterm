import json
from datetime import datetime
import os
import shutil
from pathlib import Path

class DiveJournal:
    def __init__(self, file_path="dive_journals.json"):
        self.file_path = file_path
        self.journals = self._load_journals()
        self.image_dir = Path("static/journal_images")
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def _load_journals(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_journal(self, entry, image_file=None):
        """Save a new journal entry with optional image"""
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
        """Get all journal entries sorted by date"""
        return sorted(self.journals, key=lambda x: x['timestamp'], reverse=True)

    def _save_to_file(self):
        """Save journals to file"""
        with open(self.file_path, 'w') as f:
            json.dump(self.journals, f, indent=2)
