# throttle_utils.py

from typing import Tuple
import time

def should_throttle(tracker: dict, allowed_rate: float, now: float = None) -> Tuple[bool, float, float]:
    """
    Determines whether a message should be logged based on throttling interval.

    Parameters:
        tracker (dict): Dictionary storing 'last_time', 'last_print_time', and 'freq' per topic.
        allowed_rate (float): Maximum rate at which logging is allowed (Hz).
        now (float): Current time in seconds. If None, uses time.time().

    Returns:
        should_log (bool): Whether to print/log this message.
        print_freq (float): Effective print frequency (Hz).
        msg_freq (float): Message arrival frequency (Hz).
    """
    if now is None:
        now = time.time()

    # --- Message frequency ---
    last_time = tracker.get("last_time")
    if last_time is not None:
        dt = now - last_time
        msg_freq = 1.0 / dt if dt > 0 else 0.0
    else:
        msg_freq = 0.0
    tracker["last_time"] = now
    tracker["freq"] = msg_freq

    # --- Throttling ---
    min_interval = 1.0 / allowed_rate if allowed_rate > 0 else float("inf")
    last_print_time = tracker.get("last_print_time")

    if last_print_time is None or (now - last_print_time) >= min_interval:
        print_dt = now - last_print_time if last_print_time is not None else 0
        print_freq = 1.0 / print_dt if print_dt > 0 else 0.0
        tracker["last_print_time"] = now
        return True, print_freq, msg_freq

    return False, 0.0, msg_freq
