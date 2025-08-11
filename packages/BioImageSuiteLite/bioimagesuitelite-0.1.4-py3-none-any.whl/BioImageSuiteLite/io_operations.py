import cv2
import numpy as np
import tifffile
from typing import Tuple, List, Optional, Dict, Any
import logging
import csv

logger = logging.getLogger(__name__)

def load_avi(file_path: str) -> Tuple[Optional[List[np.ndarray]], Optional[Dict[str, Any]]]:
    """
    Loads an .avi file and extracts frames and metadata.

    Args:
        file_path (str): Path to the .avi file.

    Returns:
        Tuple[Optional[List[np.ndarray]], Optional[Dict[str, Any]]]:
            A list of frames (each as a NumPy array) and a dictionary of metadata.
            Returns (None, None) if loading fails.
    """
    try:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            logger.error(f"Error: Could not open AVI file: {file_path}")
            return None, None

        frames: List[np.ndarray] = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        fps = cap.get(cv2.CAP_PROP_FPS)
        # Default values from cap.get initially
        frame_count_meta = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        height_meta = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width_meta = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

        cap.release()

        if not frames:
            logger.warning(f"No frames extracted from {file_path}. File might be empty or corrupted after attempting to read all frames.")
            # Try to return metadata from cap.get if it was opened, but log that frames are missing
            if cap.isOpened(): # Should be false here as it's released, but good to be defensive
                 metadata_fallback = {
                    "file_path": file_path,
                    "fps": fps,
                    "frame_count": 0, # Explicitly 0 as no frames were read into the list
                    "height": height_meta,
                    "width": width_meta,
                    "original_format": "AVI",
                    "notes": "File opened but no frames could be read into the list."
                }
                 logger.info(f"Fallback metadata for {file_path}: Frames: 0 (cap.get said {frame_count_meta}), FPS: {fps}, Dimensions: {height_meta}x{width_meta}")
                 return [], metadata_fallback # Return empty list and fallback metadata
            return None, None

        # Update frame count, height, and width from the actual frames read
        actual_frame_count = len(frames)
        if actual_frame_count > 0:
            # Assuming all frames have the same dimensions as the first frame
            # For color frames (BGR), shape is (height, width, channels)
            # For grayscale, shape could be (height, width)
            first_frame_shape = frames[0].shape
            actual_height = first_frame_shape[0]
            actual_width = first_frame_shape[1]
            logger.info(f"Frame details from actual read data: Count={actual_frame_count}, H={actual_height}, W={actual_width}")
        else: # Should not happen if `if not frames:` check above is passed, but as a safeguard
            actual_height = height_meta
            actual_width = width_meta
            logger.warning(f"Frame list was populated but reports zero length. Using cap.get() dimensions: H={height_meta}, W={width_meta}")


        metadata = {
            "file_path": file_path,
            "fps": fps,
            "frame_count": actual_frame_count, # Use actual count
            "height": actual_height,           # Use actual height
            "width": actual_width,             # Use actual width
            "original_format": "AVI"
        }
        # Update log message to reflect actual read count if different from cap.get()
        if actual_frame_count != frame_count_meta:
            logger.info(f"Successfully loaded {file_path}. Actual Frames: {actual_frame_count} (cap.get reported: {frame_count_meta}), FPS: {fps}, Dimensions: {actual_height}x{actual_width}")
        else:
            logger.info(f"Successfully loaded {file_path}. Frames: {actual_frame_count}, FPS: {fps}, Dimensions: {actual_height}x{actual_width}")
        return frames, metadata
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading AVI {file_path}: {e}")
        return None, None


def load_multitiff(file_path: str, fps: float = 30.0) -> Tuple[Optional[List[np.ndarray]], Optional[Dict[str, Any]]]:
    """
    Loads a multi-page TIFF file and extracts frames and metadata.

    Args:
        file_path (str): Path to the TIFF file.
        fps (float): Frame rate to use if not found in metadata (default: 30.0).

    Returns:
        Tuple[Optional[List[np.ndarray]], Optional[Dict[str, Any]]]:
            A list of frames (each as a NumPy array) and a dictionary of metadata.
            Returns (None, None) if loading fails.
    """
    try:
        # Read the TIFF file
        with tifffile.TiffFile(file_path) as tif:
            # Extract frames
            frames = []
            for page in tif.pages:
                frames.append(page.asarray())
            
            # Try to extract FPS from ImageJ metadata
            actual_fps = fps
            if hasattr(tif, 'imagej_metadata') and tif.imagej_metadata:
                if 'finterval' in tif.imagej_metadata:
                    actual_fps = 1.0 / tif.imagej_metadata['finterval']
                elif 'fps' in tif.imagej_metadata:
                    actual_fps = tif.imagej_metadata['fps']
            
            if not frames:
                logger.error(f"No frames found in TIFF file: {file_path}")
                return None, None
            
            # Get dimensions from first frame
            first_frame = frames[0]
            height, width = first_frame.shape[:2]
            
            metadata = {
                "file_path": file_path,
                "fps": actual_fps,
                "frame_count": len(frames),
                "height": height,
                "width": width,
                "original_format": "TIFF"
            }
            
            logger.info(f"Successfully loaded {file_path}. Frames: {len(frames)}, FPS: {actual_fps}, Dimensions: {height}x{width}")
            return frames, metadata
            
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading TIFF {file_path}: {e}")
        return None, None


def load_file(file_path: str, fps: float = 30.0) -> Tuple[Optional[List[np.ndarray]], Optional[Dict[str, Any]]]:
    """
    Loads a video file (AVI or multi-page TIFF) and extracts frames and metadata.

    Args:
        file_path (str): Path to the file.
        fps (float): Frame rate to use for TIFF files if not found in metadata (default: 30.0).

    Returns:
        Tuple[Optional[List[np.ndarray]], Optional[Dict[str, Any]]]:
            A list of frames (each as a NumPy array) and a dictionary of metadata.
            Returns (None, None) if loading fails.
    """
    file_lower = file_path.lower()
    
    if file_lower.endswith('.avi'):
        return load_avi(file_path)
    elif file_lower.endswith(('.tif', '.tiff')):
        return load_multitiff(file_path, fps)
    else:
        logger.error(f"Unsupported file format: {file_path}. Only .avi and .tif/.tiff files are supported.")
        return None, None


def convert_to_greyscale_stack(frames: List[np.ndarray]) -> Optional[np.ndarray]:
    """
    Converts a list of BGR frames to a greyscale stack (T, H, W).

    Args:
        frames (List[np.ndarray]): List of BGR frames.

    Returns:
        Optional[np.ndarray]: A 3D NumPy array (T, H, W) of greyscale frames.
                               Returns None if input is invalid.
    """
    if not frames:
        logger.warning("Cannot convert to greyscale: No frames provided.")
        return None
    try:
        grey_frames: List[np.ndarray] = []
        for frame in frames:
            if frame.ndim == 3 and frame.shape[2] == 3: # Check if it's a color image
                grey_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            elif frame.ndim == 2: # Already greyscale
                grey_frames.append(frame)
            else:
                logger.warning(f"Skipping frame with unexpected shape: {frame.shape}")
                continue
        
        if not grey_frames:
            logger.error("No valid frames found for greyscale conversion.")
            return None

        return np.array(grey_frames)
    except Exception as e:
        logger.error(f"Error during greyscale conversion: {e}")
        return None


def save_to_multitiff(frames_stack: np.ndarray, output_path: str, metadata: Optional[Dict] = None) -> bool:
    """
    Saves a stack of frames (T, H, W) or (T, H, W, C) as a multi-page TIFF.

    Args:
        frames_stack (np.ndarray): NumPy array of frames.
        output_path (str): Path to save the TIFF file.
        metadata (Optional[Dict]): Metadata to embed (e.g., FPS for ImageJ compatibility).

    Returns:
        bool: True if successful, False otherwise.
    """
    if frames_stack is None or frames_stack.ndim < 3:
        logger.error("Invalid frame stack for TIFF saving. Must be at least 3D.")
        return False
    try:
        # Prepare ImageJ metadata if FPS is available
        imagej_metadata = {}
        if metadata and 'fps' in metadata and metadata['fps'] > 0:
            imagej_metadata['finterval'] = 1.0 / metadata['fps']
            imagej_metadata['fps'] = metadata['fps']
            imagej_metadata['unit'] = 'sec'
        
        # Ensure output path ends with .tif or .tiff
        if not (output_path.lower().endswith(".tif") or output_path.lower().endswith(".tiff")):
            output_path += ".tif"
            logger.info(f"Appending .tif extension. Output path: {output_path}")

        tifffile.imwrite(output_path, frames_stack, imagej=True, metadata=imagej_metadata)
        logger.info(f"Successfully saved multi-page TIFF to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving TIFF to {output_path}: {e}")
        return False

def export_results_to_csv(file_path: str, headers: List[str], table_data: List[List[str]], analysis_timestamp: str) -> bool:
    """
    Exports analysis results from a table format to a CSV file, prepending a timestamp.

    Args:
        file_path (str): The path to save the CSV file to.
        headers (List[str]): The column headers for the CSV.
        table_data (List[List[str]]): The data from the table, as a list of rows.
        analysis_timestamp (str): The timestamp of when the analysis was run.

    Returns:
        bool: True if the export was successful, False otherwise.
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # Write a metadata line for the timestamp
            csv_writer.writerow([f"Analysis Run At: {analysis_timestamp}"])
            
            # Write the main header
            csv_writer.writerow(headers)
            
            # Write the data rows
            csv_writer.writerows(table_data)
            
        logger.info(f"Successfully exported analysis results to {file_path}")
        return True
    except IOError as e:
        logger.error(f"Failed to write to CSV file {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during results CSV export: {e}")
        return False