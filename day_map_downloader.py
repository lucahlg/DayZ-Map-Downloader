import streamlit as st
import os
import requests
from PIL import Image
from io import BytesIO

# --- Core Functions ---

# Set to None for no limit, or a sufficiently large integer like 2_000_000_000
Image.MAX_IMAGE_PIXELS = None 


def download_tiles(base_url, map_name, version, zoom_level, x_range, y_range, progress_bar):
    """
    Downloads the map tiles from the server.
    Saves tiles with unique names to prevent cache conflicts between maps.
    """
    tiles_dir = "tiles"
    # Create the 'tiles' directory if it doesn't exist
    os.makedirs(tiles_dir, exist_ok=True)
    
    total_tiles = len(x_range) * len(y_range)
    status_text = st.empty() # Placeholder for status messages
    
    downloaded_count = 0
    # Iterate through x and y coordinates to download each tile
    for i, x in enumerate(x_range):
        for j, y in enumerate(y_range):
            # Construct a unique filename for the tile using map name, zoom, x, and y
            tile_filename = f"{tiles_dir}/{map_name}_{zoom_level}_{x}_{y}.webp"
            
            # Skip downloading if the tile already exists locally
            if os.path.exists(tile_filename):
                downloaded_count += 1
                progress_bar.progress(downloaded_count / total_tiles)
                status_text.text(f"Tile {x},{y} for {map_name} already exists. Skipping...")
                continue
            
            # Format the URL for the specific tile
            url = f"{base_url.format(map_name=map_name, version=version)}{zoom_level}/{x}/{y}.webp"
            
            try:
                status_text.text(f"Downloading tile {x},{y} for {map_name}...")
                response = requests.get(url)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                # Save the downloaded tile content to the file
                with open(tile_filename, "wb") as f:
                    f.write(response.content)
                
            except requests.exceptions.RequestException as e:
                # Display a warning if a tile fails to download
                st.warning(f"Failed to download tile {x},{y}: {e}")
            
            finally:
                downloaded_count += 1
                # Update the progress bar after each tile (downloaded or skipped)
                progress_bar.progress(downloaded_count / total_tiles)

    status_text.text("Download complete!")


def stitch_tiles(map_name, zoom_level, x_range, y_range, tile_size=256):
    """
    Stitches the downloaded tiles into a single image.
    Looks for tiles with unique names matching the selected map.
    """
    # Calculate the total width and height of the output image
    output_width = len(x_range) * tile_size
    output_height = len(y_range) * tile_size
    # Create a new blank RGBA image to paste tiles onto
    output_image = Image.new("RGBA", (output_width, output_height))

    # Iterate through y and x ranges to stitch tiles in the correct order
    for y_index, y in enumerate(y_range):
        for x_index, x in enumerate(x_range):
            # Construct the expected path for the tile file
            tile_path = f"tiles/{map_name}_{zoom_level}_{x}_{y}.webp"
            if os.path.exists(tile_path):
                try:
                    # Open the tile image and convert it to RGBA
                    tile_image = Image.open(tile_path).convert("RGBA")
                    # Calculate the paste coordinates based on tile index
                    output_image.paste(tile_image, (x_index * tile_size, y_index * tile_size))
                except Exception as e:
                    st.error(f"Failed to open or paste tile {x},{y}: {e}")
            else:
                # Warn if a tile is missing, resulting in a blank space
                st.warning(f"Tile not found: {tile_path}. It will be a blank space.")

    return output_image


# --- Streamlit Application ---

# Configure the Streamlit page
st.set_page_config(page_title="DayZ Map Downloader", layout="wide", page_icon="🗺️")

st.title("🗺️ DayZ Map Downloader")
st.markdown("This tool downloads and stitches map tiles from an online source to create a full high-resolution map image for the game DayZ.")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("⚙️ Map Configuration")

    # Dictionary of available maps and their default versions
    map_options = {
        "ChernarusPlus-Top": "1.26.0",
        "ChernarusPlus-Sat": "1.26.0",
        "Livonia-Top": "1.26.0",
        "Livonia-Sat": "1.26.0",
        "Sakhal-Top": "1.3.0",
        "Sakhal-Sat": "1.3.0",
    }
    
    # Dropdown for selecting the map
    map_name = st.selectbox(
        "Select Map",
        options=list(map_options.keys()),
        help="Choose the game map and style (Topographical or Satellite)."
    )

    # Text input for map version, pre-filled based on selected map
    version = st.text_input(
        "Map Version",
        value=map_options[map_name],
        help="The version number of the map. It's updated automatically when you select a map."
    )
    
    # Define the mapping from zoom level (internal) to grid size (N for NxN grid)
    zoom_level_to_grid_size = {
        1: 2,   # 2x2 grid
        2: 4,   # 4x4 grid
        3: 8,   # 8x8 grid
        4: 16,  # 16x16 grid
        5: 32,  # 32x32 grid
        6: 64,  # 64x64 grid
        7: 128  # 128x128 grid
    }

    # Calculate resolutions and create options for the dropdown
    resolution_options = []
    # Store a mapping from resolution string back to zoom level
    resolution_to_zoom_map = {} 
    tile_size = 256 # Defined in stitch_tiles function, used here for consistency

    # Populate resolution options for the selectbox
    for zoom_level, grid_size in zoom_level_to_grid_size.items():
        width = grid_size * tile_size
        height = grid_size * tile_size
        resolution_str = f"{width}px x {height}px"
        resolution_options.append(resolution_str)
        resolution_to_zoom_map[resolution_str] = zoom_level

    # Dropdown for selecting the resolution
    selected_resolution_str = st.selectbox(
        "Select Resolution",
        options=resolution_options,
        index=3, # Default to 4096px x 4096px (which corresponds to zoom 4)
        help="Higher resolutions provide more detail but result in a larger image and longer download time."
    )
    
    # Get the actual zoom level from the selected resolution string
    zoom_level = resolution_to_zoom_map[selected_resolution_str]

    # Button to trigger map generation
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
        
        # Get the grid size based on the determined zoom level
        grid_size = zoom_level_to_grid_size.get(zoom_level)

        # Assuming 0-based indexing for tile coordinates to include (0,0)
        if grid_size:
            x_range = range(0, grid_size)
            y_range = range(0, grid_size)
        else:
            # Fallback for safety, though the selectbox options are controlled
            st.error(f"Invalid zoom level determined for resolution: {selected_resolution_str}. Using default range of 16x16.")
            x_range = range(0, 16)
            y_range = range(0, 16)

        st.subheader("1. Downloading Tiles")
        progress_bar = st.progress(0)
        # Call the download function
        download_tiles(base_url, map_name, version, zoom_level, x_range, y_range, progress_bar)
        
        st.subheader("2. Stitching Tiles")
        # Call the stitching function
        stitched_image = stitch_tiles(map_name, zoom_level, x_range, y_range)
        
        st.subheader("3. Generated Map")
        # Display the generated image
        st.image(stitched_image, caption=f"Generated Map: {map_name} (Resolution: {selected_resolution_str})", use_container_width=True)
        
        # Store the image and filename in session state for download persistence
        st.session_state['map_image'] = stitched_image
        st.session_state['map_filename'] = f"DayZ_Map_{map_name}_{selected_resolution_str.replace(' ', '')}.png"

# Display download section only if a map has been generated and is in session state
if 'map_image' in st.session_state:
    st.subheader("4. Download")
    
    # Convert the PIL image to bytes for downloading
    buf = BytesIO()
    st.session_state.map_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    # Download button for the generated map
    st.download_button(
        label="Download Map Image",
        data=byte_im,
        file_name=st.session_state.map_filename,
        mime="image/png",
        type="primary"
    )

st.sidebar.markdown("---")
# Give credit for the map data
st.sidebar.markdown("Map data provided by [iZurvive DayZ](https://dayz.ginfo.gg/about/).")
