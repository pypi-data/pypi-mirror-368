"""
Enhanced Custom Dropdown Menu for CTkMenuBarPlus

This module provides an advanced dropdown menu system with support for:
- Keyboard accelerators and shortcuts
- Icons in menu items
- Checkable menu items with state management
- Scrollable menus with automatic scrollbar
- Context menus (right-click)

Original Author: LucianoSaldivia | https://github.com/LucianoSaldivia
CTkMenuBar Author: Akash Bora (Akascape) | https://github.com/Akascape
Enhanced Features: xzyqox (KiTant) | https://github.com/KiTant

Version: Enhanced Edition 1.0
"""

from __future__ import annotations
import customtkinter
from functools import partial
import tkinter as tk
from typing import Callable, Optional, Union, List, Dict, Any, Tuple
import PIL.Image, PIL.ImageTk
import warnings
import sys


# Custom Exception Classes
class CTkMenuBarError(Exception):
    """Base exception class for CTkMenuBar dropdown menu errors."""
    pass


class MenuWidgetBindingError(CTkMenuBarError):
    """Raised when menu widget binding fails."""
    pass


class MenuCommandExecutionError(CTkMenuBarError):
    """Raised when menu command execution fails."""
    pass


class MenuToggleError(CTkMenuBarError):
    """Raised when menu show/hide toggle fails."""
    pass


class MenuOptionError(CTkMenuBarError):
    """Raised when menu option operations fail."""
    pass


class MenuIconError(CTkMenuBarError):
    """Raised when menu icon loading or processing fails."""
    pass


class MenuPositioningError(CTkMenuBarError):
    """Raised when menu positioning calculations fail."""
    pass


class MenuScrollError(CTkMenuBarError):
    """Raised when scrollable menu operations fail."""
    pass

# ===== CONSTANTS =====

# Timing constants (in milliseconds)
DEFAULT_SUBMENU_DELAY = 500  # Delay before showing submenu on hover

# Layout and spacing constants
DEFAULT_PADDING = 3  # Internal padding for menu items
DEFAULT_CORNER_RADIUS_FACTOR = 5  # Factor for calculating corner radius scaling
DEFAULT_BORDER_WIDTH = 1  # Default border width for menu items
DEFAULT_WIDTH = 150  # Default menu width in pixels
DEFAULT_HEIGHT = 25  # Default menu item height in pixels  
DEFAULT_CORNER_RADIUS = 10  # Default corner radius for rounded corners

# Theme color constants (light mode, dark mode)
DEFAULT_SEPARATOR_COLOR = ("grey80", "grey20")  # Separator line colors
DEFAULT_TEXT_COLOR = ("black", "white")  # Menu text colors
DEFAULT_HOVER_COLOR = ("grey75", "grey25")  # Hover colors
DEFAULT_BORDER_COLOR = "grey50"  # Border color

# Scrollbar constants
DEFAULT_MAX_VISIBLE_OPTIONS = 10  # Maximum options before scrollbar appears
SCROLLBAR_EXTRA_SPACE = 20  # Extra space for scrollbar
SCROLLBAR_WIDTH = 16  # Default scrollbar width

# Positioning constants  
SUBMENU_HORIZONTAL_OFFSET = 1  # Additional horizontal offset for submenu positioning
SUBMENU_OVERLAP_PREVENTION = 1  # Minimal gap to prevent visual overlap

# Icon constants
DEFAULT_ICON_SIZE = 16  # Default icon size in pixels

# Type aliases for better readability
ColorType = Union[str, Tuple[str, str]]
WidgetType = Union[customtkinter.CTkBaseClass, '_CDMSubmenuButton']
RootType = Union[customtkinter.CTk, customtkinter.CTkToplevel]

# Global storage for accelerator bindings, layout-independent
_GLOBAL_ACCEL_BINDINGS: Dict[int, Dict[str, Dict[int, List[Callable]]]] = {}
_LAST_ACCEL_EVENT = None


def _register_accelerator(root: RootType, accelerator: str, callback: Callable):
    """Register a keyboard accelerator that works regardless of keyboard layout.

    This function creates layout-independent keyboard shortcuts by binding both
    traditional keysym patterns and physical keycode handlers. This ensures
    shortcuts work consistently across different keyboard layouts and languages.

    Supported Modifiers: Ctrl, Alt, Shift, Cmd (macOS)
    Supported Keys: A-Z, 0-9, F1-F12, Delete, Insert, Home, End, Page_Up, Page_Down, etc.
    Supports both single keys (F1, F2, Delete) and modified keys (Ctrl+S, Alt+F4)

    Args:
        root: The root window (CTk or CTkToplevel) to bind the accelerator to
        accelerator: Accelerator string in format 'Modifier+Key' or just 'Key' (e.g., "Ctrl+S", "Alt+F4", "F1")
        callback: Function to call when the accelerator is triggered

    Examples:
        _register_accelerator(root, "Ctrl+S", save_function)
        _register_accelerator(root, "Alt+F4", close_function)
        _register_accelerator(root, "F1", help_function)
        _register_accelerator(root, "Delete", delete_function)
    """
    # Parse accelerator string (e.g., "Ctrl+S", "Alt+F4", "F1", "Delete")
    parts = accelerator.split('+')
    
    # Handle single keys (no modifier)
    if len(parts) == 1:
        modifier = None
        key = parts[0]
        modifier_lower = 'none'  # Special case for no modifier
        tkinter_modifier = None
    elif len(parts) == 2:
        modifier, key = parts
        modifier_lower = modifier.lower()
        # Map modifier names to Tkinter event patterns
        modifier_map = {
            'ctrl': 'Control',
            'alt': 'Alt',
            'shift': 'Shift',
            'cmd': 'Command'  # For macOS compatibility
        }
        
        if modifier_lower not in modifier_map:
            return  # Unsupported modifier
        tkinter_modifier = modifier_map[modifier_lower]
    else:
        return  # Invalid format
    
    # Enhanced key mapping including function keys and special keys
    key_upper = key.upper()
    
    # Platform-specific keycode dictionaries
    if sys.platform == 'win32':
        # Windows keycodes
        function_keys = {
            'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117,
            'F7': 118, 'F8': 119, 'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123
        }
        special_keys = {
            'DELETE': 46, 'DEL': 46,
            'INSERT': 45, 'INS': 45,
            'HOME': 36, 'END': 35,
            'PAGE_UP': 33, 'PAGEUP': 33, 'PGUP': 33,
            'PAGE_DOWN': 34, 'PAGEDOWN': 34, 'PGDN': 34,
            'UP': 38, 'DOWN': 40, 'LEFT': 37, 'RIGHT': 39,
            'TAB': 9,
            'ENTER': 13, 'RETURN': 13,
            'ESCAPE': 27, 'ESC': 27,
            'SPACE': 32,
            'BACKSPACE': 8,
            'PLUS': 107, '+': 107,
            'MINUS': 109, '-': 109,
            'EQUAL': 187, '=': 187,
            'COMMA': 188, ',': 188,
            'PERIOD': 190, '.': 190
        }
    elif sys.platform == 'darwin':
        # macOS keycodes
        function_keys = {
            'F1': 122, 'F2': 120, 'F3': 99,  'F4': 118, 'F5': 96,  'F6': 97,
            'F7': 98,  'F8': 100, 'F9': 101, 'F10': 109, 'F11': 103, 'F12': 111
        }
        special_keys = {
            'DELETE': 51, 'DEL': 117,  # 51 = Backspace, 117 = Forward Delete
            'INSERT': 114,
            'HOME': 115, 'END': 119,
            'PAGE_UP': 116, 'PAGEUP': 116, 'PGUP': 116,
            'PAGE_DOWN': 121, 'PAGEDOWN': 121, 'PGDN': 121,
            'UP': 126, 'DOWN': 125, 'LEFT': 123, 'RIGHT': 124,
            'TAB': 48,
            'ENTER': 36, 'RETURN': 76,
            'ESCAPE': 53, 'ESC': 53,
            'SPACE': 49,
            'BACKSPACE': 51,
            # For PLUS/MINUS/EQUAL etc macOS uses printable char handling
        }
    else:
        # Linux/X11 keycodes
        function_keys = {
            'F1': 67,  'F2': 68,  'F3': 69,  'F4': 70,  'F5': 71,  'F6': 72,
            'F7': 73,  'F8': 74,  'F9': 75,  'F10': 76,  'F11': 95,  'F12': 96
        }
        special_keys = {
            'DELETE': 119, 'DEL': 119,
            'INSERT': 118, 'INS': 118,
            'HOME': 110, 'END': 115,
            'PAGE_UP': 112, 'PAGEUP': 112, 'PGUP': 112,
            'PAGE_DOWN': 117, 'PAGEDOWN': 117, 'PGDN': 117,
            'UP': 111, 'DOWN': 116, 'LEFT': 113, 'RIGHT': 114,
            'TAB': 23,
            'ENTER': 36, 'RETURN': 36,
            'ESCAPE': 9, 'ESC': 9,
            'SPACE': 65,
            'BACKSPACE': 22,
        }
    
    # Determine keycode
    if key_upper in function_keys:
        keycode = function_keys[key_upper]
    elif key_upper in special_keys:
        keycode = special_keys[key_upper]
    elif len(key) == 1 and key.isalnum():
        # Regular alphanumeric keys (A-Z, 0-9)
        keycode = ord(key_upper)
    else:
        # Unsupported key
        warnings.warn(f"Unsupported key in accelerator: {key}")
        return

    # Store binding info
    root_id = root.winfo_id()
    bindings = _GLOBAL_ACCEL_BINDINGS.setdefault(root_id, {})
    modifier_bindings = bindings.setdefault(modifier_lower, {})
    callbacks = modifier_bindings.setdefault(keycode, [])
    callbacks.append(callback)

    # Create unique handler attribute name for this modifier
    handler_attr = f'_ctkmenubar_{modifier_lower}_binding'

    # Ensure we have the generic handler only once per root per modifier
    if not hasattr(root, handler_attr):
        def _handle_key_press(event, mod=modifier_lower):
            global _LAST_ACCEL_EVENT
            import time
            
            # Create event signature for deduplication
            current_time = time.time()
            event_sig = (event.keycode, mod, current_time)
            
            # Prevent multiple firing within 100ms window for same key+modifier
            if (_LAST_ACCEL_EVENT and 
                _LAST_ACCEL_EVENT[0] == event.keycode and 
                _LAST_ACCEL_EVENT[1] == mod and 
                current_time - _LAST_ACCEL_EVENT[2] < 0.1):
                return
                
            _LAST_ACCEL_EVENT = event_sig
            
            root_id_local = event.widget.winfo_toplevel().winfo_id()
            if root_id_local in _GLOBAL_ACCEL_BINDINGS:
                modifier_dict = _GLOBAL_ACCEL_BINDINGS[root_id_local].get(mod, {})
                cb_list = modifier_dict.get(event.keycode, [])
                if cb_list:  # Only process if we have callbacks
                    for cb in cb_list:
                        try:
                            cb()
                        except Exception as e:
                            raise MenuCommandExecutionError(f"Error in accelerator callback: {e}") from e
                    # Prevent further event propagation to avoid interfering with system bindings
                    return "break"

        # Bind to toplevel so it fires regardless of focus widget
        if modifier_lower == 'none':
            # For single keys, bind only to the root window to prevent multiple triggers
            root.bind('<KeyPress>', _handle_key_press, add='+')
        else:
            # For modified keys, use bind instead of bind_all to reduce duplication
            event_pattern = f'<{tkinter_modifier}-KeyPress>'
            root.bind(event_pattern, _handle_key_press, add='+')
            
        setattr(root, handler_attr, True)


class _CDMOptionButton(customtkinter.CTkButton):
    """Enhanced option button for dropdown menus with accelerator, icon, and state support."""
    
    def __init__(self, *args, **kwargs):
        """Initialize option button with enhanced features.
        
        Args:
            accelerator: Keyboard shortcut (e.g., "Ctrl+O")
            icon: Path to icon file or PIL Image object
            checkable: Whether this item can be checked/unchecked
            checked: Initial checked state
            enabled: Whether the item is initially enabled
            **kwargs: Additional arguments passed to CTkButton
        """
        # Extract and store custom parameters
        self.accelerator = kwargs.pop('accelerator', None)
        self.icon = kwargs.pop('icon', None)
        self.checkable = kwargs.pop('checkable', False)
        self.checked = kwargs.pop('checked', False)
        self.enabled = kwargs.pop('enabled', True)
        
        # Capture logical text before parent init so we can preserve it
        self._option_text = kwargs.get("text", "")

        # Initialize parent button
        super().__init__(*args, **kwargs)
        
        # Setup initial configuration
        self._configure_initial_state()
        self._setup_features()
    
    def _configure_initial_state(self) -> None:
        """Configure the initial state of the button."""
        if not self.enabled:
            self.configure(state="disabled")
    
    def _setup_features(self) -> None:
        """Setup all enhanced features (icon, accelerator, checkable state)."""
        if self.icon:
            self._setup_icon()
        if self.accelerator:
            self._setup_accelerator_display()
        if self.checkable:
            self.set_checked(self.checked)
    
    def _setup_icon(self) -> None:
        """Setup icon for the menu item."""
        try:
            # Load image from file or use provided PIL image
            if isinstance(self.icon, str):
                image = PIL.Image.open(self.icon)
            else:
                image = self.icon
            
            # Resize to standard icon size
            image = image.resize((DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE), PIL.Image.Resampling.LANCZOS)
            self.icon_image = customtkinter.CTkImage(
                light_image=image, 
                dark_image=image, 
                size=(DEFAULT_ICON_SIZE, DEFAULT_ICON_SIZE)
            )
            self.configure(image=self.icon_image)
            
        except Exception as e:
            raise MenuIconError(f"Error loading icon: {e}") from e
    
    def _setup_accelerator_display(self) -> None:
        """Ensure accelerator is reflected in display string."""
        self._refresh_display()
    
    def setParentMenu(self, menu: "CustomDropdownMenu") -> None:
        """Set the parent menu and bind accelerator if provided.
        
        Args:
            menu: The parent dropdown menu
        """
        self.parent_menu = menu
        
        if self.accelerator:
            self._bind_accelerator()
    
    def _bind_accelerator(self) -> None:
        """Bind keyboard accelerator to the command with error handling."""
        try:
            root = self.parent_menu.winfo_toplevel()
            
            # Bind traditional accelerator format
            tk_accelerator = self._convert_accelerator_format(self.accelerator)
            if tk_accelerator:
                root.bind(tk_accelerator, lambda e: self._execute_if_enabled())
            
            # Bind layout-independent accelerator
            _register_accelerator(root, self.accelerator, self._execute_if_enabled)
            
        except Exception as e:
            raise MenuIconError(f"Error binding accelerator {self.accelerator}: {e}") from e
    
    def _execute_if_enabled(self) -> None:
        """Execute button command only if enabled."""
        if self.enabled:
            self.invoke()
    
    def _convert_accelerator_format(self, accelerator: str) -> str:
        """Convert accelerator format from 'Ctrl+O' to '<Control-o>' or 'F1' to '<F1>'.
        
        Args:
            accelerator: Accelerator string in format 'Modifier+Key' or just 'Key'
            
        Returns:
            Tkinter-compatible accelerator string or empty string if invalid
        """
        if not accelerator:
            return ""
        
        parts = accelerator.split('+')
        
        # Handle single keys (no modifier)
        if len(parts) == 1:
            key = parts[0]
            
            # Map special keys to tkinter keysyms
            key_upper = key.upper()
            special_key_map = {
                'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5', 'F6': 'F6',
                'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10', 'F11': 'F11', 'F12': 'F12',
                'DELETE': 'Delete', 'DEL': 'Delete',
                'INSERT': 'Insert', 'INS': 'Insert',
                'HOME': 'Home', 'END': 'End',
                'PAGE_UP': 'Page_Up', 'PAGEUP': 'Page_Up', 'PGUP': 'Page_Up',
                'PAGE_DOWN': 'Page_Down', 'PAGEDOWN': 'Page_Down', 'PGDN': 'Page_Down',
                'UP': 'Up', 'DOWN': 'Down', 'LEFT': 'Left', 'RIGHT': 'Right',
                'TAB': 'Tab', 'ENTER': 'Return', 'RETURN': 'Return',
                'ESCAPE': 'Escape', 'ESC': 'Escape',
                'SPACE': 'space', 'BACKSPACE': 'BackSpace'
            }
            
            # Use special key mapping if available, otherwise use key as is
            if key_upper in special_key_map:
                tk_key = special_key_map[key_upper]
            else:
                tk_key = key
            
            return f"<{tk_key}>"
            
        elif len(parts) == 2:
            # Handle modified keys
            modifier, key = parts
            modifier_map = {
                'Ctrl': 'Control',
                'Alt': 'Alt', 
                'Shift': 'Shift',
                'Cmd': 'Command'
            }
            
            # Map special keys to tkinter keysyms
            key_upper = key.upper()
            special_key_map = {
                'F1': 'F1', 'F2': 'F2', 'F3': 'F3', 'F4': 'F4', 'F5': 'F5', 'F6': 'F6',
                'F7': 'F7', 'F8': 'F8', 'F9': 'F9', 'F10': 'F10', 'F11': 'F11', 'F12': 'F12',
                'DELETE': 'Delete', 'DEL': 'Delete',
                'INSERT': 'Insert', 'INS': 'Insert',
                'HOME': 'Home', 'END': 'End',
                'PAGE_UP': 'Page_Up', 'PAGEUP': 'Page_Up', 'PGUP': 'Page_Up',
                'PAGE_DOWN': 'Page_Down', 'PAGEDOWN': 'Page_Down', 'PGDN': 'Page_Down',
                'UP': 'Up', 'DOWN': 'Down', 'LEFT': 'Left', 'RIGHT': 'Right',
                'TAB': 'Tab', 'ENTER': 'Return', 'RETURN': 'Return',
                'ESCAPE': 'Escape', 'ESC': 'Escape',
                'SPACE': 'space', 'BACKSPACE': 'BackSpace',
                'PLUS': 'plus', '+': 'plus',
                'MINUS': 'minus', '-': 'minus',
                'EQUAL': 'equal', '=': 'equal',
                'COMMA': 'comma', ',': 'comma',
                'PERIOD': 'period', '.': 'period'
            }
            
            tk_modifier = modifier_map.get(modifier, modifier)
            
            # Use special key mapping if available, otherwise use lowercase key
            if key_upper in special_key_map:
                tk_key = special_key_map[key_upper]
            else:
                tk_key = key.lower()
            
            return f"<{tk_modifier}-{tk_key}>"
        
        else:
            return ""  # Invalid format
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the menu item.
        
        Args:
            enabled: Whether the item should be enabled
        """
        self.enabled = enabled
        self.configure(state="normal" if enabled else "disabled")
    
    def enable(self, enabled: bool = True) -> None:
        """Enable or disable the menu item (alias for set_enabled).
        
        Args:
            enabled: Whether the item should be enabled (default: True)
        """
        self.set_enabled(enabled)
    
    def set_checked(self, checked: bool) -> None:
        """Set the checked state for checkable items.
        
        Args:
            checked: Whether the item should be checked
        """
        if not self.checkable:
            return
        
        self.checked = checked
        self._refresh_display()
    
    def _update_check_display(self) -> None:
        """Deprecated: use _refresh_display()."""
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Compose and set the display text from logical text, checkmark, and accelerator."""
        base = self._option_text or ""
        # Apply checkmark prefix if checkable
        if self.checkable:
            prefix = "✅ " if getattr(self, "checked", False) else "❌  "
            base = f"{prefix}{base}"
        # Apply accelerator suffix with spacing
        if self.accelerator:
            base = f"{base}    {self.accelerator}"
        super().configure(text=base)
    
    def toggle_checked(self) -> None:
        """Toggle the checked state for checkable items."""
        if self.checkable:
            self.set_checked(not self.checked)
    
    # Enhanced cget and configure methods
    def cget(self, param: str) -> Any:
        """Get configuration parameter value with support for custom parameters.
        
        Args:
            param: Parameter name to retrieve
            
        Returns:
            Parameter value
        """
        custom_params = {
            "option": lambda: self._option_text,
            "accelerator": lambda: self.accelerator,
            "enabled": lambda: self.enabled,
            "checked": lambda: self.checked,
            "checkable": lambda: self.checkable,
            "icon": lambda: self.icon
        }
        
        if param in custom_params:
            return custom_params[param]()
        
        return super().cget(param)
    
    def configure(self, **kwargs) -> None:
        """Configure button with support for custom parameters.
        
        Args:
            **kwargs: Configuration parameters
        """
        # Handle custom parameters
        custom_handlers = {
            "option": self._handle_option_config,
            "accelerator": self._handle_accelerator_config,
            "enabled": self.set_enabled,
            "checked": self.set_checked,
            "checkable": self._handle_checkable_config,
            "icon": self._handle_icon_config
        }
        
        # Treat plain text updates as logical text updates to preserve decorations
        if "text" in kwargs and "option" not in kwargs:
            kwargs["option"] = kwargs.pop("text")

        for param, value in list(kwargs.items()):
            if param in custom_handlers:
                custom_handlers[param](value)
                kwargs.pop(param)
        
        # Configure remaining standard parameters
        if kwargs:
            super().configure(**kwargs)
    
    def _handle_option_config(self, value: str) -> None:
        """Handle logical option text change and refresh display."""
        self._option_text = value
        self._refresh_display()

    def _handle_accelerator_config(self, value: str) -> None:
        """Handle accelerator configuration change."""
        self.accelerator = value
        self._refresh_display()
        if hasattr(self, 'parent_menu'):
            self._bind_accelerator()
    
    def _handle_checkable_config(self, value: bool) -> None:
        """Handle checkable configuration change."""
        self.checkable = value
        self._refresh_display()
    
    def _handle_icon_config(self, value: Union[str, PIL.Image.Image]) -> None:
        """Handle icon configuration change."""
        self.icon = value
        if value:
            self._setup_icon()


class _CDMSubmenuButton(_CDMOptionButton):
    """Specialized button for submenu items that can hold child menus.
    
    This class extends _CDMOptionButton to provide submenu functionality,
    allowing menu items to open child dropdown menus when hovered or clicked.
    """
    
    def setSubmenu(self, submenu: "CustomDropdownMenu"):
        """Assign a submenu to this button.
        
        Args:
            submenu: The CustomDropdownMenu instance to assign as child menu
        """
        self.submenu = submenu

    def cget(self, param):
        if param == "submenu_name":
            return getattr(self, "_option_text", super().cget("text"))
        return super().cget(param)

    def configure(self, **kwargs):
        if "submenu_name" in kwargs:
            # Map submenu_name to logical option text and refresh
            kwargs["option"] = kwargs.pop("submenu_name")
        super().configure(**kwargs)


class CustomDropdownMenu(customtkinter.CTkFrame):
    """Enhanced dropdown menu with scrollbar support, accelerators, icons, and state management."""

    def __init__(self,
                 widget: WidgetType,
                 master: any = None,
                 border_width: int = DEFAULT_BORDER_WIDTH,
                 width: int = DEFAULT_WIDTH,
                 height: int = DEFAULT_HEIGHT,
                 bg_color: ColorType = None,
                 corner_radius: int = DEFAULT_CORNER_RADIUS,
                 border_color: ColorType = DEFAULT_BORDER_COLOR,
                 separator_color: ColorType = DEFAULT_SEPARATOR_COLOR,
                 text_color: ColorType = DEFAULT_TEXT_COLOR,
                 fg_color: ColorType = "transparent",
                 hover_color: ColorType = DEFAULT_HOVER_COLOR,
                 font: customtkinter.CTkFont = ("helvetica", 12),
                 padx: int = DEFAULT_PADDING,
                 pady: int = DEFAULT_PADDING,
                 cursor: str = "hand2",
                 max_visible_options: int = DEFAULT_MAX_VISIBLE_OPTIONS,
                 enable_scrollbar: bool = True,
                 scrollbar_width: int = SCROLLBAR_WIDTH,
                 **kwargs):
        """Initialize the dropdown menu with enhanced features.
        
        Args:
            widget: The widget that triggers this menu
            master: Parent widget (auto-determined if None)
            border_width: Width of the menu border
            width: Menu width in pixels
            height: Height of menu items in pixels
            bg_color: Background color
            corner_radius: Corner radius for rounded corners
            border_color: Border color
            separator_color: Color for separator lines
            text_color: Text color for menu items
            fg_color: Foreground color
            hover_color: Color when hovering over items
            font: Font for menu text
            padx: Horizontal padding
            pady: Vertical padding
            cursor: Cursor type when hovering
            max_visible_options: Max options before scrollbar appears
            enable_scrollbar: Whether to enable scrollbar
            scrollbar_width: Width of the scrollbar
            **kwargs: Additional arguments passed to CTkFrame
        """
        # Setup master and bindings based on widget type
        master = self._setup_master_and_bindings(widget, master)
        
        # Initialize the CTkFrame
        super().__init__(
            master=master,
            border_width=border_width,
            fg_color=bg_color,
            border_color=border_color,
            corner_radius=corner_radius,
            **kwargs)
        
        # Store configuration parameters
        self._store_configuration(
            widget, master, border_width, width, height, bg_color, 
            corner_radius, border_color, separator_color, text_color, 
            fg_color, hover_color, font, padx, pady, cursor, 
            max_visible_options, enable_scrollbar, scrollbar_width
        )
        
        # Initialize menu state and components
        self._initialize_menu_state()
        self._setup_menu_widget()
    
    def _setup_master_and_bindings(self, widget: WidgetType, master: any) -> any:
        """Setup master widget and mouse event bindings based on widget type.
        
        Args:
            widget: The trigger widget
            master: Proposed master widget
            
        Returns:
            The determined master widget
        """
        # Prefer robust isinstance checks over fragile name introspection
        try:
            from .menu_bar import CTkMenuBar
        except Exception:
            CTkMenuBar = None
        try:
            from .title_menu_win import CTkTitleMenu
        except Exception:
            CTkTitleMenu = None

        parent = getattr(widget, "master", None)

        # Route based on actual parent type when available
        if CTkTitleMenu is not None and isinstance(parent, CTkTitleMenu):
            return self._setup_title_menu_bindings(widget, master)
        if CTkMenuBar is not None and isinstance(parent, CTkMenuBar):
            return self._setup_menu_bar_bindings(widget, master)

        # Default safe path
        return self._setup_default_bindings(widget, master)
    
    def _setup_title_menu_bindings(self, widget: WidgetType, master: any) -> any:
        """Setup bindings for title menu context."""
        tl = widget.winfo_toplevel()
        tl.bind("<ButtonPress>", self._checkIfMouseLeft, add="+")
        tl.bind("<Button-1>", self._checkIfMouseLeft, add="+")
        resolved_master = master if master is not None else getattr(widget, "master", tl)
        if hasattr(widget, "master") and hasattr(widget.master, "menu"):
            try:
                widget.master.menu.append(self)
            except Exception:
                pass
        return resolved_master
    
    def _setup_menu_bar_bindings(self, widget: WidgetType, master: any) -> any:
        """Setup bindings for menu bar context."""
        tl = widget.winfo_toplevel()
        tl.bind("<ButtonPress>", self._checkIfMouseLeft, add="+")
        tl.bind("<Button-1>", self._checkIfMouseLeft, add="+")

        # Determine an appropriate master: prefer the menubar's master if present
        if master is None:
            menubar = getattr(widget, "master", None)
            master = getattr(menubar, "master", tl) if menubar is not None else tl

        if hasattr(widget, "master") and hasattr(widget.master, "menu"):
            try:
                widget.master.menu.append(self)
            except Exception:
                pass

        return master
    
    def _setup_default_bindings(self, widget: WidgetType, master: any) -> any:
        """Setup bindings for default context."""
        tl = widget.winfo_toplevel()
        tl.bind("<ButtonPress>", self._checkIfMouseLeft, add="+")
        tl.bind("<Button-1>", self._checkIfMouseLeft, add="+")

        if master is None:
            parent = getattr(widget, "master", None)
            # Prefer the parent's master if available
            master = getattr(parent, "master", parent) if parent is not None else tl
            if master is None:
                master = tl

        return master
    
    def _store_configuration(self, widget, master, border_width, width, height, bg_color, 
                           corner_radius, border_color, separator_color, text_color, 
                           fg_color, hover_color, font, padx, pady, cursor, 
                           max_visible_options, enable_scrollbar, scrollbar_width):
        """Store all configuration parameters as instance variables."""
        # Core widget references
        self.menu_seed_object = widget
        self.master = master
        
        # Visual configuration
        self.border_color = border_color
        self.border_width = border_width
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self.fg_color = fg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.font = font
        self.separator_color = separator_color
        
        # Layout configuration
        self.height = height
        self.width = width
        self.padx = padx
        self.pady = pady
        self.cursor = cursor
        
        # Scrollbar configuration
        self.max_visible_options = max_visible_options
        self.enable_scrollbar = enable_scrollbar
        self.scrollbar_width = scrollbar_width
    
    def _initialize_menu_state(self):
        """Initialize menu state variables and containers."""
        # Menu state
        self.hovered = False
        self.is_submenu = False
        
        # Scrollbar components
        self._scrollable_frame = None
        self._options_container = self  # Will be changed to scrollable frame if needed
        
        # Menu options storage
        self._options_list: List[Union[_CDMOptionButton, _CDMSubmenuButton]] = []
    
    def _setup_menu_widget(self):
        """Setup the menu widget command binding."""
        try:
            self.menu_seed_object.configure(command=self.toggleShow)
        except Exception as e:
            raise MenuWidgetBindingError(f"Failed to set up menu widget binding: {e}") from e
    
    def selectOption(self, command: Optional[Callable]) -> None:
        """Execute the selected option command and hide all menus."""
        self._hideAllMenus()
        if command and callable(command):
            try:
                command()
            except Exception as e:
                raise MenuCommandExecutionError(f"Failed to execute menu command: {e}") from e

    def _dummy_command(*args, **kwargs) -> None:
        """Default empty command for menu options."""
        pass

    def add_option(self,
                   option: str,
                   command: Optional[Callable] = None,
                   accelerator: Optional[str] = None,
                   icon: Optional[Union[str, PIL.Image.Image]] = None,
                   checkable: bool = False,
                   checked: bool = False,
                   enabled: bool = True,
                   **kwargs) -> _CDMOptionButton:
        """Add a new option to the dropdown menu.

        Args:
            option: The text to display for this option
            command: The function to call when this option is selected
            accelerator: Keyboard shortcut (e.g., "Ctrl+O", "Alt+F4")
            icon: Path to icon file or PIL Image object
            checkable: Whether this item can be checked/unchecked
            checked: Initial checked state
            enabled: Whether the item is initially enabled
            **kwargs: Additional arguments to pass to the button

        Returns:
            The created option button

        Raises:
            ValueError: If option text is empty or None
        """
        # Validate input parameters
        self._validate_option_input(option)
        
        # Store original command for checkable items
        original_command = command
        
        # Process command (but keep original for checkable items)
        processed_command = self._process_option_command(command, checkable)
        
        # Check for duplicate accelerators
        if accelerator and self._has_duplicate_accelerator(accelerator, option):
            return self._get_existing_option_with_accelerator(accelerator)
        
        # Create and configure the option button
        option_button = self._create_option_button(
            option, processed_command, accelerator, icon, checkable, checked, enabled, **kwargs
        )
        
        # Set up checkable command wrapper if needed (using original command)
        if checkable and original_command and original_command != self._dummy_command:
            self._setup_checkable_command(option_button, original_command)
        
        # Add to menu and update display
        self._add_option_to_menu(option_button)
        
        return option_button
    
    def _validate_option_input(self, option: str) -> None:
        """Validate option input parameters.
        
        Args:
            option: The option text to validate
            
        Raises:
            ValueError: If option text is invalid
        """
        if not option or not isinstance(option, str):
            raise ValueError("Option text must be a non-empty string")
    
    def _process_option_command(self, command: Optional[Callable], checkable: bool) -> Callable:
        """Process and wrap the command for checkable items.
        
        Args:
            command: The original command
            checkable: Whether the item is checkable
            
        Returns:
            The processed command
        """
        if command is None:
            return self._dummy_command
        
        # For checkable items, return the original command - it will be wrapped later
        return command
    
    def _has_duplicate_accelerator(self, accelerator: str, option: str) -> bool:
        """Check if accelerator is already in use.
        
        Args:
            accelerator: The accelerator to check
            option: The option text (for warning message)
            
        Returns:
            True if duplicate found
        """
        for existing in self._options_list:
            if (hasattr(existing, "accelerator") and existing.accelerator == accelerator):
                warnings.warn(f"Duplicate accelerator '{accelerator}' detected for menu option '{option}'. "
                              f"Skipping addition to prevent conflicts.")
                return True
        return False
    
    def _get_existing_option_with_accelerator(self, accelerator: str) -> _CDMOptionButton:
        """Get existing option with the specified accelerator.
        
        Args:
            accelerator: The accelerator to find
            
        Returns:
            The existing option button
        """
        for existing in self._options_list:
            if (hasattr(existing, "accelerator") and existing.accelerator == accelerator):
                return existing
        return None  # Should not happen if _has_duplicate_accelerator returned True
    
    def _create_option_button(self,
                              option: str, command: Callable,
                              accelerator: Optional[str],
                              icon: Optional[Union[str, PIL.Image.Image]],
                              checkable: bool,
                              checked: bool,
                              enabled: bool, **kwargs) -> _CDMOptionButton:
        """Create and configure an option button.
        
        Args:
            option: Option text
            command: Command to execute
            accelerator: Keyboard shortcut
            icon: Icon for the option
            checkable: Whether item is checkable
            checked: Initial checked state
            enabled: Whether item is enabled
            **kwargs: Additional button arguments
            
        Returns:
            The created option button
        """
        option_button = _CDMOptionButton(
            self._options_container,
            width=self.width,
            height=self.height,
            text=option,
            anchor="w",
            text_color=self.text_color,
            command=partial(self.selectOption, command),
            accelerator=accelerator,
            icon=icon,
            checkable=checkable,
            checked=checked,
            enabled=enabled,
            **kwargs
        )
        
        # Configure button appearance
        option_button.configure(cursor=self.cursor)
        
        return option_button
    
    def _setup_checkable_command(self, option_button: _CDMOptionButton, original_command: Callable) -> None:
        """Setup command wrapper for checkable items.
        
        Args:
            option_button: The option button
            original_command: The original command to wrap
        """
        def checkable_command():
            # Toggle the checked state first
            option_button.toggle_checked()
            # Then execute the original command with the new state
            if original_command:
                try:
                    # Try to pass the checked state to the command
                    original_command(option_button.checked)
                except TypeError:
                    # If command doesn't accept parameters, call without them
                    original_command()
        
        # Update the button's command
        option_button.configure(command=partial(self.selectOption, checkable_command))
    
    def _add_option_to_menu(self, option_button: _CDMOptionButton) -> None:
        """Add option button to the menu and configure it.
        
        Args:
            option_button: The option button to add
        """
        # Set parent menu and configure
        option_button.setParentMenu(self)
        self._options_list.append(option_button)
        self._configureButton(option_button)

        # Pack option with calculated padding based on corner radius
        option_button.pack(
            side="top",
            fill="both",
            expand=True,
            # Dynamic padding: base padding + corner radius scaling factor
            padx=DEFAULT_PADDING+(self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR),
            pady=DEFAULT_PADDING+(self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR)
        )
        
        # Add submenu hover binding if this is a submenu
        if self.is_submenu:
            option_button.bind("<Enter>", lambda e, submenu=self: submenu.change_hover(self), add="+")
            self._setup_submenu_timers(option_button)
            
        # Update scrollbar visibility
        self._update_scrollbar_visibility()

    def add_submenu(self, submenu_name: str,
                    max_visible_options: int = None,
                    enable_scrollbar: bool = None,
                    scrollbar_width: int = None,
                    **kwargs) -> "CustomDropdownMenu":
        """
        Add a submenu to the dropdown menu.

        Args:
            submenu_name: Name of the submenu
            max_visible_options: Maximum number of visible options before scrollbar appears (inherits from parent if None)
            enable_scrollbar: Whether to enable scrollbar for this submenu (inherits from parent if None)
            scrollbar_width: Width of the scrollbar (inherits from parent if None)
            **kwargs: Additional arguments for the submenu button

        Returns:
            The created submenu
        """
        # Extract scrollbar parameters from kwargs if provided there
        if max_visible_options is None:
            max_visible_options = kwargs.pop('max_visible_options', self.max_visible_options)
        if enable_scrollbar is None:
            enable_scrollbar = kwargs.pop('enable_scrollbar', self.enable_scrollbar)
        if scrollbar_width is None:
            scrollbar_width = kwargs.pop('scrollbar_width', self.scrollbar_width)

        submenuButtonSeed = _CDMSubmenuButton(self._options_container, text=submenu_name, anchor="w",
                                              text_color=self.text_color,
                                              width=self.width, height=self.height, **kwargs)
        submenuButtonSeed.setParentMenu(self)
        self._options_list.append(submenuButtonSeed)
        self._configureButton(submenuButtonSeed)

        submenu = CustomDropdownMenu(
            master=self.master,
            height=self.height,
            width=self.width,
            widget=submenuButtonSeed,
            fg_color=self.fg_color,
            bg_color=self.bg_color,
            hover_color=self.hover_color,
            corner_radius=self.corner_radius,
            border_width=self.border_width,
            border_color=self.border_color,
            separator_color=self.separator_color,
            text_color=self.text_color,
            font=self.font,
            max_visible_options=max_visible_options,
            enable_scrollbar=enable_scrollbar,
            scrollbar_width=scrollbar_width)

        submenuButtonSeed.setSubmenu(submenu=submenu)
        submenuButtonSeed.configure(command=submenu.toggleShow)
        submenu.is_submenu = True

        submenu.bind("<Enter>", lambda e, sub=self: self.change_hover(self), add="+")

        submenuButtonSeed.configure(cursor=self.cursor)

        submenuButtonSeed.pack(
            side="top",
            fill="both",
            expand=True,
            padx=DEFAULT_PADDING + (self.corner_radius / DEFAULT_CORNER_RADIUS_FACTOR),
            pady=DEFAULT_PADDING + (self.corner_radius / DEFAULT_CORNER_RADIUS_FACTOR)
        )

        self._setup_submenu_timers(submenuButtonSeed, submenu)

        # Update scrollbar visibility
        self._update_scrollbar_visibility()

        return submenu

    def add_separator(self) -> None:
        separator = customtkinter.CTkFrame(
            master=self,
            height=2,
            width=self.width,
            fg_color=self.separator_color,
            border_width=0
        )
        separator.pack(
            side="top",
            fill="x",
            expand=True,
        )

    def remove_option(self, option_name: str) -> bool:
        """Remove a single option or submenu by its display text.
        
        Args:
            option_name: Visible text of the option/submenu to remove.

        Returns:
            True if an item was removed, False if no matching item was found.
        """
        try:
            if not option_name or not isinstance(option_name, str):
                return False

            # Normalize the requested name once
            target = self._strip_display_artifacts(option_name).strip()

            removed = False
            for option in self._options_list[:]:
                try:
                    # Prefer stored logical text when available
                    try:
                        current = option.cget('option')
                    except Exception:
                        current = self._normalized_text_for_option(option)
                    if current == target or current.lower() == target.lower():
                        # If this is a submenu option, first cancel any pending timers
                        # which may have been scheduled on either this menu (self) or the submenu.
                        if isinstance(option, _CDMSubmenuButton) and hasattr(option, 'submenu') and option.submenu:
                            try:
                                submenu = option.submenu
                                if hasattr(submenu, "_timer_id") and submenu._timer_id:
                                    try:
                                        # Attempt cancel on parent scheduler
                                        self.after_cancel(submenu._timer_id)
                                    except Exception:
                                        pass
                                    try:
                                        # Attempt cancel on submenu as well (covers other case)
                                        submenu.after_cancel(submenu._timer_id)
                                    except Exception:
                                        pass
                                    submenu._timer_id = None
                            except Exception:
                                pass
                            # Now it is safe to destroy the submenu
                            try:
                                option.submenu.destroy()
                            except Exception:
                                pass

                        # Disable and destroy the button widget itself
                        try:
                            if hasattr(option, 'enable'):
                                option.enable(False)
                            option.destroy()
                        except Exception:
                            pass

                        # Remove from internal list
                        try:
                            self._options_list.remove(option)
                        except ValueError:
                            pass

                        removed = True
                        break
                except Exception:
                    # Continue searching other options even if one errors
                    continue

            if removed:
                # Reevaluate scrollbar state after removal
                self._update_scrollbar_visibility()
            return removed
        except Exception:
            return False

    def clean(self) -> None:
        """Remove all options, submenus, and separators, resetting the menu.
        
        This performs a thorough cleanup:
        - Cancels submenu timers
        - Destroys all submenu instances
        - Destroys all option widgets
        - Destroys separator frames
        - Destroys the scrollable frame (if present) and resets container
        - Updates scrollbar visibility/state
        """
        # First, attempt to cancel any submenu timers
        try:
            self._cleanup_submenu_timers()
        except Exception:
            pass

        # Destroy option widgets and any attached submenus
        for option in self._options_list[:]:
            try:
                if isinstance(option, _CDMSubmenuButton) and hasattr(option, 'submenu') and option.submenu:
                    try:
                        option.submenu.destroy()
                    except Exception:
                        pass
                try:
                    if hasattr(option, 'enable'):
                        option.enable(False)
                except Exception:
                    pass
                option.destroy()
            except Exception:
                pass

        # Clear internal list
        self._options_list.clear()

        # Destroy separator frames (but keep scrollable frame for dedicated handling)
        try:
            for child in list(self.winfo_children()):
                # Skip CTkScrollableFrame (handled below)
                if isinstance(child, getattr(customtkinter, 'CTkScrollableFrame', ())):
                    continue
                # Destroy plain frames that are used as separators
                if isinstance(child, customtkinter.CTkFrame):
                    try:
                        child.destroy()
                    except Exception:
                        pass
        except Exception:
            pass

        # Destroy scrollable frame if present and reset container
        try:
            if getattr(self, '_scrollable_frame', None) is not None:
                try:
                    self._scrollable_frame.destroy()
                except Exception:
                    pass
                self._scrollable_frame = None
            self._options_container = self
        except Exception:
            pass

        # Finally, update scrollbar visibility/state
        try:
            self._update_scrollbar_visibility()
        except Exception:
            pass

    def _strip_display_artifacts(self, text: str) -> str:
        """Strip checkmark prefixes and legacy accelerator separators from text."""
        if not isinstance(text, str):
            return str(text)
        # Remove checkmark prefixes
        if text.startswith("✅ "):
            text = text[2:]
        elif text.startswith("❌  "):
            text = text[3:]
        # Remove legacy tab-based accelerator suffix if present
        if '\t' in text:
            text = text.split('\t', 1)[0]
        return text.strip()

    def _normalized_text_for_option(self, option_widget: Union['_CDMOptionButton', '_CDMSubmenuButton']) -> str:
        """Return the logical name of an option, without checkmarks or accelerator text."""
        try:
            raw = option_widget.cget('text')
        except Exception:
            raw = ''
        text = self._strip_display_artifacts(raw)

        # Remove the runtime accelerator suffix that is added as "    <accel>"
        accel = getattr(option_widget, 'accelerator', None)
        if accel and isinstance(text, str):
            expected_suffix = f"    {accel}"
            if text.endswith(expected_suffix):
                text = text[: -len(expected_suffix)]

        return text.strip()

    def _show(self) -> None:
        """Show the dropdown menu at the appropriate position."""
        dpi = self._get_widget_scaling() if hasattr(self, "_get_widget_scaling") else (self.winfo_fpixels('1i') / 72.0)
        
        if isinstance(self.menu_seed_object, _CDMSubmenuButton):
            self._show_submenu_positioned(dpi)
        else:
            self._show_main_menu_positioned(dpi)
        
        self.lift()
        self.focus()
    
    def _show_submenu_positioned(self, dpi: float) -> None:
        """Position and show submenu relative to its parent button.
        
        Args:
            dpi: Display DPI scaling factor
        """
        button_x, button_y, button_width = self._get_submenu_button_position()
        parent_menu = self.menu_seed_object.parent_menu
        
        self.place(
            in_=parent_menu,
            x=(button_x + button_width) / dpi + self.padx + SUBMENU_HORIZONTAL_OFFSET,
            y=button_y / dpi - self.pady
        )
    
    def _show_main_menu_positioned(self, dpi: float) -> None:
        """Position and show main menu relative to its trigger widget.
        
        Args:
            dpi: Display DPI scaling factor
        """
        # Use root-relative coordinates for both the trigger and the placement container
        # to avoid coordinate space mismatch on high-DPI and nested layouts.
        container = getattr(self, "master", None) or self.winfo_toplevel()

        # Ensure geometry info is up-to-date
        try:
            self.menu_seed_object.update_idletasks()
            container.update_idletasks()
        except Exception:
            pass

        btn_root_x = self.menu_seed_object.winfo_rootx()
        btn_root_y = self.menu_seed_object.winfo_rooty()
        cont_root_x = container.winfo_rootx()
        cont_root_y = container.winfo_rooty()

        rel_x = (btn_root_x - cont_root_x) / dpi + self.padx
        rel_y = (btn_root_y - cont_root_y + self.menu_seed_object.winfo_height()) / dpi + self.pady

        self.place(x=rel_x, y=rel_y)
    
    def _get_submenu_button_position(self) -> tuple[int, int, int]:
        """Get the position and dimensions of the submenu button.
        
        Returns:
            Tuple of (x, y, width) coordinates
        """
        button_x = self.menu_seed_object.winfo_x()
        button_y = self.menu_seed_object.winfo_y()
        button_width = self.menu_seed_object.winfo_width()
        
        # Check if button is inside a scrollable frame
        parent_menu = self.menu_seed_object.parent_menu
        if self._is_in_scrollable_frame(parent_menu):
            button_x, button_y = self._adjust_for_scrollable_frame(parent_menu, button_x, button_y)
        
        return button_x, button_y, button_width
    
    def _is_in_scrollable_frame(self, parent_menu) -> bool:
        """Check if the button is inside a scrollable frame.
        
        Args:
            parent_menu: The parent menu to check
            
        Returns:
            True if button is in scrollable frame
        """
        return (hasattr(parent_menu, '_scrollable_frame') and 
                parent_menu._scrollable_frame is not None)
    
    def _adjust_for_scrollable_frame(self, parent_menu, button_x: int, button_y: int) -> tuple[int, int]:
        """Adjust button coordinates for scrollable frame offset.
        
        Args:
            parent_menu: The parent menu containing the scrollable frame
            button_x: Original button x coordinate
            button_y: Original button y coordinate
            
        Returns:
            Adjusted (x, y) coordinates
        """
        scrollable_frame = parent_menu._scrollable_frame
        frame_x = scrollable_frame.winfo_x()
        frame_y = scrollable_frame.winfo_y()
        
        return button_x + frame_x, button_y + frame_y

    def _hide(self, *args, **kwargs) -> None:
        """Hide the dropdown menu and cancel any pending timers."""
        self._cancel_pending_timer()
        self.place_forget()
    
    def _cancel_pending_timer(self) -> None:
        """Cancel any pending timer to prevent unwanted callbacks."""
        if hasattr(self, '_timer_id') and self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except:
                pass
            self._timer_id = None

    def _hideParentMenus(self, *args, **kwargs) -> None:
        """Hide all parent menus in the hierarchy."""
        if isinstance(self.menu_seed_object, _CDMSubmenuButton):
            parent_menu = self.menu_seed_object.parent_menu
            parent_menu._hideParentMenus()
            parent_menu._hide()

    def _hideChildrenMenus(self, *args, **kwargs) -> None:
        """Hide all child submenus."""
        for submenu in self._get_submenus():
            submenu._hide()

    def _hideAllMenus(self, *args, **kwargs) -> None:
        """Hide all menus in the hierarchy and clean up timers."""
        self._cleanup_submenu_timers()
        self._hideChildrenMenus()
        self._hide()
        self._hideParentMenus()

    def _collapseSiblingSubmenus(self, button: Union[_CDMOptionButton, _CDMSubmenuButton], *args, **kwargs) -> None:
        """Collapse all sibling submenus except the one associated with the given button.
        
        Args:
            button: The button whose submenu should remain open
        """
        for option in self._options_list:
            if option != button and isinstance(option, _CDMSubmenuButton):
                option.submenu._hideChildrenMenus()
                option.submenu._hide()

    def toggleShow(self, *args, **kwargs) -> None:
        """Toggle the visibility of the dropdown menu.
        
        This method shows the menu if it's hidden, or hides it if it's visible.
        Called when the menu button is clicked.
        """
        try:
            self._hide_sibling_menus()
            
            if self.winfo_viewable():
                self._hideChildrenMenus()
                self._hide()
            else:
                self._show()
                self.lift()
        except Exception as e:
            raise MenuToggleError(f"Failed to toggle menu visibility: {e}") from e

    def _hide_sibling_menus(self) -> None:
        """Hide sibling menus in menu bar or title menu context."""
        widget_base = self.menu_seed_object.master.winfo_name()
        if widget_base.startswith("!ctktitlemenu") or widget_base.startswith("!ctkmenubar"):
            for menu in self.menu_seed_object.master.menu:
                if menu != self:
                    menu._hide()

    def _configureButton(self, button: customtkinter.CTkButton) -> None:
        """Configure button appearance and behavior.
        
        Args:
            button: The button to configure
        """
        self._apply_button_styling(button)
        self._bind_button_events(button)
    
    def _apply_button_styling(self, button: customtkinter.CTkButton) -> None:
        """Apply visual styling to a button.
        
        Args:
            button: The button to style
        """
        button.configure(fg_color="transparent")
        if self.fg_color:
            button.configure(fg_color=self.fg_color)
        if self.hover_color:
            button.configure(hover_color=self.hover_color)
        if self.font:
            button.configure(font=self.font)
    
    def _bind_button_events(self, button: customtkinter.CTkButton) -> None:
        """Bind events to a button.
        
        Args:
            button: The button to bind events to
        """
        button.bind("<Enter>", partial(self._collapseSiblingSubmenus, button))

    def _get_submenus(self) -> List["CustomDropdownMenu"]:
        """Get list of all submenus in this menu.
        
        Returns:
            List of submenu instances
        """
        return [option.submenu for option in self._options_list 
                if isinstance(option, _CDMSubmenuButton)]

    def _get_coordinates(self, x_root: int, y_root: int) -> bool:
        """Check if coordinates are within menu bounds.
        
        Args:
            x_root: Root x coordinate
            y_root: Root y coordinate
            
        Returns:
            True if coordinates are within menu bounds
        """
        return (self.winfo_rootx() < x_root < self.winfo_rootx() + self.winfo_width() and
                self.winfo_rooty() < y_root < self.winfo_rooty() + self.winfo_height())

    def _checkIfMouseLeft(self, event: tk.Event = None) -> None:
        """Check if mouse left the menu area and hide if necessary.
        
        Args:
            event: Mouse event
        """
        # If this instance is in the process of or has been destroyed,
        # silently ignore any late events bound on the toplevel.
        if getattr(self, "_is_destroyed", False):
            return

        try:
            if not self.winfo_viewable():
                return

            if not self._get_coordinates(event.x_root, event.y_root):
                if isinstance(self.menu_seed_object, _CDMSubmenuButton):
                    parent_menu = self.menu_seed_object.parent_menu
                    if not parent_menu._get_coordinates(event.x_root, event.y_root):
                        if self._should_hide_menu():
                            self._hideAllMenus()
                else:
                    if self._should_hide_menu():
                        self._hideAllMenus()
        except tk.TclError:
            # Widget may already be destroyed; ignore spurious callbacks
            return
    
    def _should_hide_menu(self) -> bool:
        """Check if menu should be hidden based on submenu positions.
        
        Returns:
            True if menu should be hidden
        """
        submenus = self._get_submenus()
        return (not submenus or 
                all(not submenu._get_coordinates(*submenu.winfo_pointerxy()) 
                    for submenu in submenus))

    def _left(self, parent):
        """Handle mouse leaving submenu area."""
        # Ignore if either menu is already being destroyed
        if getattr(self, "_is_destroyed", False) or getattr(parent, "_is_destroyed", False):
            return
        try:
            if parent.hovered:
                parent.hovered = False
                return

            submenus = parent._get_submenus()
            for submenu in submenus:
                submenu._hide()
        except tk.TclError:
            # One of the widgets is gone; ignore
            return

    def change_hover(self, parent):
        """Change hover state of parent menu."""
        parent.hovered = True

    def _show_submenu(self, parent, button) -> None:
        """Show submenu at appropriate position.
        
        This method checks if cursor is still over the triggering button
        before showing the submenu to prevent unwanted activations.
        
        Args:
            parent: Parent menu containing the button
            button: The button that triggers this submenu
        """
        # Ignore if either menu is already being destroyed
        if getattr(self, "_is_destroyed", False) or getattr(parent, "_is_destroyed", False):
            return

        try:
            # Don't show if already visible
            if self.winfo_viewable():
                return

            # Hide all other submenus first to prevent overlap
            submenus = parent._get_submenus()
            for submenu in submenus:
                submenu._hide()

            # Check if mouse is still over the triggering button
            x, y = self.winfo_pointerxy()  # Get global mouse coordinates
            widget = self.winfo_containing(x, y)  # Find widget under mouse

            # Verify mouse is over button's components (canvas, text, or image label)
            if (str(widget) != str(button._canvas) and 
                str(widget) != str(button._text_label) and 
                str(widget) != str(button._image_label)):
                return  # Mouse moved away, don't show submenu

            # All checks passed, show the submenu
            self._show()
        except tk.TclError:
            # Any of the involved widgets could be gone already; ignore
            return
    
    def _cleanup_submenu_timers(self):
        """Clean up all submenu timer references."""
        try:
            for option in self._options_list:
                if isinstance(option, _CDMSubmenuButton) and hasattr(option, 'submenu'):
                    submenu = option.submenu
                    # Cancel any pending timer regardless of which widget scheduled it
                    if hasattr(submenu, '_timer_id') and submenu._timer_id:
                        tid = submenu._timer_id
                        for scheduler in (self, submenu):
                            try:
                                scheduler.after_cancel(tid)
                            except Exception:
                                pass
                        submenu._timer_id = None
                    # Recurse into deep submenu chains
                    try:
                        if hasattr(submenu, '_cleanup_submenu_timers'):
                            submenu._cleanup_submenu_timers()
                    except Exception:
                        pass
        except Exception:
            pass

    def configure(self, **kwargs):
        """Configure the dropdown menu properties."""
        # Mapping of parameter names to their handlers
        param_handlers = {
            "hover_color": lambda v: setattr(self, 'hover_color', v),
            "font": lambda v: setattr(self, 'font', v),
            "text_color": lambda v: setattr(self, 'text_color', v),
            "bg_color": self._handle_bg_color,
            "fg_color": lambda v: setattr(self, 'fg_color', v),
            "border_color": self._handle_border_color,
            "border_width": self._handle_border_width,
            "corner_radius": self._handle_corner_radius,
            "height": lambda v: setattr(self, 'height', v),
            "width": lambda v: setattr(self, 'width', v),
            "separator_color": self._handle_separator_color,
            "padx": lambda v: setattr(self, 'padx', v),
            "pady": lambda v: setattr(self, 'pady', v),
            "max_visible_options": self._handle_max_visible_options,
            "enable_scrollbar": self._handle_enable_scrollbar,
            "scrollbar_width": self._handle_scrollbar_width
        }

        # Process each parameter
        for param, value in kwargs.items():
            if param in param_handlers:
                param_handlers[param](value)

        # Configure child widgets with remaining parameters
        remaining_kwargs = {k: v for k, v in kwargs.items() if k not in param_handlers}
        for widget in self.winfo_children():
            if isinstance(widget, (_CDMOptionButton, _CDMSubmenuButton)):
                widget.configure(**remaining_kwargs)

    def _handle_bg_color(self, value):
        """Handle bg_color configuration."""
        self.bg_color = value
        super().configure(fg_color=value)

    def _handle_border_color(self, value):
        """Handle border_color configuration."""
        self.border_color = value
        super().configure(border_color=value)

    def _handle_border_width(self, value):
        """Handle border_width configuration."""
        self.border_width = value
        super().configure(border_width=value)

    def _handle_corner_radius(self, value):
        """Handle corner_radius configuration."""
        self.corner_radius = value
        super().configure(corner_radius=value)

    def _handle_separator_color(self, value):
        """Handle separator color configuration."""
        self.separator_color = value
        for child in self.winfo_children():
            if isinstance(child, customtkinter.CTkFrame):
                child.configure(fg_color=value)

    def _handle_max_visible_options(self, value):
        """Handle max_visible_options configuration."""
        self.max_visible_options = value
        self._update_scrollbar_visibility()

    def _handle_enable_scrollbar(self, value):
        """Handle enable_scrollbar configuration."""
        self.enable_scrollbar = value
        self._update_scrollbar_visibility()

    def _handle_scrollbar_width(self, value):
        """Handle scrollbar_width configuration and re-layout if needed."""
        try:
            self.scrollbar_width = int(value)
        except Exception:
            self.scrollbar_width = value
        # If a scrollable frame is active, rebuild it to apply new width
        if getattr(self, "_scrollable_frame", None) is not None:
            self._destroy_scrollable_frame()
            self._create_scrollable_frame()

    def cget(self, param: str):
        """Get configuration parameter value."""
        param_mapping = {
            "hover_color": self.hover_color,
            "font": self.font,
            "text_color": self.text_color,
            "bg_color": self.bg_color,
            "border_color": self.border_color,
            "border_width": self.border_width,
            "corner_radius": self.corner_radius,
            "height": self.height,
            "width": self.width,
            "separator_color": self.separator_color,
            "padx": self.padx,
            "pady": self.pady,
            "max_visible_options": self.max_visible_options,
            "enable_scrollbar": self.enable_scrollbar,
            "scrollbar_width": self.scrollbar_width
        }

        if param in param_mapping:
            return param_mapping[param]
        else:
            return super().cget(param)

    def _should_use_scrollbar(self) -> bool:
        """Check if scrollbar should be enabled based on current options count."""
        return (self.enable_scrollbar and
                len(self._options_list) >= self.max_visible_options)

    def _update_scrollbar_visibility(self) -> None:
        """Update scrollbar visibility based on current options count."""
        if self._should_use_scrollbar() and self._scrollable_frame is None:
            self._create_scrollable_frame()
        elif not self._should_use_scrollbar() and self._scrollable_frame is not None:
            self._destroy_scrollable_frame()

    def _create_scrollable_frame(self) -> None:
        """Create a scrollable frame when menu options exceed the visible limit.
        
        This method dynamically creates a scrollable container when the number of menu
        options exceeds `max_visible_options`. It:
        - Calculates optimal frame dimensions based on option height and count
        - Preserves all existing options with their states (checkable, icons, etc.)
        - Recreates options within the scrollable container
        - Maintains submenu bindings and timer logic
        - Ensures proper scrollbar integration and space allocation
        
        The scrollable frame improves usability for large menus while maintaining
        all enhanced features like accelerators, icons, and submenu functionality.
        """
        if self._scrollable_frame is not None:
            return

        # Calculate the height for the scrollable area
        option_height = self.height + (2 * (DEFAULT_PADDING + (self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR)))
        max_height = option_height * self.max_visible_options

        # Calculate maximum required width for all options
        max_option_width = self.width  # Start with default width
        
        # Get font for text measurement
        try:
            import tkinter.font as tkFont
            font = tkFont.Font(font=self.font) if self.font else tkFont.Font()
            
            # Check width of all current options
            for option in self._options_list:
                try:
                    option_text = option.cget('text')
                    # Measure text width
                    text_width = font.measure(option_text)
                    # Add conservative padding for accelerator text, icons, checkmarks, etc.
                    total_width = text_width
                    max_option_width = max(max_option_width, total_width)
                except:
                    continue
                    
        except ImportError:
            # Fallback if tkinter.font is not available
            for option in self._options_list:
                try:
                    option_text = option.cget('text')
                    # Rough estimation: ~8 pixels per character
                    estimated_width = len(option_text) * 8 + 20
                    max_option_width = max(max_option_width, estimated_width)
                except:
                    continue

        # Calculate width accounting for scrollbar space
        # Reserve space equal to the configured scrollbar width (+ small padding)
        try:
            configured_sb_width = int(self.scrollbar_width)
        except Exception:
            configured_sb_width = SCROLLBAR_WIDTH
        extra_padding = max(SCROLLBAR_EXTRA_SPACE - SCROLLBAR_WIDTH, 0)
        scrollbar_space = max(configured_sb_width, 0) + extra_padding
        frame_width = max_option_width + scrollbar_space
        
        # Ensure minimum width but allow expansion for longer texts
        frame_width = max(frame_width, self.width + scrollbar_space)
        
        # Create scrollable frame
        self._scrollable_frame = customtkinter.CTkScrollableFrame(
            self,
            width=frame_width,
            height=max_height,
            fg_color=self.fg_color if self.fg_color else "transparent",
            corner_radius=0,
            border_color=self.border_color,
            border_width=self.border_width
        )

        # Try to apply scrollbar_width to the internal scrollbar if accessible
        try:
            possible_attrs = ("_scrollbar", "scrollbar", "_scrollbar_vertical", "_v_scrollbar")
            for name in possible_attrs:
                sb = getattr(self._scrollable_frame, name, None)
                if sb and hasattr(sb, "configure"):
                    sb.configure(width=configured_sb_width)
                    break
        except Exception:
            pass

        self._scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Store current options data before recreating them
        options_data = []
        for option in self._options_list:
            try:
                if isinstance(option, _CDMSubmenuButton):
                    options_data.append({
                        'type': 'submenu',
                        'text': option.cget('option'),
                        'submenu': option.submenu
                    })
                else:
                    original_text = option.cget('option')
                    options_data.append({
                        'type': 'option',
                        'text': original_text,
                        'command': option.cget('command'),
                        'accelerator': getattr(option, 'accelerator', None),
                        'icon': getattr(option, 'icon', None),
                        'checkable': getattr(option, 'checkable', False),
                        'checked': getattr(option, 'checked', False),
                        'enabled': getattr(option, 'enabled', True)
                    })
            except Exception as e:
                # Issue warning but continue processing other options
                warnings.warn(f"Error processing option during scrollable frame creation: {e}")
                continue
        
        # Clear existing options
        for option in self._options_list:
            try:
                option.destroy()
            except:
                pass
        self._options_list.clear()

        # Update the options container
        self._options_container = self._scrollable_frame

        # Calculate button width (excluding scrollbar space)
        button_width = frame_width - scrollbar_space

        # Recreate options in the scrollable frame
        for data in options_data:
            if data['type'] == 'submenu':
                # Recreate submenu button
                submenuButtonSeed = _CDMSubmenuButton(
                    self._options_container,
                    text=data['text'],
                    anchor="w",
                    text_color=self.text_color,
                    width=button_width,
                    height=self.height
                )
                submenuButtonSeed.setParentMenu(self)

                # Update the submenu's menu_seed_object
                submenu = data['submenu']
                submenu.menu_seed_object = submenuButtonSeed

                submenuButtonSeed.setSubmenu(submenu)
                submenuButtonSeed.configure(command=submenu.toggleShow)
                submenu.is_submenu = True
                self._options_list.append(submenuButtonSeed)
                self._configureButton(submenuButtonSeed)

                submenuButtonSeed.configure(cursor=self.cursor)
                submenuButtonSeed.pack(
                    side="top",
                    fill="both",
                    expand=True,
                    padx=DEFAULT_PADDING + (self.corner_radius / DEFAULT_CORNER_RADIUS_FACTOR),
                    pady=DEFAULT_PADDING + (self.corner_radius / DEFAULT_CORNER_RADIUS_FACTOR)
                )

                self._setup_submenu_timers(submenuButtonSeed, submenu)
            else:
                # Recreate option button
                option_text = data['text']  
                command = data['command']
                accelerator = data['accelerator']
                icon = data['icon']
                checkable = data['checkable']
                checked = data['checked']
                enabled = data['enabled']

                optionButton = _CDMOptionButton(
                    self._options_container,
                    width=button_width,
                    height=self.height,
                    text=option_text,
                    anchor="w",
                    text_color=self.text_color,
                    command=partial(self.selectOption, command),
                    accelerator=accelerator,
                    icon=icon,
                    checkable=checkable,
                    checked=checked,
                    enabled=enabled
                )
                optionButton.configure(cursor=self.cursor)
                optionButton.setParentMenu(self)
                self._options_list.append(optionButton)
                self._configureButton(optionButton)

                # Set up checkable command wrapper if needed
                if checkable and command and command != self._dummy_command:
                    self._setup_checkable_command(optionButton, command)

                # Add submenu binding if this is a submenu
                if self.is_submenu:
                    optionButton.bind("<Enter>", lambda e, submenu=self: submenu.change_hover(self), add="+")
                    self._setup_submenu_timers(optionButton)

                optionButton.pack(
                    side="top",
                    fill="both",
                    expand=True,
                    padx=DEFAULT_PADDING+(self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR),
                    pady=DEFAULT_PADDING+(self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR)
                )

    def _destroy_scrollable_frame(self) -> None:
        """Remove scrollable frame and move options back to main frame."""
        if self._scrollable_frame is None:
            return

        # Store current options data before recreating them
        options_data = []
        for option in self._options_list:
            try:
                if isinstance(option, _CDMSubmenuButton):
                    options_data.append({
                        'type': 'submenu',
                        'text': option.cget('option'),
                        'submenu': option.submenu
                    })
                else:
                    original_text = option.cget('option')
                    options_data.append({
                        'type': 'option',
                        'text': original_text,
                        'command': option.cget('command'),
                        'accelerator': getattr(option, 'accelerator', None),
                        'icon': getattr(option, 'icon', None),
                        'checkable': getattr(option, 'checkable', False),
                        'checked': getattr(option, 'checked', False),
                        'enabled': getattr(option, 'enabled', True)
                    })
            except Exception as e:
                warnings.warn(f"Error processing option during scrollable frame destruction: {e}")
                continue
        
        # Clear existing options with proper error handling
        for option in self._options_list[:]:
            try:
                if hasattr(option, 'destroy'):
                    option.destroy()
            except Exception as e:
                warnings.warn(f"Error destroying option widget: {e}")
                continue
        self._options_list.clear()

        # Destroy scrollable frame with error handling
        try:
            if self._scrollable_frame and hasattr(self._scrollable_frame, 'destroy'):
                self._scrollable_frame.destroy()
        except Exception as e:
            warnings.warn(f"Error destroying scrollable frame: {e}")
        finally:
            self._scrollable_frame = None
            self._options_container = self

        # Recreate options in the main frame
        for data in options_data:
            if data['type'] == 'submenu':
                # Recreate submenu button
                submenuButtonSeed = _CDMSubmenuButton(
                    self._options_container,
                    text=data['text'],
                    anchor="w",
                    text_color=self.text_color,
                    width=self.width,
                    height=self.height
                )
                submenuButtonSeed.setParentMenu(self)

                # Update the submenu's menu_seed_object
                submenu = data['submenu']
                submenu.menu_seed_object = submenuButtonSeed

                submenuButtonSeed.setSubmenu(submenu)
                submenuButtonSeed.configure(command=submenu.toggleShow)
                submenu.is_submenu = True
                self._options_list.append(submenuButtonSeed)
                self._configureButton(submenuButtonSeed)

                submenuButtonSeed.configure(cursor=self.cursor)
                submenuButtonSeed.pack(
                    side="top",
                    fill="both",
                    expand=True,
                    padx=DEFAULT_PADDING + (self.corner_radius / DEFAULT_CORNER_RADIUS_FACTOR),
                    pady=DEFAULT_PADDING + (self.corner_radius / DEFAULT_CORNER_RADIUS_FACTOR)
                )

                self._setup_submenu_timers(submenuButtonSeed, submenu)
            else:
                # Recreate option button
                option_text = data['text']  
                command = data['command']
                accelerator = data['accelerator']
                icon = data['icon']
                checkable = data['checkable']
                checked = data['checked']
                enabled = data['enabled']

                optionButton = _CDMOptionButton(
                    self._options_container,
                    width=self.width,
                    height=self.height,
                    text=option_text,
                    anchor="w",
                    text_color=self.text_color,
                    command=partial(self.selectOption, command) if command else None,
                    accelerator=accelerator,
                    icon=icon,
                    checkable=checkable,
                    checked=checked,
                    enabled=enabled
                )
                optionButton.configure(cursor=self.cursor)
                optionButton.setParentMenu(self)
                self._options_list.append(optionButton)
                self._configureButton(optionButton)

                # Set up checkable command wrapper if needed
                if checkable and command and command != self._dummy_command:
                    self._setup_checkable_command(optionButton, command)

                # Add submenu binding if this is a submenu
                if self.is_submenu:
                    optionButton.bind("<Enter>", lambda e, submenu=self: submenu.change_hover(self), add="+")
                    self._setup_submenu_timers(optionButton)

                optionButton.pack(
                    side="top",
                    fill="both",
                    expand=True,
                    padx=DEFAULT_PADDING+(self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR),
                    pady=DEFAULT_PADDING+(self.corner_radius/DEFAULT_CORNER_RADIUS_FACTOR)
                )

    def destroy(self):
        """Clean up menu resources and destroy the widget safely.
        
        This method performs comprehensive cleanup to prevent "can't delete Tcl command"
        errors and memory leaks by:
        - Cancelling all pending timer callbacks
        - Cleaning up submenu timer references  
        - Destroying scrollable frame components
        - Clearing widget references and option lists
        - Calling parent destroy method safely
        
        This override is essential for proper resource management in complex menu
        hierarchies with timers and dynamic components.
        """
        try:
            # Mark as destroyed early so late event callbacks no-op safely
            try:
                self._is_destroyed = True
            except Exception:
                pass

            # Cancel any pending timers
            if hasattr(self, '_timer_id') and self._timer_id:
                try:
                    self.after_cancel(self._timer_id)
                except:
                    pass
                self._timer_id = None

            # Clean up submenu timers
            self._cleanup_submenu_timers()

            # Clean up scrollable frame first if it exists
            if hasattr(self, '_scrollable_frame') and self._scrollable_frame:
                try:
                    self._scrollable_frame.destroy()
                except:
                    pass
                self._scrollable_frame = None

            # Clear references
            if hasattr(self, '_options_list'):
                self._options_list.clear()
            if hasattr(self, 'menu_seed_object'):
                self.menu_seed_object = None

        except Exception as e:
            warnings.warn(f"Error during cleanup: {e}")
        finally:
            # Call parent destroy
            try:
                super().destroy()
            except:
                pass

    def _setup_submenu_timers(self, button, submenu=None):
        """Set up delayed show/hide timer bindings for submenu interactions.
        
        This method creates timer-based event handlers that prevent submenu flickering
        and auto-hide issues when the user hovers over menu items. Timers are used to
        delay both showing and hiding of submenus, providing smooth user experience.
        
        Args:
            button: The button widget to bind timer events to
            submenu: Optional submenu instance. If None, sets up timers for regular
                    option buttons in a submenu context. If provided, sets up timers
                    for submenu buttons that trigger the specified submenu.
                    
        Note:
            This method fixes the submenu auto-hide bug by properly managing timer
            cancellation and preventing unwanted menu collapses during hover events.
            Special thanks to: iLollek | https://github.com/iLollek
        """

        if submenu is None and self.is_submenu:
            submenu = self
            if not hasattr(submenu, '_timer_id'):
                submenu._timer_id = None
        else:
            submenu._timer_id = None

        def show_submenu_delayed(e):
            """Show submenu after delay, canceling any pending hide timer."""
            if submenu._timer_id:
                self.after_cancel(submenu._timer_id)
            submenu._timer_id = self.after(DEFAULT_SUBMENU_DELAY,
                                           lambda: submenu._show_submenu(self, button))

        def hide_submenu_delayed(e):
            """Hide submenu after delay, canceling any pending show timer."""
            if submenu._timer_id:
                self.after_cancel(submenu._timer_id)
            submenu._timer_id = self.after(DEFAULT_SUBMENU_DELAY, lambda: submenu._left(self))

        button.bind("<Enter>", lambda e: show_submenu_delayed(e), add="+")
        button.bind("<Leave>", lambda e: hide_submenu_delayed(e), add="+")

class ContextMenu(CustomDropdownMenu):
    """A right-click context menu with full dropdown menu functionality.
    
    This class extends CustomDropdownMenu to provide context menu behavior that appears
    when the user right-clicks on a widget. It supports all enhanced features including:
    - Keyboard accelerators and shortcuts
    - Icons and checkable menu items
    - Submenus and hierarchical organization  
    - Scrollable menus for large option lists
    - Automatic positioning at cursor location
    
    The context menu automatically binds to the target widget and its children,
    providing consistent right-click behavior throughout the widget hierarchy.
    
    Example:
        context_menu = ContextMenu(my_widget)
        context_menu.add_option("Copy", copy_function, accelerator="Ctrl+C")
        context_menu.add_option("Paste", paste_function, accelerator="Ctrl+V")
        context_menu.add_separator()
        context_menu.add_option("Delete", delete_function, accelerator="Delete")
    """
    def __init__(self, widget: customtkinter.CTkBaseClass, **kwargs):
        """Initialize a context menu.

        Args:
            widget: The widget to attach the context menu to
            **kwargs: Additional arguments passed to CustomDropdownMenu
        """
        # Create a dummy button to serve as the menu seed
        self._dummy_button = customtkinter.CTkButton(widget.master, text="", width=0, height=0)
        self._dummy_button.place_forget()  # Hide the dummy button

        super().__init__(widget=self._dummy_button, **kwargs)

        self.target_widget = widget
        self._bind_context_menu()

    def _bind_context_menu(self):
        """Bind right-click event to show context menu."""
        self.target_widget.bind("<Button-3>", self._show_context_menu, add="+")
        # Also bind to child widgets if it's a container
        try:
            for child in self.target_widget.winfo_children():
                child.bind("<Button-3>", self._show_context_menu, add="+")
        except:
            pass

    def _show_context_menu(self, event):
        """Show the context menu at the current cursor position.
        
        This method handles the right-click event by positioning the context menu
        at the cursor location with a small offset for better visibility. It:
        - Calculates cursor position relative to the target widget
        - Applies a small offset to prevent menu from appearing under cursor
        - Stores coordinates for potential repositioning
        - Shows the menu with proper focus and layering
        
        Args:
            event: The mouse event containing cursor coordinates
            
        Note:
            Includes error handling to gracefully handle coordinate calculation
            issues or widget state problems during menu display.
        """
        try:
            # Get cursor position in screen coordinates
            cursor_x = event.x_root - self.target_widget.winfo_rootx() + 30
            cursor_y = event.y_root - self.target_widget.winfo_rooty() + 30

            # Store the cursor position
            self._context_x = cursor_x
            self._context_y = cursor_y

            # Show the menu at cursor position using screen coordinates
            # Place it relative to the screen, not a parent widget
            self.place(x=cursor_x, y=cursor_y)
            self.lift()
            self.focus()

        except Exception as e:
            warnings.warn(f"Failed to show context menu: {e}")

    def _show(self, *args, **kwargs):
        """Override _show to use stored cursor position."""
        if hasattr(self, '_context_x') and hasattr(self, '_context_y'):
            self.place(x=self._context_x, y=self._context_y)
        else:
            super()._show(*args, **kwargs)
        self.lift()
        self.focus()
