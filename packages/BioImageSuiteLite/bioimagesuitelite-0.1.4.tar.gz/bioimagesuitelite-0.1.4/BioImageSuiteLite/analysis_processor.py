# BioImageSuiteLite/analysis_processor.py
import numpy as np
from scipy.signal import find_peaks, peak_widths
from scipy.ndimage import gaussian_filter1d
from skimage.filters import threshold_otsu
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class Event:
    """Represents a detected event."""
    def __init__(self, start_time: float, end_time: float, start_frame: int, end_frame: int,
                 event_type: str, roi_id: int, properties: Optional[Dict[str, Any]] = None):
        self.start_time = start_time
        self.end_time = end_time
        self.duration = end_time - start_time
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.event_type = event_type # e.g., "threshold", "dog", "scisson"
        self.roi_id = roi_id
        self.properties = properties if properties else {} # e.g., peak_value, prominence

    def __repr__(self):
        return (f"Event(ROI_ID:{self.roi_id}, Type:{self.event_type}, "
                f"Frames:[{self.start_frame}-{self.end_frame}], "
                f"Time:[{self.start_time:.2f}-{self.end_time:.2f}s], "
                f"Duration:{self.duration:.2f}s)")


def detect_events_threshold(
    intensity_trace: np.ndarray,
    fps: float,
    roi_id: int,
    threshold_value: Optional[float] = None,
    use_otsu: bool = False,
    min_duration_frames: int = 1
) -> List[Event]:
    """
    Detects events based on intensity crossing a threshold.

    Args:
        intensity_trace (np.ndarray): 1D array of intensity values over time.
        fps (float): Frames per second.
        roi_id (int): ID of the ROI being analyzed.
        threshold_value (Optional[float]): Absolute threshold. If None and use_otsu is False, raises error.
        use_otsu (bool): If True, calculates threshold using Otsu's method. Ignores threshold_value.
        min_duration_frames (int): Minimum number of consecutive frames an event must last.

    Returns:
        List[Event]: List of detected events.
    """
    if intensity_trace is None or len(intensity_trace) == 0:
        return []
    
    actual_threshold = 0.0
    if use_otsu:
        try:
            actual_threshold = threshold_otsu(intensity_trace)
            logger.info(f"ROI {roi_id}: Otsu threshold calculated: {actual_threshold:.2f}")
        except ValueError: # Happens if all values are the same
             logger.warning(f"ROI {roi_id}: Otsu threshold failed (likely constant intensity). No events detected by Otsu.")
             return []
    elif threshold_value is not None:
        actual_threshold = threshold_value
    else:
        logger.error("Threshold detection requires either a 'threshold_value' or 'use_otsu=True'.")
        raise ValueError("Invalid threshold parameters")

    above_threshold = intensity_trace > actual_threshold
    events: List[Event] = []
    in_event = False
    event_start_frame = 0

    for i in range(len(above_threshold)):
        if above_threshold[i] and not in_event:
            in_event = True
            event_start_frame = i
        elif not above_threshold[i] and in_event:
            in_event = False
            event_end_frame = i - 1 # Event ended on the previous frame
            if (event_end_frame - event_start_frame + 1) >= min_duration_frames:
                event_start_time = event_start_frame / fps
                event_end_time = (event_end_frame + 1) / fps # End time is at the end of the last frame
                evt = Event(start_time=event_start_time, end_time=event_end_time,
                            start_frame=event_start_frame, end_frame=event_end_frame,
                            event_type="threshold", roi_id=roi_id,
                            properties={'threshold_value': actual_threshold})
                events.append(evt)
                
    # Check if event was ongoing at the end of the trace
    if in_event:
        event_end_frame = len(above_threshold) - 1
        if (event_end_frame - event_start_frame + 1) >= min_duration_frames:
            event_start_time = event_start_frame / fps
            event_end_time = (event_end_frame + 1) / fps
            evt = Event(start_time=event_start_time, end_time=event_end_time,
                        start_frame=event_start_frame, end_frame=event_end_frame,
                        event_type="threshold", roi_id=roi_id,
                        properties={'threshold_value': actual_threshold})
            events.append(evt)
    logger.info(f"ROI {roi_id}: Threshold detection found {len(events)} events.")
    return events


def detect_events_dog(
    intensity_trace: np.ndarray,
    fps: float,
    roi_id: int,
    sigma1: float,
    sigma2: float,
    peak_threshold_factor: float = 0.5, # Factor of std dev of DoG signal
    min_prominence: Optional[float] = None
) -> List[Event]:
    """
    Detects events using Difference of Gaussians (DoG) on the 1D intensity trace.
    Events are considered as peaks in the DoG signal.

    Args:
        intensity_trace (np.ndarray): 1D array of intensity values.
        fps (float): Frames per second.
        roi_id (int): ID of the ROI.
        sigma1 (float): Smaller sigma for Gaussian blur.
        sigma2 (float): Larger sigma for Gaussian blur.
        peak_threshold_factor (float): Threshold for peak detection as a factor of DoG signal's std dev.
                                      Only used if min_prominence is None.
        min_prominence (Optional[float]): Minimum prominence for find_peaks.

    Returns:
        List[Event]: List of detected events (peaks).
    """
    if intensity_trace is None or len(intensity_trace) < max(sigma1, sigma2) * 3 : # Need enough data points
        logger.warning(f"ROI {roi_id}: Intensity trace too short for DoG with sigmas {sigma1}, {sigma2}.")
        return []
    if sigma1 >= sigma2:
        logger.error("Sigma1 must be smaller than Sigma2 for DoG.")
        raise ValueError("Sigma1 must be smaller than Sigma2.")

    gauss1 = gaussian_filter1d(intensity_trace.astype(float), sigma=sigma1)
    gauss2 = gaussian_filter1d(intensity_trace.astype(float), sigma=sigma2)
    dog_signal = gauss1 - gauss2

    if min_prominence is None:
        # Use std dev based threshold if prominence is not set
        # This is a heuristic and might need tuning
        dynamic_threshold = peak_threshold_factor * np.std(dog_signal)
        if dynamic_threshold == 0 : # Handle constant DoG signal
            logger.warning(f"ROI {roi_id}: DoG signal is constant. No peaks will be detected with dynamic threshold.")
            return []
        peaks, properties = find_peaks(dog_signal, height=dynamic_threshold)
    else:
        peaks, properties = find_peaks(dog_signal, prominence=min_prominence)

    events: List[Event] = []
    for i, peak_idx in enumerate(peaks):
        # For DoG, an "event" is often a transient peak. We define its duration heuristically.
        # Could use peak_widths from find_peaks if more precise duration is needed.
        # For now, let's assume a short fixed duration around the peak.
        # A more robust way would be to define start/end based on when DoG signal
        # crosses a certain baseline, or use properties['widths'].
        # Here, we simplify and consider it a 1-frame event at the peak.
        # Or use properties['left_ips'], properties['right_ips'] if available and meaningful
        
        event_frame = int(peak_idx)
        # A more sophisticated approach would be to define start/end based on the peak width.
        # For now, let's treat each peak as a single-frame event or use find_peaks 'width' if sensible.
        # Let's define a minimal event duration of 1 frame centered at the peak.
        # More advanced: Use properties['widths'] from find_peaks(..., width=...)
        start_frame = event_frame
        end_frame = event_frame

        event_start_time = start_frame / fps
        event_end_time = (end_frame + 1) / fps # Duration of 1/fps

        event_props = {
            'dog_peak_value': dog_signal[peak_idx],
            'dog_prominence': properties.get('prominences', [None])[i]
        }

        evt = Event(start_time=event_start_time, end_time=event_end_time,
                    start_frame=start_frame, end_frame=end_frame,
                    event_type="dog", roi_id=roi_id, properties=event_props)
        events.append(evt)
    logger.info(f"ROI {roi_id}: DoG detection found {len(events)} events (peaks).")
    return events


def estimate_dog_params_from_trace(
    intensity_trace: np.ndarray,
) -> Optional[Tuple[float, float, float]]:
    """
    Estimates optimal DoG parameters from an intensity trace by finding the most prominent peak.

    Args:
        intensity_trace (np.ndarray): 1D array of intensity values over time.

    Returns:
        Optional[Tuple[float, float, float]]: A tuple containing (sigma1, sigma2, min_prominence).
                                              Returns None if no peaks are found.
    """
    if intensity_trace is None or len(intensity_trace) < 10: # Need some data
        logger.warning("Intensity trace is too short for parameter estimation.")
        return None

    # Find all peaks and their prominences
    try:
        # We find peaks in the raw trace to estimate parameters for the DoG filter
        # Use a minimal prominence to avoid noise, e.g., >1% of the signal range
        min_prom = (np.max(intensity_trace) - np.min(intensity_trace)) * 0.01
        peaks, properties = find_peaks(intensity_trace, prominence=(min_prom, None))

        if len(peaks) == 0:
            logger.warning("No significant peaks found in the trace, cannot estimate DoG parameters.")
            return None

        # Find the most prominent peak
        prominences = properties['prominences']
        most_prominent_idx = np.argmax(prominences)
        best_peak_idx = peaks[most_prominent_idx]
        max_prominence = prominences[most_prominent_idx]

        # Calculate the width of the most prominent peak to estimate sigma
        # The width is calculated at half the prominence of the peak
        widths, _, _, _ = peak_widths(intensity_trace, [best_peak_idx], rel_height=0.5)
        
        if len(widths) == 0 or widths[0] == 0:
            logger.warning("Could not determine peak width. Using default sigma.")
            # Fallback if width is zero, maybe a single-point spike
            est_sigma1 = 1.0 
        else:
            # Heuristic: sigma is related to the full-width at half-maximum (FWHM)
            # For a Gaussian, FWHM = 2 * sqrt(2*ln(2)) * sigma ~= 2.355 * sigma
            # So, sigma ~= FWHM / 2.355
            est_sigma1 = max(0.5, widths[0] / 2.355) # Ensure sigma is not too small

        # Set sigma2 based on the recommended ratio
        est_sigma2 = est_sigma1 * 1.6

        # Set min_prominence based on the most prominent peak found
        # A good starting point is a fraction of this max prominence.
        # This is for the DoG signal, not the raw trace, but it's a good heuristic.
        # The DoG signal's prominence will be related to the raw signal's prominence.
        # Let's use 1/4th of the raw prominence as a starting point for DoG prominence
        est_min_prominence = max_prominence / 4.0
        
        logger.info(f"Estimated DoG params: sigma1={est_sigma1:.2f}, sigma2={est_sigma2:.2f}, prominence={est_min_prominence:.2f}")

        return (est_sigma1, est_sigma2, est_min_prominence)

    except Exception as e:
        logger.error(f"Error during DoG parameter estimation: {e}")
        return None


def detect_events_scisson_like_stub(
    intensity_trace: np.ndarray,
    fps: float,
    roi_id: int,
    # Add parameters for your chosen ruptures algorithm or BNP-Step
    model_type: str = "l2", # Example for ruptures.Pelt
    penalty_value: Optional[float] = None # Example for ruptures.Pelt
) -> List[Event]:
    """
    Placeholder for "Scisson-like" step detection.
    This needs to be implemented using a library like `ruptures` or `bnp-step`.
    """
    logger.info(f"ROI {roi_id}: Scisson-like analysis (stub) called.")
    if intensity_trace is None or len(intensity_trace) == 0:
        return []
    
    events: List[Event] = []

    # --- Integration with `ruptures` (Example with Pelt) ---
    # try:
    #     import ruptures as rpt
    #     if penalty_value is None:
    #         # Estimate penalty, this is crucial and problem-dependent
    #         # A common heuristic is related to log(n_samples) * sigma^2
    #         # For now, let's use a placeholder or require it.
    #         # A proper way to choose penalty is often via model selection criteria (BIC, AIC) or validation.
    #         n_samples = len(intensity_trace)
    #         sigma_est = np.std(np.diff(intensity_trace)) # Estimate noise std from differences
    #         if sigma_est == 0 and n_samples > 1: # Constant signal
    #             logger.warning(f"ROI {roi_id} Scisson: Intensity trace is constant or near-constant. Using default low penalty.")
    #             penalty_value = 1.0 
    #         elif sigma_est == 0 and n_samples <=1:
    #             logger.warning(f"ROI {roi_id} Scisson: Intensity trace too short to estimate noise. Not detecting steps.")
    #             return []
    #         else:
    #             # This is a very rough heuristic, proper penalty selection is key!
    #             penalty_value = 3 * np.log(n_samples) * (sigma_est**2)
    #         logger.info(f"ROI {roi_id} Scisson: Auto-estimated penalty for Pelt: {penalty_value:.2f}")


    #     algo = rpt.Pelt(model=model_type).fit(intensity_trace)
    #     # The penalty value here is critical and needs careful tuning or estimation
    #     change_points_indices = algo.predict(pen=penalty_value) # Returns indices *before* the end of segments

    #     # change_points_indices includes the last point (len(intensity_trace))
    #     # Each segment is [start, end-1]. A change point means a step *after* that index.
    #     # So, a change at index `bkp` means the step occurred between `bkp-1` and `bkp`.
    #     # Let's define an event as the segment itself if its mean differs significantly
    #     # or just the transition points. The original Scisson paper implies step fitting.

    #     # For simplicity here, let's consider each change point as an event (the step itself)
    #     # A more advanced interpretation would analyze the segments between change points.
    #     for chg_pt_idx in change_points_indices:
    #         if chg_pt_idx == len(intensity_trace): # Last point is not a start of a new step
    #             continue
            
    #         # This is a simplified interpretation: step occurs at chg_pt_idx
    #         # A proper step event would have a start and potentially a new level.
    #         # For now, treat as instantaneous.
    #         event_frame = int(chg_pt_idx)
    #         event_time = event_frame / fps
            
    #         evt = Event(start_time=event_time, end_time=event_time + (1/fps), # Minimal duration
    #                     start_frame=event_frame, end_frame=event_frame,
    #                     event_type=f"scisson_{model_type}", roi_id=roi_id,
    #                     properties={'change_point_index': event_frame})
    #         events.append(evt)
            
    # except ImportError:
    #     logger.warning("`ruptures` library not installed. Scisson-like analysis (Pelt) skipped.")
    #     return []
    # except Exception as e:
    #     logger.error(f"ROI {roi_id}: Error during Scisson-like (Pelt) analysis: {e}")
    #     return []
    
    # --- End of ruptures example ---

    if not events:
         logger.info(f"ROI {roi_id}: Scisson-like analysis found 0 events (or not implemented fully).")
    else:
        logger.info(f"ROI {roi_id}: Scisson-like analysis found {len(events)} change points.")
    return events # Return empty list until implemented


def filter_duplicate_events(events: List[Event], min_separation_seconds: float) -> List[Event]:
    """
    Filters duplicate or closely occurring events.
    Keeps the first event if multiple occur within `min_separation_seconds`.
    This is a simple temporal proximity filter. More sophisticated NMS could be used.

    Args:
        events (List[Event]): List of detected events, assumed to be sorted by start_time.
        min_separation_seconds (float): Minimum time gap between the end of one event
                                        and the start of the next to be considered distinct.

    Returns:
        List[Event]: List of filtered events.
    """
    if not events:
        return []

    # Sort events by start time, then by end time, then by type (for consistent tie-breaking)
    sorted_events = sorted(events, key=lambda e: (e.start_time, e.end_time, e.event_type))
    
    filtered_events: List[Event] = [sorted_events[0]]

    for current_event in sorted_events[1:]:
        last_kept_event = filtered_events[-1]
        # Check if current event starts after the last kept event ends, plus separation
        if current_event.start_time >= (last_kept_event.end_time + min_separation_seconds):
            filtered_events.append(current_event)
        else:
            # Potential overlap or too close. Decide on merging or keeping one.
            # For now, if they are too close, we discard the current_event.
            # A more advanced strategy might merge or pick based on event strength.
            logger.debug(f"Filtering duplicate/close event: {current_event} due to proximity to {last_kept_event}")
            pass 

    logger.info(f"Filtered duplicates: {len(events)} -> {len(filtered_events)} events (min_sep: {min_separation_seconds}s).")
    return filtered_events


def normalize_event_rate(
    total_events: int,
    observation_duration_seconds: float,
    roi_area_sq_um: float
) -> float:
    """
    Normalizes the event count to events/second/sq.µm.

    Args:
        total_events (int): Total number of unique events.
        observation_duration_seconds (float): Total observation time in seconds.
        roi_area_sq_um (float): ROI area in square micrometers.

    Returns:
        float: Normalized event rate. Returns 0 if duration or area is zero.
    """
    if observation_duration_seconds <= 0 or roi_area_sq_um <= 0:
        logger.warning(f"Cannot normalize: duration ({observation_duration_seconds}s) "
                       f"or area ({roi_area_sq_um}µm²) is non-positive.")
        return 0.0
    return total_events / (observation_duration_seconds * roi_area_sq_um)