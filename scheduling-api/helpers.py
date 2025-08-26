# scheduling-api/helpers.py
import os
import uuid
import re
from flask import current_app
from werkzeug.utils import secure_filename 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, task_id=None, update_count=None, image_count=None):
    """Enhanced version maintaining original behavior"""
    if not file or file.filename == '':
        return None
        
    if not allowed_file(file.filename):
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Maintain original UUID fallback
    if task_id is None or update_count is None or image_count is None:
        filename = f"{uuid.uuid4()}.{ext}"
    else:
        # New structured naming while keeping original extension handling
        filename = f"task{task_id}_update{update_count}_img{image_count}.{ext}"
    
    # Add security from original version
    filename = secure_filename(filename)
    
    # Original file saving logic
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    return filename

def format_duration(minutes: int) -> str:
    """Convert minutes to human-readable format: Xmonths Xdays Xhours Xminutes"""
    if not isinstance(minutes, (int, float)) or minutes < 0:
        return "0 minutes"
        
    minutes = int(minutes)
    months = minutes // (30*24*60)
    remaining = minutes % (30*24*60)
    days = remaining // (24*60)
    remaining %= (24*60)
    hours = remaining // 60
    minutes = remaining % 60
    
    parts = []
    if months > 0:
        parts.append(f"{months} month{'s' if months > 1 else ''}")
    if days > 0:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    
    return " ".join(parts) if parts else "0 minutes"

def parse_duration(duration_str: str) -> int:
    """
    FIXED: Convert duration string to minutes with better parsing
    Supports formats like:
    - "2 hours 30 minutes"
    - "1 day"
    - "3 weeks"
    - "2 months"
    - "90 minutes"
    - "1.5 hours"
    """
    if not duration_str or not isinstance(duration_str, str):
        raise ValueError("Duration string cannot be empty or null")
    
    duration_str = duration_str.lower().strip()
    if not duration_str:
        raise ValueError("Duration string cannot be empty")
    
    # Define conversion factors (in minutes)
    units = {
        'minute': 1, 'minutes': 1, 'min': 1, 'mins': 1,
        'hour': 60, 'hours': 60, 'hr': 60, 'hrs': 60,
        'day': 24*60, 'days': 24*60,
        'week': 7*24*60, 'weeks': 7*24*60,
        'month': 30*24*60, 'months': 30*24*60,
        'year': 365*24*60, 'years': 365*24*60
    }
    
    total_minutes = 0
    
    # Use regex to find all number-unit pairs
    # This pattern matches: optional decimal numbers followed by optional spaces and unit names
    pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)'
    matches = re.findall(pattern, duration_str)
    
    if not matches:
        # Try to handle pure numbers (assume minutes)
        number_match = re.search(r'(\d+(?:\.\d+)?)', duration_str)
        if number_match:
            try:
                value = float(number_match.group(1))
                if value <= 0:
                    raise ValueError("Duration must be positive")
                return int(value)  # Assume minutes
            except ValueError:
                raise ValueError("Invalid duration format")
        else:
            raise ValueError("No valid duration found in string")
    
    for value_str, unit_str in matches:
        try:
            value = float(value_str)
            if value <= 0:
                raise ValueError("Duration values must be positive")
                
            # Find matching unit
            unit_found = False
            for unit_key, multiplier in units.items():
                if unit_str.startswith(unit_key) or unit_key.startswith(unit_str):
                    total_minutes += value * multiplier
                    unit_found = True
                    break
            
            if not unit_found:
                # If unit not recognized, assume it's a number without unit (minutes)
                total_minutes += value
                
        except ValueError as e:
            raise ValueError(f"Invalid numeric value: {value_str}")
    
    if total_minutes <= 0:
        raise ValueError("Duration must be positive")
        
    return int(total_minutes)

# Modified to return all images for a task
def get_task_images(task_id: str):
    """Get all image filenames for a task"""
    from createandget import get_task
    from db import updates_col
    
    task = get_task(task_id)
    if not task:
        return []
    
    images = []
    for update_id in task['updates']:
        update = updates_col.find_one({"id": update_id})
        if update and update.get('image_filenames'):
            images.extend(update['image_filenames'])
            
    return images