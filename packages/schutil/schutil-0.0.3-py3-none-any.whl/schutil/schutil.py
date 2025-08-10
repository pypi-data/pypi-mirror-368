import asyncio, re
from typing import Optional

class Colors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    INVERT = '\033[7m'
    HIDDEN = '\033[8m'

    ENDC = '\033[0m'

async def animate(stop_event: asyncio.Event, prefix: str = "", interval: float = 0.3, animation_type: str = "ellipsis") -> None:
    """
    Async console animation.

    Args:
        stop_event (asyncio.Event): Event to stop the animation.
        prefix (str): String to print before the animation.
        interval (float): Time in seconds between animation frames.
        animation_type (str): Type of animation. One of:
            - "ellipsis" : cycles through '.', '..', '...'
            - "spinner"  : cycles through '|', '/', '-', '\\'
            - "dots"     : cycles through '.', 'o', 'O', 'o'
        
    Raises:
        AssertionError: If argument types are incorrect.

    Usage example:
    --------------
    ```python
        stop_event = asyncio.Event()
        animation_task = asyncio.create_task(
            animate(stop_event, prefix="Loading ", animation_type="spinner")
        )

        # Simulate some async work
        await asyncio.sleep(5)

        stop_event.set()
        await animation_task
        print("Done!")
    ```
    """

    assert isinstance(stop_event, asyncio.Event), "stop_event must be an asyncio.Event"
    assert isinstance(prefix, str), "prefix must be a string"
    assert isinstance(interval, (int, float)) and interval > 0, "interval must be a positive number"
    valid_animations = {"ellipsis", "spinner", "dots"}
    assert animation_type in valid_animations, f"animation_type must be one of {valid_animations}"

    animations = {
        "ellipsis": [".", "..", "..."],
        "spinner": ["|", "/", "-", "\\"],
        "dots": [".", "o", "O", "o"],
    }

    frames = animations[animation_type]
    i = 0

    while not stop_event.is_set():
        frame = frames[i]
        print(f"\r{prefix}{frame}{' ' * (max(len(f) for f in frames) - len(frame))}", end="", flush=True)
        i = (i + 1) % len(frames)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue

    print("\r" + " " * (len(prefix) + max(len(f) for f in frames)) + "\r", end="", flush=True)

def gradient_text(text: str, start_color: str, end_color: str, repeat: Optional[int] = None, reset: bool = True) -> str:
    """
    Generates a string with ANSI escape codes to display the input text
    in a smooth color gradient from start_color to end_color in the terminal.
    \nTerminal must support 24-bit RGB colors. For Windows, something like VirtualTerminalLevel = 1 in Registry.

    Args:
        text (str): The text to be colored with the gradient.
        start_color (str): Hex color code (6 characters, e.g. "AD99AD").
        end_color (str): Hex color code (6 characters, e.g. "6A0D91").
        repeat (int, optional): Number of characters to repeat the gradient over.
                                If None or > len(text), the gradient stretches over the entire text.
                                If provided and <= len(text), the gradient repeats every `repeat` characters.
        reset (bool): Whether to append the ANSI reset code at the end. Default True.

    Returns:
        str: The input text with embedded ANSI escape codes for an RGB gradient coloring.

    Raises:
        AssertionError: If argument types are incorrect.

    Usage example:
    --------------
    ```python
        print(gradient_text("Hello, World!", "FF0000", "0000FF", repeat=5))
    ```
    """
    assert start_color is not None, "start_color must be provided"
    assert end_color is not None, "end_color must be provided"
    assert len(start_color) == 6 and all(c in "0123456789abcdefABCDEF" for c in start_color), "start_color must be a 6-digit hex string"
    assert len(end_color) == 6 and all(c in "0123456789abcdefABCDEF" for c in end_color), "end_color must be a 6-digit hex string"
    assert repeat is None or (isinstance(repeat, int) and repeat > 0), "repeat must be a positive int or None"

    start_color_rgb = tuple(int(start_color[i:i+2], 16) for i in (0, 2, 4))
    end_color_rgb = tuple(int(end_color[i:i+2], 16) for i in (0, 2, 4))

    def interp_color(pos, length):
        r = int(start_color_rgb[0] + (end_color_rgb[0] - start_color_rgb[0]) * (pos / max(length - 1, 1)))
        g = int(start_color_rgb[1] + (end_color_rgb[1] - start_color_rgb[1]) * (pos / max(length - 1, 1)))
        b = int(start_color_rgb[2] + (end_color_rgb[2] - start_color_rgb[2]) * (pos / max(length - 1, 1)))
        return r, g, b

    length = len(text)
    gradient_text_str = ""

    if repeat is None or repeat > length:
        for i, char in enumerate(text):
            r, g, b = interp_color(i, length)
            gradient_text_str += f"\033[38;2;{r};{g};{b}m{char}"
    else:
        for i, char in enumerate(text):
            pos_in_repeat = i % repeat
            r, g, b = interp_color(pos_in_repeat, repeat)
            gradient_text_str += f"\033[38;2;{r};{g};{b}m{char}"

    if reset:
        gradient_text_str += "\033[0m"

    return gradient_text_str

def is_valid_ipv4(ip: str, special: bool = False) -> bool:
    """
    Validate an IPv4 address.

    Args:
        ip (str): IPv4 address string.
        special (bool): If True, allows '0.0.0.0' and '255.255.255.255'.
                        If False, only allows IPs between '1.1.1.1' and '254.254.254.254'.

    Returns:
        bool: True if valid, False otherwise.
        
    Raises:
        AssertionError: If argument types are incorrect.

    Usage examples:
    ---------------
    >>> is_valid_ipv4("0.0.0.0", special=True)
    True
    >>> is_valid_ipv4("0.0.0.0", special=False)
    False
    """
    assert isinstance(ip, str), "ip must be a string"
    assert isinstance(special, bool), "special must be a boolean"
    octets: list[str] = ip.split(".")
    assert len(octets) == 4, "IP must have exactly 4 octets"

    octet_full = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    octet_restricted = r"(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]\d?)"
    pattern = (
        rf"^{octet_full}\.{octet_full}\.{octet_full}\.{octet_full}$"
        if special else
        rf"^{octet_restricted}\.{octet_restricted}\.{octet_restricted}\.{octet_restricted}$"
    )
    return bool(re.match(pattern, ip))

def validate_input(prompt: str, validator: callable, error_message: str, retries: int | None = None, error_red: bool = True) -> str:
    """
    Prompt user for input repeatedly until the validator function returns True.

    Args:
        prompt (str): The input prompt to display to the user.
        validator (callable): A function that takes the user input string and returns True if valid.
        error_message (str): Message to display on invalid input.
        retries (int | None): Number of allowed retries before raising ValueError. None means infinite retries.
        error_red (bool): If True, prints error message in red color.

    Returns:
        str: The validated user input.

    Raises:
        AssertionError: If argument types are incorrect.
        ValueError: If retries exceeded.

    Usage example:
    --------------
    ```python
    def is_yes_no(s):
        return s in ("yes", "no")

    answer = validate_input("Continue? (yes/no): ", is_yes_no, "Please type 'yes' or 'no'.", retries=3)
    print(f"You answered: {answer}")
    ```
    """
    assert isinstance(prompt, str), "prompt must be a string"
    assert callable(validator), "validator must be callable"
    assert isinstance(error_message, str), "error_message must be a string"
    assert retries is None or (isinstance(retries, int) and retries > 0), "retries must be a positive int or None"
    assert isinstance(error_red, bool), "error_red must be a boolean"

    attempts = 0
    while True:
        user_input = input(prompt).strip()

        if validator(user_input):
            return user_input
        else:
            if error_red:
                print(f"\033[91m{error_message}\033[0m")
            else:
                print(error_message)

        attempts += 1
        if retries is not None and attempts >= retries:
            raise ValueError(f"Maximum retries ({retries}) exceeded")
        
def strip_protocol(url: str, remove_www: bool = True, remove_trailing_slash: bool = True) -> str:
    """
    Remove the protocol (http:// or https://), 'www.', and trailing slash from a URL.

    Args:
        url (str): The URL string to process.
        remove_www (bool, optional): Whether to remove 'www.' prefix. Default is True.
        remove_trailing_slash (bool, optional): Whether to remove trailing slash. Default is True.

    Returns:
        str: The URL without protocol, optionally without 'www.' and trailing slash.

    Usage example:
    --------------
    >>> strip_protocol("https://www.example.com/")
    "example.com"

    >>> strip_protocol("https://www.example.com/", remove_www=False, remove_trailing_slash=False)
    "www.example.com/"
    """
    pattern = r'^(https?://)?'
    if remove_www:
        pattern += r'(www\.)?'

    result = re.sub(pattern, '', url)
    if remove_trailing_slash:
        result = result.rstrip('/')

    return result
    
def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    """
    Convert a hex color code to an RGB tuple.

    Args:
        hex_code (str): Hex color string, e.g. "#FFAABB", "FFAABB", or "0xFFAABB".

    Returns:
        tuple[int, int, int]: RGB values as integers (0-255).

    Usage example:
    --------------
    ```python
    rgb = hex_to_rgb("#FFAABB")
    print(rgb) # (255, 170, 187)
    ```
    """
    assert isinstance(hex_code, str), "hex_code must be a string"
    hex_code = hex_code.lstrip("#").lstrip("0x")
    assert len(hex_code) in (6, 8), "hex_code must have length 6 or 8 (excluding prefix)"
    hex_code = hex_code.zfill(6)
    red = int(hex_code[0:2], 16)
    green = int(hex_code[2:4], 16)
    blue = int(hex_code[4:6], 16)
    return red, green, blue

def hex_to_rgba(hex_code: str) -> tuple[int, int, int, int]:
    """
    Convert a hex color code to an RGBA tuple.

    Args:
        hex_code (str): Hex color string, 6 or 8 characters, e.g. "#FFAABBCC", "FFAABB", or "0xFFAABBCC".

    Returns:
        tuple[int, int, int, int]: RGBA values as integers (0-255). Alpha defaults to 255 if missing.

    Usage example:
    --------------
    ```python
    rgba = hex_to_rgba("FFAABBCC")
    print(rgba)  # (255, 170, 187, 204)
    ```
    """
    assert isinstance(hex_code, str), "hex_code must be a string"
    hex_code = hex_code.lstrip("#").lstrip("0x")
    if len(hex_code) == 8:
        alpha = int(hex_code[6:8], 16)
        hex_code = hex_code[:6]
    elif len(hex_code) == 6:
        alpha = 255
    else:
        raise ValueError("Invalid hex color format. Length should be 6 or 8 characters.")
    hex_code = hex_code.zfill(6)
    red = int(hex_code[0:2], 16)
    green = int(hex_code[2:4], 16)
    blue = int(hex_code[4:6], 16)
    return red, green, blue, alpha  

def hex_to_decimal(hex_code: str) -> int:
    """
    Convert a hex color code to its decimal integer representation.

    Args:
        hex_code (str): Hex color string, e.g. "#FFAABB", "FFAABB", or "0xFFAABB".

    Returns:
        int: Decimal integer value of the hex code.

    Usage example:
    --------------
    ```python
    dec = hex_to_decimal("#FFAABB")
    print(dec)  # 16755387
    ```
    """
    assert isinstance(hex_code, str), "hex_code must be a string"
    hex_code = hex_code.lstrip("#").lstrip("0x")
    assert all(c in "0123456789abcdefABCDEF" for c in hex_code), "hex_code contains invalid characters"
    decimal_value = int(hex_code, 16)
    return decimal_value

def rgb_to_hsl(red: int, green: int, blue: int) -> tuple[int, int, int]:
    """
    Convert RGB color values to HSL color space.

    Args:
        red (int): Red component (0-255).
        green (int): Green component (0-255).
        blue (int): Blue component (0-255).

    Returns:
        tuple[int, int, int]: (Hue in degrees 0-360, Saturation in % 0-100, Lightness in % 0-100).

    Raises:
        AssertionError: If argument types are incorrect.

    Usage example:
    --------------
    ```python
    h, s, l = rgb_to_hsl(255, 0, 0)
    print(h, s, l)  # 0 100 50
    ```
    """
    assert all(isinstance(v, int) and 0 <= v <= 255 for v in (red, green, blue)), "RGB values must be integers 0-255"
    r, g, b = red / 255.0, green / 255.0, blue / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    luminance = (max_c + min_c) / 2.0

    if max_c == min_c:
        hue = saturation = 0
    else:
        delta = max_c - min_c
        saturation = delta / (1 - abs(2 * luminance - 1))
        if max_c == r:
            hue = ((g - b) / delta) % 6
        elif max_c == g:
            hue = ((b - r) / delta) + 2
        else:
            hue = ((r - g) / delta) + 4
        hue *= 60

    return round(hue), round(saturation * 100), round(luminance * 100)

def rgb_to_hsv(red: int, green: int, blue: int) -> tuple[int, int, int]:
    """
    Convert RGB color values to HSV color space.

    Args:
        red (int): Red component (0-255).
        green (int): Green component (0-255).
        blue (int): Blue component (0-255).

    Returns:
        tuple[int, int, int]: (Hue in degrees 0-360, Saturation in % 0-100, Value in % 0-100).

    Raises:
        AssertionError: If argument types are incorrect.

    Usage example:
    --------------
    ```python
    h, s, v = rgb_to_hsv(255, 0, 0)
    print(h, s, v)  # 0 100 100
    ```
    """
    assert all(isinstance(v, int) and 0 <= v <= 255 for v in (red, green, blue)), "RGB values must be integers 0-255"
    r, g, b = red / 255.0, green / 255.0, blue / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c

    if delta == 0:
        hue = 0
    elif max_c == r:
        hue = 60 * (((g - b) / delta) % 6)
    elif max_c == g:
        hue = 60 * (((b - r) / delta) + 2)
    else:
        hue = 60 * (((r - g) / delta) + 4)

    saturation = 0 if max_c == 0 else delta / max_c
    value = max_c

    return round(hue), round(saturation * 100), round(value * 100)

def rgb_to_cmyk(red: int, green: int, blue: int) -> tuple[int, int, int, int]:
    """
    Convert RGB color values to CMYK color space.

    Args:
        red (int): Red component (0-255).
        green (int): Green component (0-255).
        blue (int): Blue component (0-255).

    Returns:
        tuple[int, int, int, int]: (Cyan, Magenta, Yellow, Black) in percent 0-100.

    Raises:
        AssertionError: If argument types are incorrect.

    Usage example:
    --------------
    ```python
    c, m, y, k = rgb_to_cmyk(255, 0, 0)
    print(c, m, y, k)  # 0 100 100 0
    ```
    """
    assert all(isinstance(v, int) and 0 <= v <= 255 for v in (red, green, blue)), "RGB values must be integers 0-255"
    if red == 0 and green == 0 and blue == 0:
        return 0, 0, 0, 100

    c = 1 - (red / 255.0)
    m = 1 - (green / 255.0)
    y = 1 - (blue / 255.0)
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    return round(c * 100), round(m * 100), round(y * 100), round(k * 100)

if __name__ == "__main__":
    raise RuntimeError("This module is not meant to be run directly. Import it in your code.")