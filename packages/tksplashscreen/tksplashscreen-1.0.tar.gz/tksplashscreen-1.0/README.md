# SplashScreen

A simple and flexible Python splash screen library built with tkinter. Create customizable splash screens for your applications with ease.

## Features

- **Easy to use**: Create splash screens with just one line of code
- **Flexible positioning**: 9 predefined positions (corners, edges, center)
- **Auto-close functionality**: Automatically close after a specified time
- **Customizable appearance**: Custom fonts, colors, and messages
- **Thread-safe**: Non-blocking operation that doesn't freeze your main application
- **Dynamic updates**: Update message and colors while the splash screen is running

## Installation

```bash
pip install splashscreen
```

## Quick Start

```python
from splashscreen import SplashScreen

# Simple splash screen that closes after 3 seconds
splash = SplashScreen("Loading application...", close_after=3.0)

# Your application initialization code here
import time
time.sleep(5)  # Simulate work

# Splash will automatically close after 3 seconds
```

## Basic Usage

### Creating a Splash Screen

```python
from splashscreen import SplashScreen

# Basic splash screen
splash = SplashScreen("Welcome to MyApp!")

# With auto-close
splash = SplashScreen("Loading...", close_after=5.0)

# Custom positioning
splash = SplashScreen("Please wait...", placement="C")  # Center

# Custom colors and font
splash = SplashScreen(
    message="Initializing...",
    placement="TR",              # Top Right
    font="Arial, 24, bold",      # Font specification
    bg="#2E3440",               # Background color
    fg="#ECEFF4"                # Text color
)
```

### Placement Options

The `placement` parameter accepts the following values:

| Code | Position |
|------|----------|
| `'TL'` | Top Left |
| `'TC'` | Top Center |
| `'TR'` | Top Right |
| `'CL'` | Center Left |
| `'C'`  | Center |
| `'CR'` | Center Right |
| `'BL'` | Bottom Left |
| `'BC'` | Bottom Center |
| `'BR'` | Bottom Right (default) |

### Font Specification

Fonts can be specified in two ways:

```python
# As a string: "family, size, style"
font="Arial, 16, normal"
font="Times New Roman, 20, bold"
font="Courier, 14, italic"

# As a tuple
font=("Helvetica", 18, "bold")
```

### Color Specification

Colors can be specified as:

```python
# Named colors
bg="red"
fg="white"

# Hex colors
bg="#FF5733"
fg="#FFFFFF"

# RGB tuples (will be converted to hex)
bg=(255, 87, 51)    # Converts to #FF5733
```

## Advanced Usage

### Dynamic Updates

```python
splash = SplashScreen("Initializing...")

# Update the message
splash.update_message("Loading modules...")

# Append to existing message
splash.update_message("\nPlease wait...", append=True)

# Change background color
splash.update_color("#4CAF50")  # Green

# Close manually
splash.close()

# Close after delay
splash.close(close_after_sec=2.0)
```

### Progress Indication

```python
import time
from splashscreen import SplashScreen

splash = SplashScreen("Starting application...")

steps = [
    "Loading configuration...",
    "Connecting to database...",
    "Initializing modules...",
    "Loading user interface...",
    "Ready!"
]

for i, step in enumerate(steps):
    splash.update_message(f"Step {i+1}/{len(steps)}: {step}")
    time.sleep(1)  # Simulate work
    
splash.close(close_after_sec=1.0)
```

### Multiple Sequential Splash Screens

```python
def show_splash(message, placement, duration=2.0):
    splash = SplashScreen(
        message=message,
        placement=placement,
        close_after=duration,
        font="Verdana, 20, bold"
    )
    # Wait for splash to close before continuing
    time.sleep(duration + 0.1)

# Show splash screens in different positions
positions = ['TL', 'TR', 'BL', 'BR', 'C']
for pos in positions:
    show_splash(f"Position: {pos}", pos)
```

## API Reference

### SplashScreen Class

#### Constructor

```python
SplashScreen(
    message: str,
    close_after: Optional[float] = None,
    placement: Optional[str] = "BR",
    font: Optional[Union[str, Tuple]] = None,
    bg: str = "#00538F",
    fg: str = "white"
)
```

**Parameters:**
- `message` (str): The text to display on the splash screen
- `close_after` (float, optional): Time in seconds before auto-closing
- `placement` (str, optional): Position on screen (default: "BR")
- `font` (str|tuple, optional): Font specification (default: Calibri, 18, bold)
- `bg` (str, optional): Background color (default: "#00538F")
- `fg` (str, optional): Text color (default: "white")

#### Methods

##### `update_message(new_text: str, append: bool = False)`
Update the displayed message.

**Parameters:**
- `new_text` (str): New text to display
- `append` (bool): If True, append to existing text instead of replacing

##### `update_color(new_color: str)`
Change the background color of the splash screen.

**Parameters:**
- `new_color` (str): New background color

##### `close(close_after_sec: float = 0)`
Close the splash screen.

**Parameters:**
- `close_after_sec` (float): Delay in seconds before closing (default: immediate)

## Examples

### Loading Screen with Progress

```python
import time
from splashscreen import SplashScreen

def main():
    splash = SplashScreen(
        "MyApp is starting...",
        placement="C",
        font="Arial, 22, bold",
        bg="#2C3E50",
        fg="#ECF0F1"
    )
    
    # Simulate application startup
    modules = ["Config", "Database", "UI", "Plugins", "Assets"]
    
    for i, module in enumerate(modules):
        progress = f"Loading {module}... ({i+1}/{len(modules)})"
        splash.update_message(progress)
        
        # Change color based on progress
        if i < 2:
            splash.update_color("#E74C3C")  # Red for early stages
        elif i < 4:
            splash.update_color("#F39C12")  # Orange for middle stages
        else:
            splash.update_color("#27AE60")  # Green for final stages
            
        time.sleep(1.5)  # Simulate loading time
    
    splash.update_message("Ready! Starting application...")
    splash.close(close_after_sec=1.0)

if __name__ == "__main__":
    main()
```

### Multi-Stage Splash Screen

```python
from splashscreen import SplashScreen
import time

def startup_sequence():
    # Stage 1: Welcome
    welcome = SplashScreen(
        "Welcome to MyApplication!",
        placement="C",
        font="Times New Roman, 24, bold",
        bg="#8E44AD",
        close_after=2.0
    )
    time.sleep(2.2)  # Wait for close + small buffer
    
    # Stage 2: Loading
    loading = SplashScreen(
        "Initializing components...",
        placement="BR",
        font="Arial, 16, normal",
        bg="#3498DB"
    )
    
    for i in range(1, 6):
        loading.update_message(f"Loading component {i}/5...")
        time.sleep(0.8)
    
    loading.close()

startup_sequence()
```

## Requirements

- Python 3.6+
- tkinter (usually included with Python)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
