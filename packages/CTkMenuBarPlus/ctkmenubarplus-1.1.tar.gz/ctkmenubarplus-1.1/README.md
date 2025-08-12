# CTkMenuBarPlus
Modern menu bar widget library for customtkinter with enhanced features.

## Quick Navigation
- [Installation](#installation-anchor)
- [CTkMenuBar — Arguments](#ctkmenubar-arguments)
- [CTkTitleMenu — Arguments](#ctktitlemenu-arguments)
- [CustomDropdownMenu — Arguments](#customdropdownmenu-arguments)
- [CustomDropdownMenu — add_option() Parameters](#customdropdownmenu-add-option-params)
- [ContextMenu — Arguments](#contextmenu-arguments)
- [Keyboard Accelerators](#keyboard-accelerators-anchor)
- [Theming](#theming-anchor)
- [Error Handling](#error-handling-anchor)
- [Advanced Features](#advanced-features-anchor)

## Features
- Custom dropdown menus with full customization
- Menu bar integration - add menus to window top or title bar
- Keyboard shortcuts/accelerators - layout-independent key bindings
- Icons in menu items - PNG, JPG, or PIL Image support
- Checkable menu items - toggle states with visual feedback
- Context menus - right-click dropdown support
- Scrollable menus - automatic scrollbars for long option lists
- Dynamic menu control - enable/disable items programmatically
- Platform support - cross-platform (Windows title menu Windows-only)

## Installation

<a id="installation-anchor"></a>

```bash
pip install CTkMenuBarPlus
```

---

## Menu Types

## 1. CTkMenuBar

![menubar](https://github.com/Akascape/CTkMenuBar/assets/89206401/02c512b2-557f-4d59-86e0-a6eb9da3696c)

### Usage
```python
from CTkMenuBarPlus import *
import customtkinter as ctk

root = ctk.CTk()
menu_bar = CTkMenuBar(root)
file_button = menu_bar.add_cascade("File")
edit_button = menu_bar.add_cascade("Edit")
```

### Methods
- **.add_cascade(text, postcommand, kwargs)**: Add new menu button to the bar
- **.configure(kwargs)**: Update menu bar parameters
- **.cget(param)**: Get configuration parameter value
- **.show()**: Show the menu bar (if hidden)
- **.hide()**: Hide the menu bar
- **.toggle()**: Toggle menu bar visibility

### Arguments
<a id="ctkmenubar-arguments"></a>

| Parameter       | Type      | Default            | Description                              |
|-----------------|-----------|--------------------|------------------------------------------|
| **master**      | Widget    | -                  | Parent widget (root or frame)            |
| **bg_color**    | str/tuple | ["white", "black"] | Background color (theme tuple or string) |
| **height**      | int       | 25                 | Menu bar height in pixels                |
| **width**       | int       | 10                 | Menu button width in pixels              |
| **padx**        | int       | 5                  | Horizontal spacing between buttons       |
| **pady**        | int       | 2                  | Vertical padding                         |
| **postcommand** | callable  | None               | Function called before showing dropdown  |
| ***other_args** | various   | -                  | Additional CTkFrame parameters           |

---

## 2. CTkTitleMenu

_Windows Only - integrates with window title bar_

![titlebar](https://github.com/Akascape/CTkMenuBar/assets/89206401/da6cd858-f700-476c-a2f0-93a1c6335a4d)

### Usage
```python
from CTkMenuBarPlus import *
import customtkinter as ctk

root = ctk.CTk()
title_menu = CTkTitleMenu(root)
file_button = title_menu.add_cascade("File")
```

### Methods
- **.add_cascade(text, kwargs)**: Add menu button to title bar
- **.show()**: Show the title menu
- **.hide()**: Hide the title menu  
- **.toggle()**: Toggle title menu visibility

### Arguments
<a id="ctktitlemenu-arguments"></a>

| Parameter           | Type            | Default   | Description                           |
|---------------------|-----------------|-----------|---------------------------------------|
| **master**          | CTk/CTkToplevel | -         | Parent window (root or toplevel only) |
| **title_bar_color** | str/int         | "default" | Title bar color                       |
| **padx**            | int             | 10        | Spacing between menu buttons          |
| **width**           | int             | 10        | Width of menu buttons                 |
| **x_offset**        | int             | None      | Horizontal position offset            |
| **y_offset**        | int             | None      | Vertical position offset              |

---

## 3. CustomDropdownMenu

Core dropdown menu class with enhanced features - used by both CTkMenuBar and CTkTitleMenu.

### Usage
```python
from CTkMenuBarPlus import *

# Attach to any widget
dropdown = CustomDropdownMenu(widget=my_button)
dropdown.add_option("Option 1")
dropdown.add_separator()
submenu = dropdown.add_submenu("Submenu")
submenu.add_option("Sub Option")
```

### Enhanced Usage with New Features
```python
# Keyboard shortcuts
dropdown.add_option(
    option="Open", 
    command=open_file,
    accelerator="Ctrl+O"
)

# Checkable items
dropdown.add_option(
    option="Word Wrap",
    command=toggle_wrap,
    checkable=True,
    checked=True
)

# Icons in menu items
dropdown.add_option(
    option="Save",
    command=save_file,
    icon="assets/save.png",
    accelerator="Ctrl+S"
)

# Disabled items
dropdown.add_option(
    option="Advanced Settings",
    command=advanced_settings,
    enabled=False
)

# Dynamic state control
option_button = dropdown.add_option("Toggle Me", checkable=True)
option_button.set_checked(True)  # Set checked state
option_button.set_enabled(False)  # Disable item
```

### Methods
- **.add_option(option, command, kwargs)**: Add menu option with enhanced features
- **.add_separator()**: Add visual separator line
- **.add_submenu(submenu_name, kwargs)**: Add nested submenu
- **.configure(kwargs)**: Update dropdown appearance
- **.cget(param)**: Get configuration parameter
- **.show()**: Show the dropdown menu
- **.hide()**: Hide the dropdown menu
- **.destroy()**: Clean up resources and destroy menu

### Arguments
<a id="customdropdownmenu-arguments"></a>

| Parameter               | Type      | Default              | Description                             |
|-------------------------|-----------|----------------------|-----------------------------------------|
| **widget**              | Widget    | -                    | Widget that triggers this dropdown      |
| **master**              | Widget    | None                 | Parent widget (auto-determined if None) |
| **border_width**        | int       | 1                    | Border width in pixels                  |
| **width**               | int       | 150                  | Menu width in pixels                    |
| **height**              | int       | 25                   | Menu item height in pixels              |
| **bg_color**            | str/tuple | None                 | Background color                        |
| **corner_radius**       | int       | 10                   | Corner radius for rounded corners       |
| **border_color**        | str/tuple | "grey50"             | Border color                            |
| **separator_color**     | str/tuple | ("grey80", "grey20") | Separator line color                    |
| **text_color**          | str/tuple | ("black", "white")   | Text color                              |
| **fg_color**            | str/tuple | "transparent"        | Foreground color                        |
| **hover_color**         | str/tuple | ("grey75", "grey25") | Hover color                             |
| **font**                | CTkFont   | ("helvetica", 12)    | Font for menu text                      |
| **padx**                | int       | 3                    | Horizontal padding                      |
| **pady**                | int       | 3                    | Vertical padding                        |
| **cursor**              | str       | "hand2"              | Cursor type on hover                    |
| **max_visible_options** | int       | 10                   | Options before scrollbar appears        |
| **enable_scrollbar**    | bool      | True                 | Enable scrollbar for long menus         |
| **scrollbar_width**     | int       | 16                   | Scrollbar width in pixels               |

### add_option() Parameters
<a id="customdropdownmenu-add-option-params"></a>

| Parameter       | Type          | Default   | Description                                  |
|-----------------|---------------|-----------|----------------------------------------------|
| **option**      | str           | -         | Text to display for this option              |
| **command**     | callable      | None      | Function to call when selected               |
| **accelerator** | str           | None      | Keyboard shortcut (e.g., "Ctrl+S", "Alt+F4") |
| **icon**        | str/PIL.Image | None      | Icon file path or PIL Image object           |
| **checkable**   | bool          | False     | Whether item can be checked/unchecked        |
| **checked**     | bool          | False     | Initial checked state (if checkable=True)    |
| **enabled**     | bool          | True      | Whether item is initially enabled            |
| ***kwargs**     | various       | -         | Additional CTkButton styling options         |

---

## 4. ContextMenu

Right-click context menu with full dropdown functionality.

### Usage
```python
from CTkMenuBarPlus import *

# Create context menu for any widget
context_menu = ContextMenu(my_widget)
context_menu.add_option("Copy", copy_function, accelerator="Ctrl+C")
context_menu.add_option("Paste", paste_function, accelerator="Ctrl+V")
context_menu.add_separator()
context_menu.add_option("Delete", delete_function, accelerator="Delete")

# Right-click will automatically show the menu
```

### Methods
Same as CustomDropdownMenu - inherits all functionality plus:
- **Automatic right-click binding** to target widget and children
- **Cursor-position display** - appears where you right-click
- **Full feature support** - accelerators, icons, checkable items, submenus

### Arguments
<a id="contextmenu-arguments"></a>

| Parameter   | Type         | Description                                 |
|-------------|--------------|---------------------------------------------|
| **widget**  | CTkBaseClass | Widget to attach context menu to            |
| ***kwargs** | various      | All CustomDropdownMenu parameters supported |

---

## Theming

<a id="theming-anchor"></a>

CTkMenuBarPlus automatically adapts to customtkinter appearance modes:

```python
# Light/Dark mode support
ctk.set_appearance_mode("dark")  # "light" or "dark"

# Custom colors (theme tuples)
menu_bar = CTkMenuBar(
    root,
    bg_color=("white", "#2b2b2b"),  # (light_mode, dark_mode)
)

dropdown = CustomDropdownMenu(
    widget=button,
    bg_color=("white", "#1a1a1a"),
    text_color=("black", "white"),
    hover_color=("lightblue", "#3a3a3a")
)
```

---

## Error Handling

<a id="error-handling-anchor"></a>

The library includes comprehensive error handling:

```python
from CTkMenuBarPlus import MenuWidgetBindingError, MenuCommandExecutionError

try:
    dropdown.add_option("Test", invalid_command)
except MenuCommandExecutionError as e:
    print(f"Command error: {e}")
```

**Custom Exception Classes:**
- `CTkMenuBarError` - Base exception
- `MenuWidgetBindingError` - Widget binding issues
- `MenuCommandExecutionError` - Command execution problems  
- `MenuToggleError` - Show/hide toggle failures
- `MenuOptionError` - Menu option operations
- `MenuIconError` - Icon loading/processing errors
- `MenuPositioningError` - Menu positioning failures
- `MenuScrollError` - Scrollable menu issues

---

## Advanced Features

<a id="advanced-features-anchor"></a>

### Scrollable Menus
Large menus automatically get scrollbars:
```python
dropdown = CustomDropdownMenu(
    widget=button,
    max_visible_options=5,  # Show scrollbar after 5 items
    enable_scrollbar=True,
    scrollbar_width=16
)
```

### Keyboard Accelerators
<a id="keyboard-accelerators-anchor"></a>
Layout-independent shortcuts that work across keyboard layouts:
```python
# Supports: Ctrl, Alt, Shift, Cmd (macOS), CmdOrCtrl (Cmd on macOS, Ctrl on others)
# Keys: A-Z, 0-9, Function keys, special keys
dropdown.add_option("Open", open_func, accelerator="CmdOrCtrl+O")
dropdown.add_option("Save", save_func, accelerator="Ctrl+S")
dropdown.add_option("Save as", save_func, accelerator="Ctrl+Shift+S")
dropdown.add_option("Quit", quit_func, accelerator="Alt+F4")
```

#### Supported keys and modifiers

Modifiers
- Ctrl / Control
- Alt (Option on macOS)
- Shift
- Cmd (macOS only)
- CmdOrCtrl (Cmd on macOS, Ctrl elsewhere)

Keys (common to all platforms)
- Letters: A–Z
- Digits: 0–9
- Function keys: F1–F12
 
Special/navigation keys (platform-specific keycodes):

| Platform   | Keys                                                                                                                                                                                                                     |
|------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Windows    | Delete/Del, Insert/Ins, Home, End, Page_Up/PageUp/PgUp, Page_Down/PageDown/PgDn, Up/Down/Left/Right, Tab, Enter/Return, Escape/Esc, Space, Backspace, punctuation: plus (+), minus (-), equal (=), comma (,), period (.) |
| macOS      | Delete/Del (Backspace/Forward Delete), Insert, Home, End, Page_Up/PageUp/PgUp, Page_Down/PageDown/PgDn, Up/Down/Left/Right, Tab, Enter/Return, Escape/Esc, Space, Backspace                                              |
| Linux/X11  | Delete/Del, Insert/Ins, Home, End, Page_Up/PageUp/PgUp, Page_Down/PageDown/PgDn, Up/Down/Left/Right, Tab, Enter/Return, Escape/Esc, Space, Backspace                                                                     |

Notes
- Punctuation shortcuts are limited: on Windows we support +, -, =, ,, . as accelerator keys. Other punctuation (e.g., /, ;, etc.) are not currently mapped.
- Accelerators are layout‑independent: physical keycodes are used under the hood, so shortcuts work consistently across keyboard layouts.
- Use CmdOrCtrl in strings to automatically map to Command (macOS) or Control (Windows/Linux).

### Dynamic Control
Control menu items programmatically:
```python
option = dropdown.add_option("Toggle", checkable=True)

# Later in your code:
option.set_checked(True)    # Check the item
option.set_enabled(False)   # Disable the item
option.toggle_checked()     # Toggle check state
```

---

## Support & Issues

- **GitHub Issues**: [Report bugs or request features](https://github.com/KiTant/CTkMenuBarPlus/issues)
- **Discussions**: [Community support and questions](https://github.com/KiTant/CTkMenuBarPlus/discussions)

---

## Authors

- **Original Author**: [Akash Bora (Akascape)](https://github.com/Akascape) - CTkMenuBar 
- **Enhanced Features**: [xzyqox (KiTant)](https://github.com/KiTant) - Accelerators, icons, checkable items, context menus, etc
- **Base Dropdown**: [LucianoSaldivia](https://github.com/LucianoSaldivia) - Original dropdown implementation

---

## License

This project is licensed under the MIT License.

---
