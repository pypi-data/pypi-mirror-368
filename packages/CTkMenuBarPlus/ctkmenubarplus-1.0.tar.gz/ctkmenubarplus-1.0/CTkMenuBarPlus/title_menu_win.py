"""
Menu Bar in Title Bar of customtkinter window

A Windows-only title menu system that integrates with the window title bar.
Provides native-looking menu buttons with dropdown support.

Author: Akash Bora (Akascape) | https://github.com/Akascape
Modified by: xzyqox (KiTant) | https://github.com/KiTant
"""

import customtkinter
import tkinter as tk
import sys
from typing import Optional, Union

# Platform constants
SUPPORTED_PLATFORMS = ["win32", "win"]
DEFAULT_LIGHT_COLOR = 0xFFFFFF
DEFAULT_DARK_COLOR = 0x303030


class PlatformError(Exception):
    """Exception raised when the platform is not supported."""
    pass


class CTkTitleMenu(customtkinter.CTkToplevel):
    """Title menu widget that integrates with Windows title bar.
    
    Creates menu buttons that appear in the window title area.
    Supports themes, positioning, and dropdown menus.
    Windows only - uses transparent overlay technique.
    """
        
    def __init__(
        self,
        master,
        title_bar_color: Union[str, int] = "default",
        padx: int = 10,
        width: int = 10,
        x_offset: Optional[int] = None,
        y_offset: Optional[int] = None):
        """
        Initialize title menu.
        
        Args:
            master: Parent window (CTk or CTkToplevel)
            title_bar_color: Color for title bar ("default" for auto theme)
            padx: Spacing between menu buttons
            width: Width of menu buttons  
            x_offset: Horizontal position offset
            y_offset: Vertical position offset
            
        Raises:
            PlatformError: If not on Windows
        """
        
        super().__init__()

        # Platform check with better error handling
        if not self._is_windows_platform():
            raise PlatformError(
                "This title menu works only on Windows platform, not supported on your system! "
                "Try the CTkMenuBar instead..."
            )
        
        self.after(10)
        self.master = master
        self._validate_master()
        
        self.master.minsize(200, 100)
        self.after(100, lambda: self.overrideredirect(True))
        
        # Handle title bar color configuration
        title_bar_color = self._configure_title_bar_color(title_bar_color)
                
        self.transparent_color = self._apply_appearance_mode(self._fg_color)
        self.attributes("-transparentcolor", self.transparent_color)
        self.resizable(True, True)
        self.transient(self.master)
        self.menu = []

        self.config(background=self.transparent_color)
        self.caption_color = title_bar_color
        self.change_header_color(self.caption_color)
        self.x_offset = 40 if x_offset is None else x_offset
        self.y_offset = 6 if y_offset is None else y_offset
        self.width = width
        if x_offset is None:
            title = self.master.title()
            if len(title)>=1:
                for i in title:
                    if i.islower():
                        self.x_offset += 9
                    else:
                        self.x_offset += 7
            
        self.padding = padx
  
        self.master.bind("<Configure>", lambda _: self.change_dimension())
        self.master.bind("<Destroy>", lambda _: super().destroy() if not self.master.winfo_viewable() else None)
        self.num = 0
        self._is_visible = True  # Track visibility state
        
        self.master.bind("<Map>", lambda e: self.withdraw)

    def _set_appearance_mode(self, mode_string):
        if customtkinter.get_appearance_mode()=="Light":
            self.caption_color = DEFAULT_LIGHT_COLOR # RGB order: 0xrrggbb             
        else:
            self.caption_color = DEFAULT_DARK_COLOR # RGB order: 0xrrggbb

        self.change_header_color(self.caption_color)
        
    def add_cascade(self, text=None, postcommand=None, **kwargs):
        """Add menu button to title bar.
        
        Args:
            text: Button text (auto-generated if None)
            postcommand: Function to call on click
            **kwargs: Button styling options
            
        Returns:
            CTkButton: The created menu button
        """
    
        if not "fg_color" in kwargs:
            fg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        else:
            fg_color = kwargs.pop("fg_color")
        if not "text_color" in kwargs:
            text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"]
        else:
            text_color = kwargs.pop("text_color")
            
        if text is None:
            text = f"Tab {self.num+1}"
    
        self.menu_button = customtkinter.CTkButton(self, text=text, fg_color=fg_color,
                                                   text_color=text_color, width=self.width, height=10, **kwargs)
        self.menu_button.grid(row=0, column=self.num, padx=(0, self.padding))
        self.num += 1

        if postcommand:
            self.menu_button.bind("<Button-1>", lambda event: postcommand(), add="+")
            
        return self.menu_button
    
    def change_dimension(self):
        """Update menu position and size to match parent window."""
        if not self._is_visible:
            return  # Don't show if manually hidden
            
        width = self.master.winfo_width()-130-self.x_offset
        if width<0:
            self.withdraw()
            return
        if self.master.state()=="iconic":
            self.withdraw()
            return
        height = self.master.winfo_height()
        x = self.master.winfo_x()+self.x_offset
        y = self.master.winfo_y()+self.y_offset
        if self.master.state()=="zoomed":
            y += 4
            x -= 7
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.deiconify()

    def destroy_window(self):
        """
        Destroy the title menu window.
        """
        super().destroy()
 
    def change_header_color(self, caption_color):
        """Change Windows title bar color (Windows 11 only)."""
        try:
            from ctypes import windll, byref, sizeof, c_int
            # optional feature to change the header in windows 11
            HWND = windll.user32.GetParent(self.master.winfo_id())
            DWMWA_CAPTION_COLOR = 35
            windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, byref(c_int(caption_color)), sizeof(c_int))
        except: None

    def _is_windows_platform(self) -> bool:
        """Check if running on Windows."""
        return sys.platform in SUPPORTED_PLATFORMS

    def _validate_master(self) -> None:
        """Validate master window type."""
        master_type = self.master.winfo_name()
        
        if master_type=="tk":
            pass
        elif master_type.startswith("!ctktoplevel"):
            pass
        elif master_type.startswith("!toplevel"):
            pass
        elif isinstance(self.master, customtkinter.CTkToplevel):
            pass
        elif isinstance(self.master, tk.Toplevel):
            pass
        else:
            raise TypeError("Only root windows/toplevels can be passed as the master!")

    def _configure_title_bar_color(self, title_bar_color: Union[str, int]) -> int:
        """Configure the title bar color."""
        if title_bar_color=="default":
            if customtkinter.get_appearance_mode()=="Light":
                title_bar_color = DEFAULT_LIGHT_COLOR # RGB order: 0xrrggbb             
            else:
                title_bar_color = DEFAULT_DARK_COLOR # RGB order: 0xrrggbb
                
        return title_bar_color

    def show(self):
        """Show the title menu."""
        if not self._is_visible:
            self.deiconify()
            self._is_visible = True

    def hide(self):
        """Hide the title menu."""
        if self._is_visible:
            self.withdraw()
            self._is_visible = False

    def toggle(self):
        """Toggle the visibility of the title menu."""
        if self._is_visible:
            self.hide()
        else:
            self.show()
