#!/usr/bin/env python3
"""
Demo script showing how to use JupyterGallery class to create a page similar to index.html
"""

from ipyswiper import IpySwiper

# Sample image data (same as in the dev script)
sample_images = [
    {
        "label": "Mountain Lake",
        "image": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiM4N0NFRUIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM0NjgyQjQiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2cpIi8+PHBvbHlnb24gcG9pbnRzPSIwLDQwMCA0MDAsMjAwIDgwMCwzMDAgODAwLDYwMCAwLDYwMCIgZmlsbD0iIzJFOEI1NyIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMzYiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+TW91bnRhaW4gTGFrZTwvdGV4dD48L3N2Zz4="
    },
    {
        "label": "Forest Path",
        "image": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiM2OEQ0NTMiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMyRTdEMzIiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2cpIi8+PGVsbGlwc2UgY3g9IjIwMCIgY3k9IjE1MCIgcng9IjgwIiByeT0iMTIwIiBmaWxsPSIjMjI3MjI3Ii8+PGVsbGlwc2UgY3g9IjYwMCIgY3k9IjEwMCIgcng9IjEwMCIgcnk9IjE0MCIgZmlsbD0iIzFCNUIxRiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMzYiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+Rm9yZXN0IFBhdGg8L3RleHQ+PC9zdmc+"
    },
    {
        "label": "Ocean View", 
        "image": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiM4N0NFRUIiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwMDY5OEMiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2cpIi8+PHBhdGggZD0iTTAgNDAwIFEgMjAwIDM1MCA0MDAgMzgwIFQgODAwIDM2MCA4MDAgNjAwIDAgNjAwIFoiIGZpbGw9IiMwMDc4QUEiLz48Y2lyY2xlIGN4PSI3MDAiIGN5PSIxMDAiIHI9IjYwIiBmaWxsPSIjRkZEQjAwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIzNiIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5PY2VhbiBWaWV3PC90ZXh0Pjwvc3ZnPg=="
    },
    {
        "label": "Desert Landscape",
        "image": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkQ3MDAiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiNGRjg5MDAiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2cpIi8+PGVsbGlwc2UgY3g9IjIwMCIgY3k9IjQ1MCIgcng9IjE1MCIgcnk9IjgwIiBmaWxsPSIjRDI2OTFEIi8+PGVsbGlwc2UgY3g9IjYwMCIgY3k9IjQwMCIgcng9IjIwMCIgcnk9IjEwMCIgZmlsbD0iI0NBNUQxNiIvPjxjaXJjbGUgY3g9IjcwMCIgY3k9IjgwIiByPSI1MCIgZmlsbD0iI0ZGRkZGRiIgb3BhY2l0eT0iMC44Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIzNiIgZmlsbD0iIzMzMzMzMyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRlc2VydCBMYW5kc2NhcGU8L3RleHQ+PC9zdmc+"
    },
    {
        "label": "City Skyline",
        "image": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImciIHgxPSIwJSIgeTE9IjAlIiB4Mj0iMTAwJSIgeTI9IjEwMCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiM2QzVCN0IiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMzNTQ3NTgiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJ1cmwoI2cpIi8+PHJlY3QgeD0iNTAiIHk9IjMwMCIgd2lkdGg9IjgwIiBoZWlnaHQ9IjMwMCIgZmlsbD0iIzM0NDk1RSIvPjxyZWN0IHg9IjE1MCIgeT0iMjAwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjQwMCIgZmlsbD0iIzM0NDk1RSIvPjxyZWN0IHg9IjMwMCIgeT0iMTUwIiB3aWR0aD0iMTIwIiBoZWlnaHQ9IjQ1MCIgZmlsbD0iIzJDM0U1MCIvPjxyZWN0IHg9IjUwMCIgeT0iMjUwIiB3aWR0aD0iOTAiIGhlaWdodD0iMzUwIiBmaWxsPSIjMzQ0OTVFIi8+PHJlY3QgeD0iNjUwIiB5PSIxMDAiIHdpZHRoPSIxMDAiIGhlaWdodD0iNTAwIiBmaWxsPSIjMkMzRTUwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIzNiIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5DaXR5IFNreWxpbmU8L3RleHQ+PC9zdmc+"
    }
]

def main():
    """Create and save a gallery page similar to index.html"""
    
    # Create gallery instance
    gallery = IpySwiper(sample_images)
    
    # Save as standalone HTML (similar to index.html)
    output_file = "gallery_demo.html"
    gallery.save_to_html(output_file, title="JupyterGallery Demo - Image Gallery")
    
    print(f"Gallery page created: {output_file}")
    print("This page includes:")
    print("- Interactive image gallery with focus-based keyboard navigation")
    print("- Mouse navigation with next/prev buttons")
    print("- Thumbnail panel with vertical scrolling")
    print("- All the functionality from the dev environment")
    
    return gallery

if __name__ == "__main__":
    gallery = main()
