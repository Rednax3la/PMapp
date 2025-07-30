# scheduling-api/helpers.py
import os
import uuid
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
    """Convert duration string to minutes"""
    minutes = 0
    parts = duration_str.lower().split()
    
    # Define conversion factors
    units = {
        'month': 30*24*60,
        'months': 30*24*60,
        'week': 7*24*60,
        'weeks': 7*24*60,
        'day': 24*60,
        'days': 24*60,
        'hour': 60,
        'hours': 60,
        'minute': 1,
        'minutes': 1
    }
    
    i = 0
    while i < len(parts):
        try:
            # Try to parse number
            value = int(parts[i])
            i += 1
            
            # Check if next part is a unit
            if i < len(parts) and parts[i] in units:
                unit = parts[i]
                minutes += value * units[unit]
                i += 1
            # Handle cases like "3 months" where unit comes after number
            elif i-2 >= 0 and parts[i-2] in units:
                unit = parts[i-2]
                minutes += value * units[unit]
        except ValueError:
            # Handle cases where unit comes before number (e.g., "months 3")
            if parts[i] in units and i+1 < len(parts):
                try:
                    value = int(parts[i+1])
                    minutes += value * units[parts[i]]
                    i += 2
                except ValueError:
                    i += 1
            else:
                i += 1
    
    if minutes <= 0:
        raise ValueError("Duration must be positive")
    return minutes

# Modified to return all images for a task
def get_task_images(task_id: int):
    from createandget import get_task, updates_db
    task = get_task(task_id)
    if not task:
        return []
    
    images = []
    for update_id in task['updates']:
        update = updates_db.get(update_id)
        if update and update.get('image_filenames'):
            images.extend(update['image_filenames'])
            
    return images