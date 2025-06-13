import streamlit as st
import os
import requests
from PIL import Image
from io import BytesIO

# --- Core Functions (Corrected) ---

Image.MAX_IMAGE_PIXELS = None # Set to None for no limit, or a sufficiently large integer like 2_000_000_000


def download_tiles(base_url, map_name, version, zoom_level, x_range, y_range, progress_bar):
    """
    Downloads the map tiles from the server.
    Saves tiles with unique names to prevent cache conflicts between maps.
    """
    tiles_dir = "tiles"
    os.makedirs(tiles_dir, exist_ok=True)
    
    total_tiles = len(x_range) * len(y_range)
    status_text = st.empty()
    
    downloaded_count = 0
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            # CORRECTED: Added map_name to the filename for unique caching
            tile_filename = f"{tiles_dir}/{map_name}_{zoom_level}_{x}_{y}.webp"
            
            # Skip if already downloaded
            if os.path.exists(tile_filename):
                downloaded_count += 1
                progress_bar.progress(downloaded_count / total_tiles)
                status_text.text(f"Tile {x},{y} for {map_name} already exists. Skipping...")
                continue
            
            # Format the URL with the selected map and version
            url = f"{base_url.format(map_name=map_name, version=version)}{zoom_level}/{x}/{y}.webp"
            
            try:
                status_text.text(f"Downloading tile {x},{y} for {map_name}...")
                response = requests.get(url)
                response.raise_for_status()
                with open(tile_filename, "wb") as f:
                    f.write(response.content)
                
            except requests.exceptions.RequestException as e:
                st.warning(f"Failed to download tile {x},{y}: {e}")
            
            finally:
                downloaded_count += 1
                progress_bar.progress(downloaded_count / total_tiles)

    status_text.text("Download complete!")


def stitch_tiles(map_name, zoom_level, x_range, y_range, tile_size=256):
    """
    Stitches the downloaded tiles into a single image.
    Looks for tiles with unique names matching the selected map.
    """
    # Note: The output dimensions depend on the order of iteration.
    # The outer loop is over y, inner is over x, so width is determined by x_range.
    output_width = len(x_range) * tile_size
    output_height = len(y_range) * tile_size
    output_image = Image.new("RGBA", (output_width, output_height))

    for y_index, y in enumerate(y_range):
        for x_index, x in enumerate(x_range):
            # CORRECTED: Added map_name to the path to load the correct tile
            tile_path = f"tiles/{map_name}_{zoom_level}_{x}_{y}.webp"
            if os.path.exists(tile_path):
                try:
                    tile_image = Image.open(tile_path).convert("RGBA")
                    # The paste location depends on the iteration order.
                    output_image.paste(tile_image, (x_index * tile_size, y_index * tile_size))
                except Exception as e:
                    st.error(f"Failed to open or paste tile {x},{y}: {e}")
            else:
                st.warning(f"Tile not found: {tile_path}. It will be a blank space.")

    return output_image


# --- Streamlit Application ---

st.set_page_config(page_title="DayZ Map Downloader", layout="wide", page_icon="🗺️")

st.title("🗺️ DayZ Map Downloader")
st.markdown("This tool downloads and stitches map tiles from an online source to create a full high-resolution map image for the game DayZ.")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("⚙️ Map Configuration")

    map_options = {
        "ChernarusPlus-Top": "1.26.0",
        "ChernarusPlus-Sat": "1.26.0",
        "Livonia-Top": "1.26.0",
        "Livonia-Sat": "1.26.0",
        "Sakhal-Top": "1.3.0",
        "Sakhal-Sat": "1.3.0",
    }
    
    map_name = st.selectbox(
        "Select Map",
        options=list(map_options.keys()),
        help="Choose the game map and style (Topographical or Satellite)."
    )

    version = st.text_input(
        "Map Version",
        value=map_options[map_name],
        help="The version number of the map. It's updated automatically when you select a map."
    )
    
    zoom_level = st.selectbox(
        "Select Zoom Level",
        options=[1, 2, 3, 4, 5, 6, 7],
        index=3, 
        help="Higher zoom levels provide more detail but result in a larger image and longer download time."
    )

    # --- ADJUSTED SECTION: DYNAMIC RANGE INFO ---
    # Define the mapping from zoom level to the grid size (N for an NxN grid)
    zoom_to_grid_size = {
        1: 2,  # 2x2
        2: 4,  # 4x4
        3: 8,  # 8x8
        4: 16, # 16x16
        5: 32, # 32x32
        6: 64, # 64x64
        7: 128 # 128x128
    }
    # --- END ADJUSTED SECTION ---

    run_button = st.button("Generate Map", type="primary")

# --- Main Application Area ---
# Check if the run button was clicked OR if a map is already in session state (e.g., after a rerun)
if run_button:
    # Clear session state for map image and filename when new generation starts
    # This ensures the download section is removed until a new map is generated
    if 'map_image' in st.session_state:
        del st.session_state['map_image']
    if 'map_filename' in st.session_state:
        del st.session_state['map_filename']

    with st.spinner('Processing... Please wait.'):
        base_url = "https://maps.izurvive.com/maps/{map_name}/{version}/tiles/"
        
        # --- ADJUSTED SECTION: DYNAMIC RANGE CALCULATION ---
        # Get the grid size (e.g., 15 for a 15x15 grid) from the mapping
        grid_size = zoom_to_grid_size.get(zoom_level)

        # Assuming 0-based indexing for tile coordinates to include (0,0)
        if grid_size:
            x_range = range(0, grid_size)
            y_range = range(0, grid_size)
        else:
            # Fallback for safety, though the selectbox options are controlled
            st.error(f"Invalid zoom level: {zoom_level}. Using default range of 16x16.") # Updated fallback
            x_range = range(0, 16)
            y_range = range(0, 16)
        # --- END ADJUSTED SECTION ---

        st.subheader("1. Downloading Tiles")
        progress_bar = st.progress(0)
        download_tiles(base_url, map_name, version, zoom_level, x_range, y_range, progress_bar)
        
        st.subheader("2. Stitching Tiles")
        # CORRECTED: Pass ranges in the correct order (x then y)
        stitched_image = stitch_tiles(map_name, zoom_level, x_range, y_range)
        
        st.subheader("3. Generated Map")
        st.image(stitched_image, caption=f"Generated Map: {map_name} (Zoom: {zoom_level})", use_container_width=True)
        
        st.session_state['map_image'] = stitched_image
        st.session_state['map_filename'] = f"DayZ_Map_{map_name}_{zoom_level}.png"

# Display download section only if a map has been generated and is in session state
if 'map_image' in st.session_state:
    st.subheader("4. Download")
    
    buf = BytesIO()
    st.session_state.map_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="Download Map Image",
        data=byte_im,
        file_name=st.session_state.map_filename,
        mime="image/png",
        type="primary"
    )

st.sidebar.markdown("---")
# give credit to https://dayz.ginfo.gg/about/ (iSurvive) for the map data
st.sidebar.markdown("Map data provided by [iSurvive DayZ](https://dayz.ginfo.gg/about/).")