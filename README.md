# DayZ Map Downloader 🗺️

This Streamlit application allows you to download and stitch together high-resolution map tiles from online sources to create full, detailed maps for the game DayZ. Whether you need a topographical overview or a satellite image, this tool simplifies the process of generating your desired map.

-----

## Features ✨

  * **Multiple Map Support**: Select from various DayZ maps like ChernarusPlus and Livonia, including both topographical and satellite views.
  * **Adjustable resolution**: Choose your desired resolution of the generated map between 7 different levels.
  * **Tile Downloading with Progress**: Downloads individual map tiles efficiently, skipping already downloaded tiles and showing a progress bar.
  * **Seamless Tile Stitching**: Automatically combines all downloaded tiles into a single, large image.
  * **Direct Download**: Easily download the generated map as a PNG image.
  * **Unique Caching**: Tiles are saved with unique names based on the map and zoom level, preventing conflicts and improving performance for repeat downloads.


 ![DayZ Map Downloader Screenshot](src\screenshot-1.png)

-----

## How it Works ⚙️

The application functions by:

1.  **Selecting Map Parameters**: You choose the desired map (e.g., ChernarusPlus-Top), its version, and the resolution level from the sidebar.
2.  **Downloading Tiles**: The app connects to `maps.izurvive.com` to download individual map tiles based on your selections. It stores these tiles locally in a `tiles/` directory.
3.  **Stitching Images**: Once all tiles are downloaded, the application stitches them together into a single, large image.
4.  **Display & Download**: The final stitched map is displayed in the application, and you're provided with a button to download it.

-----

## Getting Started 🚀

Follow these instructions to get your local copy up and running.

### Prerequisites

Make sure you have Python installed (Python 3.7+ is recommended).

### Installation

1.  **Clone the repository** (or copy the `day_map_downloader.py` code into a file named `day_map_downloader.py`):

    ```bash
    git clone https://github.com/lucahlg/DayZ-Map-Downloader.git
    cd DayZ-Map-Downloader
    ```

2.  **Install the required Python packages**:

    ```bash
    pip install streamlit requests Pillow
    ```

### Running the Application

1.  **Navigate to the application directory** in your terminal.

2.  **Run the Streamlit application**:

    ```bash
    streamlit run app.py
    ```

    This command will open the application in your default web browser.

-----

## Usage 🎮

1.  **Select Map**: In the sidebar, choose the DayZ map you wish to generate (e.g., "ChernarusPlus-Top", "Livonia-Sat"). The map version will automatically update.
2.  **Select Zoom Level**: Choose a zoom level. Higher zoom levels offer more detail but will result in larger file sizes and longer download times.
3.  **Generate Map**: Click the **"Generate Map"** button.
4.  **Wait for Processing**: The application will display progress as it downloads and stitches the tiles.
5.  **View and Download**: Once complete, the generated map will appear, and a **"Download Map Image"** button will become available to save the map to your computer.

-----

## Contributing 🤝

If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request\!

-----

## License 📄

This project is open-source and available under the MIT License.

-----

## Acknowledgments 🙏

  * [Streamlit](https://streamlit.io/) for making it easy to build interactive web applications.
  * [iZurvive](https://www.google.com/search?q=https://maps.izurvive.com/) for providing the map tiles.
