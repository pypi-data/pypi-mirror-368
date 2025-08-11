import numpy as np
from shapely.geometry import Polygon
from typing import List, Tuple, Dict, Any, Optional
import logging
import csv
from datetime import datetime

logger = logging.getLogger(__name__)

class ROI:
    """Represents a Region of Interest."""
    def __init__(self, id: int, vertices: np.ndarray, image_shape: Tuple[int, int, int], shape_index: int):
        """
        Args:
            id (int): Unique identifier for the ROI.
            vertices (np.ndarray): Array of (y, x) coordinates defining the polygon.
                                   For Napari Shapes layer, data is typically (N, D)
                                   where D=2 for 2D shapes, and coordinates are (row, column).
            image_shape (Tuple[int, int, int]): Shape of the image stack (T, H, W).
            shape_index (int): The index of the shape in the napari Shapes layer.
        """
        self.id = id
        self.creation_time = datetime.now()
        self.vertices = np.array(vertices) # Ensure it's a NumPy array
        self.shape_index = shape_index
        self.image_height = image_shape[1]
        self.image_width = image_shape[2]
        self.mask: Optional[np.ndarray] = None # (H, W) mask
        self._area_pixels: Optional[float] = None
        self._area_sq_um: Optional[float] = None
        self.properties: Dict[str, Any] = {'name': f'ROI_{id}'} # For Napari properties

        if self.vertices.ndim != 2 or self.vertices.shape[1] != 2:
            raise ValueError(f"Vertices must be a N_points x 2 array. Got shape {self.vertices.shape}")
        self._create_mask()
        self._calculate_area_pixels()

    def _create_mask(self):
        """Creates a binary mask from the ROI vertices."""
        from skimage.draw import polygon
        # Napari vertices are (row, col) which corresponds to (y, x)
        # Ensure vertices are within image bounds, skimage.draw.polygon needs this
        # Also, polygon requires rr, cc format.
        rows = np.clip(self.vertices[:, 0], 0, self.image_height - 1)
        cols = np.clip(self.vertices[:, 1], 0, self.image_width - 1)
        
        rr, cc = polygon(rows, cols, shape=(self.image_height, self.image_width))
        self.mask = np.zeros((self.image_height, self.image_width), dtype=bool)
        self.mask[rr, cc] = True

    def _calculate_area_pixels(self):
        """Calculates the area of the ROI in pixels using Shapely or mask sum."""
        if self.vertices.shape[0] < 3: # Not a polygon
            self._area_pixels = 0.0
            logger.warning(f"ROI {self.id} has less than 3 vertices. Area set to 0.")
            return

        try:
            # Shapely expects (x, y) order, Napari provides (row, col) which is (y,x)
            # So we might need to flip if using Shapely directly on raw vertices
            # However, using the mask is more straightforward here.
            if self.mask is not None:
                 self._area_pixels = np.sum(self.mask)
            else: # Fallback if mask creation failed
                poly = Polygon(self.vertices[:, ::-1]) # Flip to (x,y) for shapely
                self._area_pixels = poly.area
        except Exception as e:
            logger.error(f"Error calculating area for ROI {self.id} with Shapely: {e}. Falling back to mask sum.")
            if self.mask is not None:
                 self._area_pixels = np.sum(self.mask)
            else:
                self._area_pixels = 0.0
                logger.error(f"Could not calculate area for ROI {self.id} as mask is also None.")


    @property
    def area_pixels(self) -> float:
        return self._area_pixels if self._area_pixels is not None else 0.0

    def set_area_physical(self, pixel_size_um: float):
        """
        Calculates and sets the ROI area in square micrometers.

        Args:
            pixel_size_um (float): The size of one pixel in micrometers (assuming square pixels).
        """
        if self._area_pixels is not None and pixel_size_um > 0:
            self._area_sq_um = self._area_pixels * (pixel_size_um ** 2)
        else:
            self._area_sq_um = 0.0
            if pixel_size_um <=0:
                logger.warning(f"Pixel size ({pixel_size_um} um) must be positive to calculate physical area.")


    @property
    def area_sq_um(self) -> Optional[float]:
        return self._area_sq_um

    def get_mean_intensity_trace(self, image_stack: np.ndarray) -> Optional[np.ndarray]:
        """
        Calculates the mean intensity within the ROI for each frame in the stack.

        Args:
            image_stack (np.ndarray): The image stack (T, H, W), expected to be greyscale.

        Returns:
            Optional[np.ndarray]: A 1D array of mean intensities over time. None if ROI or stack is invalid.
        """
        if self.mask is None or image_stack is None:
            logger.warning(f"Cannot get intensity trace for ROI {self.id}: Mask or image_stack is None.")
            return None
        if image_stack.ndim != 3:
            logger.error(f"Image stack must be 3D (T, H, W). Got {image_stack.ndim}D.")
            return None
        if image_stack.shape[1:] != self.mask.shape:
            logger.error(f"Image stack dimensions {image_stack.shape[1:]} mismatch ROI mask {self.mask.shape}.")
            return None

        try:
            num_frames = image_stack.shape[0]
            mean_intensities = np.zeros(num_frames)
            masked_area_sum = np.sum(self.mask)
            if masked_area_sum == 0:
                logger.warning(f"ROI {self.id} has zero area in mask. Intensity trace will be all zeros.")
                return mean_intensities

            for t in range(num_frames):
                mean_intensities[t] = np.sum(image_stack[t][self.mask]) / masked_area_sum
            return mean_intensities
        except Exception as e:
            logger.error(f"Error calculating mean intensity trace for ROI {self.id}: {e}")
            return None

# Example of how you might manage multiple ROIs
class ROIManager:
    def __init__(self, image_shape_thw: Tuple[int,int,int]):
        self.rois: Dict[int, ROI] = {}
        self.next_roi_id = 1
        self.image_shape_thw = image_shape_thw # T, H, W

    def export_rois_to_csv(self, file_path: str) -> bool:
        """
        Exports the vertex data for all ROIs to a CSV file.

        Args:
            file_path (str): The path to save the CSV file.

        Returns:
            bool: True if export was successful, False otherwise.
        """
        if not self.rois:
            logger.warning("No ROIs to export.")
            return False

        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write header
                header = ['roi_id', 'creation_timestamp', 'vertex_index', 'axis-0 (y)', 'axis-1 (x)']
                csv_writer.writerow(header)

                # Write data
                for roi_id, roi in sorted(self.rois.items()):
                    timestamp_str = roi.creation_time.strftime("%Y-%m-%d %H:%M:%S")
                    for vertex_idx, vertex in enumerate(roi.vertices):
                        row = [
                            roi.id,
                            timestamp_str,
                            vertex_idx,
                            vertex[0],  # axis-0 (y, row)
                            vertex[1]   # axis-1 (x, column)
                        ]
                        csv_writer.writerow(row)
            
            logger.info(f"Successfully exported {len(self.rois)} ROIs to {file_path}")
            return True
        except IOError as e:
            logger.error(f"Failed to write to CSV file {file_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during CSV export: {e}")
            return False

    def add_roi(self, vertices: np.ndarray, shape_index: int) -> Optional[ROI]:
        try:
            roi = ROI(self.next_roi_id, vertices, self.image_shape_thw, shape_index)
            self.rois[self.next_roi_id] = roi
            self.next_roi_id += 1
            logger.info(f"Added ROI {roi.id} (Shape index: {shape_index}) with {len(vertices)} vertices.")
            return roi
        except ValueError as ve:
            logger.error(f"Failed to add ROI: {ve}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error adding ROI: {e}")
            return None

    def get_roi_by_shape_index(self, shape_index: int) -> Optional[ROI]:
        """Finds an ROI by its corresponding napari shape index."""
        for roi in self.rois.values():
            if roi.shape_index == shape_index:
                return roi
        return None

    def get_roi(self, roi_id: int) -> Optional[ROI]:
        return self.rois.get(roi_id)

    def remove_roi(self, roi_id: int):
        if roi_id in self.rois:
            del self.rois[roi_id]
            logger.info(f"Removed ROI {roi_id}.")
        else:
            logger.warning(f"ROI {roi_id} not found for removal.")

    def get_all_rois(self) -> List[ROI]:
        return list(self.rois.values())

    def update_image_shape(self, new_image_shape_thw: Tuple[int,int,int]):
        self.image_shape_thw = new_image_shape_thw
        # Potentially invalidate or update existing ROIs if dimensions change drastically
        # For simplicity, we'll just update the shape for new ROIs.
        # Existing ROIs would need recalculation of masks if H/W changes.
        logger.info(f"ROIManager image shape updated to {new_image_shape_thw}")