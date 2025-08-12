"""
IpySwiper: A reusable interactive image gallery component for Jupyter Notebooks.

This component provides an interactive image gallery with:
- Main image display with optional fade effects
- Scrollable thumbnail strip
- Keyboard navigation support
- Multiple instances support without conflicts
- Standalone HTML export capability
"""

__version__ = "0.1.0"

import json
import uuid
import os
import base64
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from IPython.display import HTML
from jinja2 import Template


class IpySwiper:
    """
    Interactive image gallery component for Jupyter Notebooks.
    
    Features:
    - Displays a main image with thumbnail navigation
    - Supports keyboard navigation (arrow keys)
    - Can be used multiple times in the same notebook
    - Exports to standalone HTML files
    """
    
    def __init__(self, images: List[Dict[str, str]], transition_speed: int = 0, transition_effect: str = 'slide',
                 container_height: int = 600, thumbnail_panel_width: int = 200, thumbnails_per_view: int = 4, thumbnail_fit: str = 'contain', show_labels: bool = True, use_base64: bool = False, base_path: str = ""):
        """
        Initialize the gallery with image data.
        
        Args:
            images: List of dictionaries with 'label' and 'image' keys.
                   Example: [{'label': 'Image 1', 'image': 'path/to/image1.jpg'}]
            transition_speed: Transition speed in milliseconds. Default is 0 (no transition).
            transition_effect: Swiper transition effect. Options: 'slide', 'fade', 'cube', 'coverflow', 'flip'.
                              Default is 'slide'.
            container_height: Height of the gallery container in pixels. Default is 600.
            thumbnail_panel_width: Width of the thumbnail panel in pixels. Default is 200.
            thumbnails_per_view: Number of thumbnails visible at once in the thumbnail strip.
                                Controls the size of individual thumbnails. Default is 4.
            thumbnail_fit: How thumbnails should fit in their container. Options: 'cover', 'contain', 'fill'.
                          Default is 'cover'.
            show_labels: Whether to show image labels on thumbnails. Default is False.
            use_base64: Whether to convert images to base64 data URIs for standalone HTML. Default is False.
            base_path: Base path to prepend to relative image paths when converting to base64. Default is "".
        """
        if not images:
            raise ValueError("Images list cannot be empty")
        
        # Validate image data structure
        for i, img in enumerate(images):
            if not isinstance(img, dict):
                raise ValueError(f"Image {i} must be a dictionary")
            if 'label' not in img or 'image' not in img:
                raise ValueError(f"Image {i} must have 'label' and 'image' keys")
        
        self.images = images
        self.transition_speed = transition_speed
        self.transition_effect = transition_effect
        self.container_height = container_height
        self.thumbnail_panel_width = thumbnail_panel_width
        self.thumbnails_per_view = thumbnails_per_view
        self.thumbnail_fit = thumbnail_fit
        self.show_labels = show_labels
        self.use_base64 = use_base64
        self.base_path = base_path
        self.unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        self._template_path = Path(__file__).parent / 'templates' / 'gallery_template.html'
        self._standalone_template_path = Path(__file__).parent / 'templates' / 'standalone_template.html'
        
        # Prepend base_path to image paths
        if self.base_path:
            for img in self.images:
                img['image'] = os.path.join(self.base_path, img['image'])

        # Convert images to base64 if requested
        if self.use_base64:
            self.images = self._convert_images_to_base64(self.images)
    
    def _load_template(self, template_path: Path) -> Template:
        """Load and return a Jinja2 template."""
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        return Template(template_content)
    
    def _render_gallery(self) -> str:
        """Render the gallery HTML content."""
        template = self._load_template(self._template_path)
        
        # Prepare template variables
        template_vars = {
            'unique_id': self.unique_id,
            'images': self.images,
            'images_json': json.dumps(self.images),
            'transition_speed': self.transition_speed,
            'transition_effect': self.transition_effect,
            'container_height': self.container_height,
            'thumbnail_panel_width': self.thumbnail_panel_width,
            'thumbnails_per_view': self.thumbnails_per_view,
            'thumbnail_fit': self.thumbnail_fit,
            'show_labels': self.show_labels
        }
        
        return template.render(**template_vars)
    
    def _ipython_display_(self) -> None:
        """
        Display the gallery in a Jupyter notebook cell.
        This method is automatically called when the object is displayed.
        """
        gallery_html = self._render_gallery()
        
        # Add Swiper.js CDN if not already included
        swiper_cdn = '''
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
        <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
        '''
        
        full_html = swiper_cdn + gallery_html
        
        # Display the HTML content
        from IPython.display import display
        display(HTML(full_html))
    
    def save_to_html(self, filepath: str, title: str = "Image Gallery") -> None:
        """
        Save the gallery as a standalone HTML file.
        
        Args:
            filepath: Path where the HTML file will be saved
            title: Title for the HTML page
        """
        # Render the gallery content
        gallery_content = self._render_gallery()
        
        # Load the standalone template
        standalone_template = self._load_template(self._standalone_template_path)
        
        # Render the complete HTML page
        full_html = standalone_template.render(
            title=title,
            gallery_content=gallery_content
        )
        
        # Write to file
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"Gallery saved to: {output_path.absolute()}")
    
    def add_image(self, label: str, image: str) -> None:
        """
        Add a new image to the gallery.
        
        Args:
            label: Label/description for the image
            image: Path or URL to the image
        """
        self.images.append({'label': label, 'image': image})
    
    def remove_image(self, index: int) -> None:
        """
        Remove an image from the gallery by index.
        
        Args:
            index: Index of the image to remove
        """
        if 0 <= index < len(self.images):
            self.images.pop(index)
        else:
            raise IndexError(f"Image index {index} out of range")
    
    def get_image_count(self) -> int:
        """Get the number of images in the gallery."""
        return len(self.images)
    
    def get_images(self) -> List[Dict[str, str]]:
        """Get a copy of the images list."""
        return self.images.copy()
    
    def _image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Convert an image file to base64 data URI.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 data URI string or None if conversion fails
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            if mime_type is None:
                # Default to common image types
                ext = Path(image_path).suffix.lower()
                mime_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.webp': 'image/webp'
                }
                mime_type = mime_map.get(ext, 'image/jpeg')
            
            # Read and encode the image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Create data URI
            data_uri = f"data:{mime_type};base64,{base64_data}"
            
            print(f"✅ Converted to base64: {image_path} ({len(base64_data)} chars)")
            return data_uri
            
        except Exception as e:
            print(f"❌ Error converting {image_path} to base64: {e}")
            return None
    
    def _convert_images_to_base64(self, images: List[Dict[str, str]], base_path: str = "") -> List[Dict[str, str]]:
        """
        Convert all image paths in the images list to base64 data URIs.
        
        Args:
            images: List of image dictionaries
            base_path: Base path to prepend to relative image paths
            
        Returns:
            List of image dictionaries with base64 data URIs
        """
        converted_images = []
        
        for i, img in enumerate(images):
            print(f"🔄 Processing image {i+1}/{len(images)}: {img['label']}")
            
            image_path = img['image']
            
            # Skip if already a data URI
            if image_path.startswith('data:'):
                print(f"  ℹ️  Already a data URI, skipping conversion")
                converted_images.append(img.copy())
                continue
            
            # Handle relative paths
            if base_path and not os.path.isabs(image_path):
                full_path = os.path.join(base_path, image_path)
            else:
                full_path = image_path
            
            # Convert to base64
            base64_uri = self._image_to_base64(full_path)
            
            if base64_uri:
                converted_img = img.copy()
                converted_img['image'] = base64_uri
                converted_images.append(converted_img)
            else:
                print(f"  ⚠️  Skipping image due to conversion error")
        
        print(f"✅ Successfully converted {len(converted_images)}/{len(images)} images")
        return converted_images
    
    def convert_to_base64(self, base_path: str = "") -> None:
        """
        Convert all images in the gallery to base64 data URIs.
        This can be called after initialization to convert images on demand.
        
        Args:
            base_path: Base path to prepend to relative image paths
        """
        self.images = self._convert_images_to_base64(self.images, base_path or self.base_path)
        self.use_base64 = True
    
    @staticmethod
    def load_images_from_json(json_path: str) -> Optional[List[Dict[str, str]]]:
        """
        Load image data from JSON file.
        
        Expected JSON format:
        [
            {
                "label": "Image description",
                "image": "path/to/image.jpg"
            },
            ...
        ]
        
        Args:
            json_path: Path to JSON file containing image data
            
        Returns:
            List of image dictionaries with 'label' and 'image' keys, or None if loading fails
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✅ Successfully loaded {len(data)} images from {json_path}")
            return data
            
        except FileNotFoundError:
            print(f"❌ JSON file not found: {json_path}")
            print("💡 Make sure the JSON file exists and contains image data")
            return None
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format in {json_path}: {e}")
            return None
    
    @classmethod
    def from_json(cls, json_path: str, use_base64: bool = False, base_path: str = "", **kwargs) -> Optional['IpySwiper']:
        """
        Create a IpySwiper instance from a JSON file.
        
        Args:
            json_path: Path to JSON file containing image data
            use_base64: Whether to convert images to base64 data URIs
            base_path: Base path to prepend to relative image paths when converting to base64
            **kwargs: Additional arguments to pass to IpySwiper constructor
            
        Returns:
            IpySwiper instance or None if loading fails
        """
        images = cls.load_images_from_json(json_path)
        if images is None:
            return None
        
        return cls(images, use_base64=use_base64, base_path=base_path, **kwargs)
    
    def __repr__(self) -> str:
        """String representation of the gallery."""
        return f"IpySwiper(images={len(self.images)}, id='{self.unique_id}')"
    
    def __len__(self) -> int:
        """Return the number of images in the gallery."""
        return len(self.images)


# Convenience function for quick gallery creation
def create_swiper(images: List[Dict[str, str]], use_base64: bool = False, base_path: str = "", **kwargs) -> IpySwiper:
    """
    Convenience function to create a IpySwiper instance.
    
    Args:
        images: List of image dictionaries
        use_base64: Whether to convert images to base64 data URIs
        base_path: Base path to prepend to relative image paths when converting to base64
        **kwargs: Additional arguments to pass to IpySwiper constructor
        
    Returns:
        IpySwiper instance
    """
    return IpySwiper(images, use_base64=use_base64, base_path=base_path, **kwargs)


# Example usage and testing
if __name__ == "__main__":
    # Example image data
    sample_images = [
        {
            "label": "Sample Image 1",
            "image": "https://picsum.photos/800/600?random=1"
        },
        {
            "label": "Sample Image 2", 
            "image": "https://picsum.photos/800/600?random=2"
        },
        {
            "label": "Sample Image 3",
            "image": "https://picsum.photos/800/600?random=3"
        }
    ]
    
    # Create gallery
    gallery = IpySwiper(sample_images)
    print(f"Created gallery: {gallery}")
    
    # Test saving to HTML
    gallery.save_to_html("test_gallery.html", "Test Image Gallery")
    print("Test completed successfully!")
