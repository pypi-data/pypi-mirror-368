from collections import Counter
import cv2
import numpy as np

COLOR_NAMES = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "gray": (128, 128, 128),
}

def classify_dominant_color(image_path: str) -> str:
    """
    Detects the dominant color in an image.
    Args:
        image_path (str): Path to the image file.
    Returns:
        str: Name of the dominant color.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or cannot be read.")

    image = cv2.resize(image, (50, 50))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image_rgb.reshape(-1, 3)

    most_common_color = Counter(map(tuple, pixels)).most_common(1)[0][0]

    closest_color = min(
        COLOR_NAMES.items(),
        key=lambda name_rgb: np.linalg.norm(np.array(name_rgb[1]) - np.array(most_common_color))
    )[0]

    return closest_color
