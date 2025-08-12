"""
Customtkinter Menu Bar

A menu bar widget for customtkinter applications with support for
cascading dropdown menus and theme integration.

Author: Akash Bora (Akascape) | https://github.com/Akascape
Modified by: xzyqox (KiTant) | https://github.com/KiTant
"""

import customtkinter
from typing import Optional, Callable, Union, List


class CTkMenuBar(customtkinter.CTkFrame):
    """Menu bar widget with cascading dropdown support.
    
    Creates a horizontal menu bar that can contain buttons with dropdown menus.
    Automatically adapts to parent widget styling and supports theming.
    """
        
    def __init__(
        self,
        master,
        bg_color: Union[str, tuple[str, str]] = ["white", "black"],
        height: int = 25,
        width: int = 10,
        padx: int = 5,
        pady: int = 2,
        **kwargs):
        """
        Initialize menu bar.
        
        Args:
            master: Parent widget
            bg_color: Background color (theme tuple or string)
            height: Menu bar height in pixels
            width: Menu button width in pixels
            padx: Horizontal spacing between buttons
            pady: Vertical padding
            **kwargs: Additional CTkFrame arguments
        """

        if master.winfo_name().startswith("!ctkframe"):
            bg_corners = ["", "", bg_color, bg_color]
            corner = master.cget("corner_radius")
        else:
            bg_corners = ["", "", "", ""]
            corner = 0
            
        super().__init__(master, fg_color=bg_color, corner_radius=corner, height=height, background_corner_colors=bg_corners, **kwargs)
        self.height = height
        self.width = width
        self.after(10)
        self.num = 0
        self.menu: List = []
        self.padx = padx
        self.pady = pady
        self.bg_color = bg_color
        self._is_visible = True  # Track visibility state

        super().pack(anchor="n", fill="x")

    def add_cascade(self, text: Optional[str] = None, postcommand: Optional[Callable] = None, **kwargs) -> customtkinter.CTkButton:
        """
        Add menu button to the bar.
        
        Args:
            text: Button text (auto-generated if None)
            postcommand: Function to call on click
            **kwargs: Button styling options
            
        Returns:
            CTkButton: The created menu button
        """
        if not "fg_color" in kwargs:
            fg_color = "transparent"
        else:
            fg_color = kwargs.pop("fg_color")
            
        if not "text_color" in kwargs:
            text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"]
        else:
            text_color = kwargs.pop("text_color")
            
        if not "anchor" in kwargs:
            anchor = "w"
        else:
            anchor = kwargs.pop("anchor")

        if text is None:
            text = f"Menu {self.num+1}"
            
        self.menu_button = customtkinter.CTkButton(
            self, 
            text=text, 
            fg_color=fg_color,
            text_color=text_color, 
            width=self.width,
            height=self.height, 
            anchor=anchor, 
            **kwargs)
        self.menu_button.grid(row=0, column=self.num, padx=(self.padx, 0), pady=self.pady)
        
        if postcommand and callable(postcommand):
            self.menu_button.bind("<Button-1>", lambda event: postcommand(), add="+")
            
        self.num += 1

        return self.menu_button
    
    def configure(self, **kwargs):
        """Configure menu bar properties.
        
        Args:
            **kwargs: Properties to configure (bg_color, height, width, padx, pady, etc.)
        """
        # Handle menu bar specific parameters
        if "bg_color" in kwargs:
            self.bg_color = kwargs.pop("bg_color")
            super().configure(fg_color=self.bg_color)
            
        if "height" in kwargs:
            self.height = kwargs.pop("height")
            super().configure(height=self.height)
            
        if "width" in kwargs:
            self.width = kwargs.pop("width")
            # Update existing buttons if any
            for child in self.winfo_children():
                if isinstance(child, customtkinter.CTkButton):
                    child.configure(width=self.width)
                    
        if "padx" in kwargs:
            self.padx = kwargs.pop("padx")
            # Re-grid existing buttons with new padding
            for i, child in enumerate(self.winfo_children()):
                if isinstance(child, customtkinter.CTkButton):
                    child.grid(row=0, column=i, padx=(self.padx, 0), pady=self.pady)
                    
        if "pady" in kwargs:
            self.pady = kwargs.pop("pady")
            # Re-grid existing buttons with new padding
            for i, child in enumerate(self.winfo_children()):
                if isinstance(child, customtkinter.CTkButton):
                    child.grid(row=0, column=i, padx=(self.padx, 0), pady=self.pady)
        
        # Pass remaining arguments to parent class
        if kwargs:
            super().configure(**kwargs)
            
    def cget(self, param: str):
        """Get configuration parameter value.
        
        Args:
            param: Parameter name
            
        Returns:
            Parameter value
        """
        if param == "bg_color":
            return self.bg_color
        elif param == "height":
            return self.height
        elif param == "width":
            return self.width
        elif param == "padx":
            return self.padx
        elif param == "pady":
            return self.pady
        else:
            return super().cget(param)

    def show(self):
        """Show the menu bar at the top of parent widget.
        
        Temporarily removes other widgets to place menu bar first,
        then restores them with their original layout managers.
        """
        if not self._is_visible:
            # Store information about other widgets using different geometry managers
            pack_widgets = []
            grid_widgets = []
            place_widgets = []
            
            for child in self.master.winfo_children():
                if child != self:
                    manager = child.winfo_manager()
                    if manager == 'pack':
                        pack_info = child.pack_info()
                        pack_widgets.append((child, pack_info))
                        child.pack_forget()
                    elif manager == 'grid':
                        grid_info = child.grid_info()
                        grid_widgets.append((child, grid_info))
                        child.grid_forget()
                    elif manager == 'place':
                        place_info = child.place_info()
                        place_widgets.append((child, place_info))
                        child.place_forget()
            
            # Pack the menu bar first (at the top)
            super().pack(side="top", anchor="n", fill="x")
            
            # Restore other widgets with their original geometry managers
            for widget, pack_info in pack_widgets:
                widget.pack(**pack_info)
            
            for widget, grid_info in grid_widgets:
                widget.grid(**grid_info)
            
            for widget, place_info in place_widgets:
                # Filter out problematic parameters for customtkinter place()
                filtered_place_info = {}
                for k, v in place_info.items():
                    if k not in ['width', 'height']:
                        # Convert string coordinates to numbers if needed
                        if k in ['x', 'y', 'relx', 'rely', 'relwidth', 'relheight']:
                            try:
                                if isinstance(v, str):
                                    v = float(v) if '.' in v else int(v)
                            except (ValueError, TypeError):
                                continue  # Skip invalid values
                        filtered_place_info[k] = v
                
                if filtered_place_info:  # Only place if we have valid parameters
                    widget.place(**filtered_place_info)
            
            self._is_visible = True

    def hide(self):
        """Hide the menu bar."""
        if self._is_visible:
            super().pack_forget()
            self._is_visible = False

    def toggle(self):
        """Toggle menu bar visibility (show/hide)."""
        if self._is_visible:
            self.hide()
        else:
            self.show()
