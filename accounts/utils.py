"""
Accounts Utilities - File Handling and Helper Functions

OOP Concept Demonstrated: FILE HANDLING IN OOP (TOPIC 7)
=======================================================================
This module demonstrates file handling using object-oriented principles.
The FileHandler class encapsulates all file-related operations, providing
a clean interface for saving images, validating files, and generating
unique filenames.

File handling in OOP involves:
1. Reading files (loading images, reading data)
2. Writing files (saving uploads, creating files)
3. File validation (checking types, sizes)
4. File manipulation (resizing, converting)

Benefits of OOP for file handling:
1. Encapsulation: File operations are bundled in a class
2. Reusability: FileHandler can be used throughout the project
3. Error handling: Centralized exception handling for file operations
4. Testing: Easy to mock/test file operations
=======================================================================
"""

import base64
import uuid
import os
from datetime import datetime
import pytz
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from ojt_project.exceptions import OJTValidationError


class FileHandler:
    """
    Utility class for handling file operations in the OJT system.

    OOP Concept: UTILITY CLASS
    -------------------------
    A utility class contains static methods and class methods that provide
    common functionality. These methods don't require instance state.

    Design Pattern: This follows the Utility/Helper pattern where related
    static methods are grouped in a class for organization.

    All methods are either @staticmethod or @classmethod because:
    1. They don't need instance-specific data (no self.something)
    2. They provide general-purpose file utilities
    3. They can be called without creating an instance: FileHandler.method()

    Usage examples:
        # Save a base64 image from webcam
        file = FileHandler.save_base64_image(base64_data)

        # Generate a unique filename
        filename = FileHandler.generate_unique_filename('jpg')

        # Validate an uploaded file
        FileHandler.validate_image(uploaded_file)
    """

    # CLASS CONSTANTS - shared configuration values
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 5MB
    
    # Philippine timezone
    PH_TIMEZONE = pytz.timezone('Asia/Manila')

    @staticmethod
    def save_base64_image(base64_data, prefix='image', add_timestamp=True):
        """
        Convert a base64 encoded image string to a Django ContentFile.
        Optionally adds a Philippine time timestamp overlay.

        OOP Concept: STATIC METHOD
        -------------------------
        This is a @staticmethod - it doesn't need access to any instance
        or class variables. It's a pure utility function that takes input
        and returns output.

        Static methods are used when:
        1. The method doesn't need 'self' (instance data)
        2. The method doesn't need 'cls' (class data)
        3. It's a utility that logically belongs to this class

        File Handling Concept:
        This demonstrates reading binary data (base64) and writing it
        as an image file. The base64 string comes from the browser's
        canvas.toDataURL() method when capturing webcam selfies.

        Args:
            base64_data (str): Base64 encoded image string
                Format: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
            prefix (str): Prefix for the generated filename
            add_timestamp (bool): Whether to add Philippine time timestamp

        Returns:
            ContentFile: Django file object that can be saved to ImageField

        Raises:
            OJTValidationError: If the base64 data is invalid

        Example:
            base64_string = "data:image/jpeg;base64,/9j/4AAQSkZ..."
            file = FileHandler.save_base64_image(base64_string, 'selfie')
            dtr_log.selfie.save(file.name, file)
        """
        try:
            # Parse the base64 data URL
            # Format: data:image/jpeg;base64,<actual_base64_data>
            if ';base64,' not in base64_data:
                raise OJTValidationError(
                    "Invalid image format. Expected base64 encoded image.",
                    "INVALID_IMAGE_FORMAT"
                )

            # Split into format info and actual data
            format_info, image_string = base64_data.split(';base64,')

            # Extract the file extension
            ext = FileHandler.get_file_extension(format_info)

            # Validate the extension
            if ext.lower() not in FileHandler.ALLOWED_IMAGE_EXTENSIONS:
                raise OJTValidationError(
                    f"Invalid image type '{ext}'. Allowed: {', '.join(FileHandler.ALLOWED_IMAGE_EXTENSIONS)}",
                    "INVALID_IMAGE_TYPE"
                )

            # Generate unique filename
            filename = FileHandler.generate_unique_filename(ext, prefix)

            # Decode base64 to binary
            image_data = base64.b64decode(image_string)
            
            # Add timestamp if requested
            if add_timestamp:
                image_data = FileHandler.add_timestamp_to_image(image_data)

            # Create Django ContentFile from binary data
            return ContentFile(image_data, name=filename)

        except (ValueError, TypeError) as e:
            raise OJTValidationError(
                f"Failed to process image: {str(e)}",
                "IMAGE_PROCESSING_ERROR"
            )

    @staticmethod
    def add_timestamp_to_image(image_data):
        """
        Add a Philippine time timestamp overlay to an image.
        
        Args:
            image_data (bytes): Raw image binary data
            
        Returns:
            bytes: Image data with timestamp overlay
        """
        try:
            # Open image from binary data
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Get current Philippine time
            ph_tz = pytz.timezone('Asia/Manila')
            ph_time = datetime.now(ph_tz)
            timestamp_text = ph_time.strftime("%B %d, %Y  %I:%M:%S %p")
            location_text = "Philippine Time (PHT)"
            
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Try to use a better font, fallback to default
            font_size = max(16, image.width // 30)  # Dynamic font size based on image width
            small_font_size = max(12, image.width // 40)
            
            try:
                # Try common Windows fonts
                font = ImageFont.truetype("arial.ttf", font_size)
                small_font = ImageFont.truetype("arial.ttf", small_font_size)
            except (IOError, OSError):
                try:
                    # Try common Linux fonts
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", small_font_size)
                except (IOError, OSError):
                    # Fallback to default font
                    font = ImageFont.load_default()
                    small_font = font
            
            # Calculate text positions (bottom-left corner with padding)
            padding = 10
            
            # Get text bounding boxes
            timestamp_bbox = draw.textbbox((0, 0), timestamp_text, font=font)
            location_bbox = draw.textbbox((0, 0), location_text, font=small_font)
            
            timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
            timestamp_height = timestamp_bbox[3] - timestamp_bbox[1]
            location_width = location_bbox[2] - location_bbox[0]
            location_height = location_bbox[3] - location_bbox[1]
            
            # Position at bottom-left
            timestamp_x = padding
            location_x = padding
            location_y = image.height - padding - location_height
            timestamp_y = location_y - timestamp_height - 5
            
            # Draw semi-transparent background rectangle
            bg_padding = 8
            bg_left = 0
            bg_top = timestamp_y - bg_padding
            bg_right = max(timestamp_width, location_width) + padding * 2 + bg_padding
            bg_bottom = image.height
            
            # Create overlay for semi-transparent background
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [bg_left, bg_top, bg_right, bg_bottom],
                fill=(0, 0, 0, 160)  # Semi-transparent black
            )
            
            # Composite the overlay onto the image
            image = image.convert('RGBA')
            image = Image.alpha_composite(image, overlay)
            image = image.convert('RGB')
            
            # Redraw text on composited image
            draw = ImageDraw.Draw(image)
            
            # Draw timestamp text (white with slight shadow for readability)
            # Shadow
            draw.text((timestamp_x + 1, timestamp_y + 1), timestamp_text, font=font, fill=(0, 0, 0))
            # Main text
            draw.text((timestamp_x, timestamp_y), timestamp_text, font=font, fill=(255, 255, 255))
            
            # Draw location text
            draw.text((location_x + 1, location_y + 1), location_text, font=small_font, fill=(0, 0, 0))
            draw.text((location_x, location_y), location_text, font=small_font, fill=(255, 200, 0))  # Yellow
            
            # Save to bytes
            output = BytesIO()
            image.save(output, format='JPEG', quality=90)
            return output.getvalue()
            
        except Exception as e:
            # If timestamp fails, return original image
            print(f"Warning: Could not add timestamp to image: {e}")
            return image_data

    @staticmethod
    def get_file_extension(format_string):
        """
        Extract file extension from a MIME type format string.

        OOP Concept: SINGLE RESPONSIBILITY
        ---------------------------------
        This method has ONE job: extract the extension from a format string.
        This follows the Single Responsibility Principle (SRP).

        Args:
            format_string (str): MIME type string like "data:image/jpeg"

        Returns:
            str: File extension (e.g., "jpeg", "png")
        """
        # "data:image/jpeg" -> "jpeg"
        # "data:image/png" -> "png"
        return format_string.split('/')[-1].lower()

    @staticmethod
    def generate_unique_filename(extension, prefix='file'):
        """
        Generate a unique filename using UUID.

        OOP Concept: UTILITY METHOD
        --------------------------
        This is a helper method that generates unique filenames to prevent
        file name collisions when multiple users upload files.

        File Handling: Demonstrates proper file naming practices:
        1. Unique names prevent overwriting
        2. Predictable format for organization
        3. Extension preserved for proper file handling

        Args:
            extension (str): File extension without dot (e.g., "jpg")
            prefix (str): Prefix for the filename (e.g., "selfie", "profile")

        Returns:
            str: Unique filename like "selfie_550e8400-e29b-41d4-a716-446655440000.jpg"
        """
        unique_id = uuid.uuid4()
        return f"{prefix}_{unique_id}.{extension}"

    @classmethod
    def validate_image(cls, uploaded_file):
        """
        Validate an uploaded image file.

        OOP Concept: CLASS METHOD
        ------------------------
        This is a @classmethod - it receives the class as the first argument (cls)
        instead of an instance (self). This allows access to class-level attributes
        like ALLOWED_IMAGE_EXTENSIONS and MAX_FILE_SIZE_BYTES.

        Class methods are used when:
        1. You need to access class variables (cls.ALLOWED_IMAGE_EXTENSIONS)
        2. You want to create alternative constructors
        3. The method logically belongs to the class but doesn't need instance data

        Args:
            uploaded_file: Django UploadedFile object

        Raises:
            OJTValidationError: If file is invalid

        Example:
            try:
                FileHandler.validate_image(request.FILES['profile_pic'])
            except OJTValidationError as e:
                messages.error(request, str(e))
        """
        if not uploaded_file:
            return  # No file uploaded is OK (optional field)

        # Check file size
        if uploaded_file.size > cls.MAX_FILE_SIZE_BYTES:
            raise OJTValidationError(
                f"File too large. Maximum size is {cls.MAX_FILE_SIZE_MB}MB.",
                "FILE_TOO_LARGE"
            )

        # Check file extension
        ext = os.path.splitext(uploaded_file.name)[1].lower().strip('.')
        if ext not in cls.ALLOWED_IMAGE_EXTENSIONS:
            raise OJTValidationError(
                f"Invalid file type '{ext}'. Allowed: {', '.join(cls.ALLOWED_IMAGE_EXTENSIONS)}",
                "INVALID_FILE_TYPE"
            )

        # Verify it's actually an image using Pillow
        try:
            # This demonstrates FILE READING - opening and parsing an image file
            image = Image.open(uploaded_file)
            image.verify()  # Verify it's a valid image
            uploaded_file.seek(0)  # Reset file pointer after reading
        except Exception:
            raise OJTValidationError(
                "Invalid or corrupted image file.",
                "CORRUPTED_IMAGE"
            )

    @staticmethod
    def resize_image(image_file, max_width=800, max_height=800, quality=85):
        """
        Resize an image to maximum dimensions while maintaining aspect ratio.

        OOP Concept: IMAGE PROCESSING
        ----------------------------
        This method demonstrates more advanced file handling:
        1. Reading an image file into memory
        2. Processing it (resizing)
        3. Writing it back to a file-like object

        Args:
            image_file: File-like object containing the image
            max_width (int): Maximum width in pixels
            max_height (int): Maximum height in pixels
            quality (int): JPEG quality (1-100)

        Returns:
            BytesIO: File-like object containing the resized image
        """
        # Open the image file
        image = Image.open(image_file)

        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')

        # Calculate new dimensions maintaining aspect ratio
        width, height = image.size
        ratio = min(max_width / width, max_height / height)

        if ratio < 1:  # Only resize if image is larger than max dimensions
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Save to BytesIO object
        output = BytesIO()
        image.save(output, format='JPEG', quality=quality)
        output.seek(0)

        return output


"""
FILE HANDLING EXAMPLES (Topic 7):
================================

1. Reading a file:
   with open('data.txt', 'r') as f:
       content = f.read()

2. Writing a file:
   with open('output.txt', 'w') as f:
       f.write('Hello, World!')

3. Binary file operations:
   with open('image.jpg', 'rb') as f:  # 'rb' for reading binary
       data = f.read()

4. Using context managers (with statement):
   - Automatically closes file when done
   - Handles exceptions properly
   - Best practice for file handling

5. In Django, file handling is abstracted:
   - FileField and ImageField handle storage
   - ContentFile wraps binary data
   - File.open() and File.close() managed automatically
"""
