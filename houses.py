import cv2
import numpy as np
import random

from typing import Tuple, List, Dict, Any
from colorsys import hsv_to_rgb

__all__ = ['get_drawing_house_commands', 'draw_house_from_commands']


def get_random_shade(
    hue: Tuple[int] = (0.55, 0.65),
    saturation: Tuple[int] = (0.5, 1.),
    value: Tuple[int] = (0.5, 1.)
) -> Tuple[int]:
    """
    Generates a random color shade in RGB format based on the given hue, saturation, and value ranges.
    Default ranges are considered optimal for houses unless you are a creative person.

    Args:
        hue (Tuple[int]): Tuple representing the range for the hue value (0-1).
        saturation (Tuple[int]): Tuple representing the range for the saturation value (0-1).
        value (Tuple[int]): Tuple representing the range for the value (brightness) (0-1).

    Returns:
        Tuple[int]: A tuple of three integers representing an RGB color value.
    """
    hue = random.uniform(*hue)
    saturation = random.uniform(*saturation)
    value = random.uniform(*value)

    # Convert HSV values to RGB format
    r, g, b = hsv_to_rgb(hue, saturation, value)
    r, g, b = int(r * 255), int(g * 255), int(b * 255)

    return r, g, b


def get_drawing_house_commands(
    canvas_size: int = 640,
    drawing_area: int = 480,
    floatify: bool = True
) -> List[Dict[str, Any]]:
    """
    Generates drawing commands to create a house with random parameters on a canvas.

    Args:
        canvas_size (int): The size of the entire canvas (width and height in pixels).
        drawing_area (int): The size of the area where the house will be drawn.
        floatify (bool): Whether to normalize the positions and sizes to floating-point values.

    Returns:
        List[Dict[str, Any]]: A list of commands where each command contains shape attributes
                              like position, size, and color for drawing the house.
    """
    # Generate random colors for various parts of the house
    body_color = get_random_shade(hue=(0.05, 0.16), saturation=(0.3, 0.7), value=(0.8, 1.))
    roof_color = get_random_shade(hue=(0., 0.1), saturation=(0.6, 1.), value=(0.2, 0.7))
    door_color = get_random_shade(hue=(0.04, 0.085), saturation=(0.6, 1.), value=(0.2, 0.7))
    window_color = get_random_shade(hue=(0.55, 0.65), saturation=(0.5, 1.), value=(0.5, 1.))
    chimney_color = get_random_shade(hue=(0., 0.1), saturation=(0.6, 1.), value=(0.2, 0.7))

    # Initialize a blank canvas
    canvas = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * 255

    # Set padding values to ensure the house is drawn within the drawing area
    max_pad = canvas_size - drawing_area
    pad_top = random.randint(0, max_pad)
    pad_left = random.randint(0, max_pad)

    # Randomize the body size and position
    body_w = int(random.uniform(0.3125, 0.625) * drawing_area)
    body_h = int(random.uniform(0.3125, 0.625) * drawing_area)
    body_x = random.randint(pad_left, pad_left + drawing_area - body_w)
    body_y = pad_top + drawing_area - body_h

    # Randomize the roof size
    roof_h = int(random.uniform(0.15, 0.4) * body_h)

    # Randomize the door size and position
    door_w = int(random.uniform(0.2, 0.25) * body_w)
    door_h = int(random.uniform(0.3, 0.4) * body_h)
    door_x = body_x + (body_w - door_w) // 2
    door_y = body_y + body_h - door_h

    # Randomize the chimney size and position
    chimney_w = int(random.uniform(0.05, 0.1) * body_w)
    chimney_h = int(random.uniform(1., 1.4) * roof_h)
    chimney_x = random.choice([
        random.randint(body_x, body_x + body_w // 2 - chimney_w * 2),
        random.randint(body_x + body_w // 2 + chimney_w, body_x + body_w - chimney_w)
    ])
    chimney_y = body_y - chimney_h

    # Randomize window grid layout within the available area on the house body
    area_w = int(body_w * 0.95)
    area_h = int((body_h - door_h) * 0.9)
    area_x = body_x + (body_w - area_w) // 2
    area_y = body_y + (body_h - door_h - area_h) // 2

    pad_w = int(random.uniform(0.05, 0.15) * area_w)
    pad_h = int(random.uniform(0.05, 0.15) * area_h)

    window_w = window_h = int(random.uniform(0.25, 0.5) * min(area_w, area_h))

    num_cols = int((area_w - pad_w) / (window_w + pad_w))
    num_rows = int((area_h - pad_h) / (window_h + pad_h))

    grid_w = num_cols * (window_w + pad_w) - pad_w
    grid_h = num_rows * (window_h + pad_h) - pad_h

    grid_x = (area_w - grid_w) // 2 + area_x
    grid_y = (area_h - grid_h) // 2 + area_y

    # Prepare commands for drawing various parts of the house
    commands = []
    commands_relative_keys = ['position_x', 'position_y', 'width', 'height']

    # Add body drawing command
    commands.append({
        'shape': 'rectangle',
        'class': 'body',
        'position_x': body_x,
        'position_y': body_y,
        'position_z': 0,
        'width': body_w,
        'height': body_h,
        'color': body_color
    })

    # Add door drawing command
    commands.append({
        'shape': 'rectangle',
        'class': 'door',
        'position_x': door_x,
        'position_y': door_y,
        'position_z': 1,
        'width': door_w,
        'height': door_h,
        'color': door_color
    })

    # Add chimney drawing command
    commands.append({
        'shape': 'rectangle',
        'class': 'chimney',
        'position_x': chimney_x,
        'position_y': chimney_y,
        'position_z': 0,
        'width': chimney_w,
        'height': chimney_h,
        'color': chimney_color
    })

    # Add roof drawing command (triangle)
    commands.append({
        'shape': 'triangle',
        'class': 'roof',
        'position_x': body_x,
        'position_y': body_y - roof_h,
        'position_z': 1,
        'width': body_w,
        'height': roof_h,
        'color': roof_color
    })

    # Add window grid drawing commands
    for row in range(num_rows):
        for col in range(num_cols):
            commands.append({
                'shape': 'rectangle',
                'class': 'window',
                'position_x': grid_x + col * (window_w + pad_w),
                'position_y': grid_y + row * (window_h + pad_h),
                'position_z': 1,
                'width': window_w,
                'height': window_h,
                'color': window_color
            })

    # Normalize coordinates if floatify is True
    if floatify:
        for command in commands:
            for key in commands_relative_keys:
                command[key] /= canvas_size

    return commands


def draw_house_from_commands(
    commands: List[Dict[str, Any]],
    canvas_size: int = 640,
    floatified: bool = True,
    fill: bool = True
) -> np.ndarray:
    """
    Draws a house based on the provided list of drawing commands onto a blank canvas.

    Args:
        commands (List[Dict[str, Any]]): A list of commands containing attributes for drawing shapes.
        canvas_size (int): The size of the canvas (width and height in pixels).
        floatified (bool): Whether the coordinates are normalized or in pixels.
        fill (bool): Whether the shapes should be filled or just outlined.

    Returns:
        np.ndarray: The canvas image with the house drawn on it.
    """
    # Sort commands by z-index to ensure correct layering
    commands = sorted(commands, key=lambda x: x['position_z'])

    # Initialize a blank canvas
    canvas = np.ones((canvas_size, canvas_size, 3), dtype=np.uint8) * 255

    # Draw objects on the canvas based on the commands
    for command in commands:
        x, y, w, h = command['position_x'], command['position_y'], command['width'], command['height']

        if floatified:
            x, y, w, h = int(x * canvas_size), int(y * canvas_size), int(w * canvas_size), int(h * canvas_size)

        if command.get('shape', 'triangle') == 'rectangle' or command.get('class', 'roof') != 'roof':
            # Draw a rectangle for the body, door, chimney, or window
            if fill:
                cv2.rectangle(canvas, (x, y), (x + w, y + h), command['color'], -1)
            else:
                cv2.rectangle(canvas, (x, y), (x + w, y + h), command.get('color', (0, 0, 0)), 1)
        elif command.get('shape', 'triangle') == 'triangle' or command.get('class', 'roof') == 'roof':
            # Draw a triangle for the roof
            poly = np.array([[x, y + h], [x + w // 2, y], [x + w, y + h]], dtype=np.int32)

            if fill:
                cv2.fillPoly(canvas, pts=[poly], color=command['color'])
            else:
                cv2.polylines(canvas, pts=[poly], isClosed=True, color=command.get('color', (0, 0, 0)), thickness=1)

    return canvas
