import sys
import datetime
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional
from ..widget.calendar import Calendar, get_calendar_theme


class _DatePickerBase:
    """Base class for date picker widgets with common functionality."""
    
    def __init__(self, parent, date_format: str = "%Y-%m-%d", 
                 year: Optional[int] = None, month: Optional[int] = None,
                 show_week_numbers: bool = False, week_start: str = "Sunday",
                 day_colors: Optional[Dict[str, str]] = None,
                 holidays: Optional[Dict[str, str]] = None,
                 selectmode: str = "single", theme: str = "light", 
                 language: str = "en", today_color: str = "yellow", 
                 date_callback: Optional[callable] = None, **kwargs):
        
        # Get platform information once
        self.platform = sys.platform
        
        self.date_format = date_format
        self.selected_date = None
        self.popup = None
        self.date_callback = date_callback
        
        # Calendar will be created when popup is shown
        self.calendar = None
        self.calendar_config = {
            'year': year,
            'month': month,
            'months': 1,
            'show_week_numbers': show_week_numbers,
            'week_start': week_start,
            'day_colors': day_colors,
            'holidays': holidays,
            'selectmode': selectmode,
            'show_navigation': True,
            'theme': theme,
            'date_format': date_format
        }
        
        # Set today color if specified
        self.today_color = None
        if today_color != "yellow":
            self.set_today_color(today_color)
        
    def _on_date_selected(self, date):
        """Handle date selection from calendar."""
        if date:
            self.selected_date = date
            self._update_entry_text(date.strftime(self.date_format))
            self.hide_calendar()
            
            # Call the callback if provided
            if self.date_callback:
                self.date_callback(date)
            
            # Reset pressed state for DateEntry
            if hasattr(self, 'state'):
                self.state(['!pressed'])
                
    def _update_entry_text(self, text: str):
        """Update the entry text (to be implemented by subclasses)."""
        raise NotImplementedError
        
    def _on_popup_click(self, event):
        """Handle click events in the popup to detect clicks outside the calendar."""
        if isinstance(event.widget, str):
            self.hide_calendar()
            return "break"
            
        if not self._is_child_of_calendar(event.widget, self.calendar):
            self.hide_calendar()
        else:
            self.calendar.focus_set()
        return "break"
        
    def _bind_calendar_events(self, widget):
        """Bind events to all child widgets of the calendar."""
        try:
            widget.bind('<ButtonRelease-1>', lambda e: 'break')
            
            for child in widget.winfo_children():
                self._bind_calendar_events(child)
        except Exception as e:
            pass
            
    def _setup_click_outside_handling(self):
        """Setup click outside handling."""
        self.calendar.bind('<FocusOut>', self._on_focus_out)
        self.popup.bind('<Button-1>', self._on_popup_click)
        self.popup.bind('<ButtonRelease-1>', self._on_popup_click)
        self.winfo_toplevel().bind('<Button-1>', self._on_main_window_click)
            
    def _is_child_of_popup(self, widget):
        """Check if widget is a child of the popup window."""
        current = widget
        while current:
            if current == self.popup:
                return True
            current = current.master
        return False
        
    def _setup_focus(self):
        """Setup focus for the popup."""
        try:
            self.popup.lift()
            self.calendar.focus_set()
            self.popup.after(50, lambda: self.calendar.focus_set())
            self.popup.after(100, lambda: self.calendar.focus_force())
        except Exception as e:
            pass
                
    def _on_focus_out(self, event):
        """Handle focus out events."""
        focus_widget = self.focus_get()
        
        if focus_widget is not None:
            if focus_widget == self:
                # Don't hide calendar when focus is on the DateEntry itself
                return "break"
            else:
                self.hide_calendar()
        else:
            try:
                x, y = self.popup.winfo_pointerxy()
                xc = self.popup.winfo_rootx()
                yc = self.popup.winfo_rooty()
                w = self.popup.winfo_width()
                h = self.popup.winfo_height()
                
                if xc <= x <= xc + w and yc <= y <= yc + h:
                    self.calendar.focus_force()
                else:
                    self.hide_calendar()
            except Exception as e:
                self.hide_calendar()
                
        return "break"
        
    def _is_child_of_calendar(self, widget, calendar_widget):
        """Check if widget is a child of calendar widget."""
        if isinstance(widget, str):
            return False
            
        current = widget
        while current:
            if current == calendar_widget:
                return True
            current = current.master
        return False
        
    def _on_main_window_click(self, event):
        """Handle click events on the main window."""
        if isinstance(event.widget, str):
            return "break"
            
        if self.popup and self.popup.winfo_exists():
            popup_x = self.popup.winfo_rootx()
            popup_y = self.popup.winfo_rooty()
            popup_w = self.popup.winfo_width()
            popup_h = self.popup.winfo_height()
            
            root_x = self.winfo_toplevel().winfo_rootx() + event.x
            root_y = self.winfo_toplevel().winfo_rooty() + event.y
            
            if (root_x < popup_x or root_x > popup_x + popup_w or 
                root_y < popup_y or root_y > popup_y + popup_h):
                self.hide_calendar()
                
        return "break"
            
    def _on_calendar_month_selected(self, year, month):
        """Handle month selection in calendar."""
        self.hide_calendar()
        self.calendar_config['year'] = year
        self.calendar_config['month'] = month
        self.show_calendar()
        
    def _on_calendar_year_view_request(self):
        """Handle year view request from calendar."""
        self.show_year_view()

    def show_year_view(self):
        """Show year view calendar."""
        if hasattr(self, 'year_view_window') and self.year_view_window:
            return
            
        if self.popup:
            self.popup.withdraw()
            
        self.year_view_window = tk.Toplevel(self)
        self.year_view_window.withdraw()
        
        theme = self.calendar_config.get('theme', 'light')
        try:
            theme_colors = get_calendar_theme(theme)
        except ValueError:
            theme_colors = get_calendar_theme('light')
        
        self.year_view_window.overrideredirect(True)
        self.year_view_window.resizable(False, False)
        self.year_view_window.configure(bg=theme_colors['background'])
        self.year_view_window.transient(self.winfo_toplevel())
        
        year_view_config = self.calendar_config.copy()
        year_view_config['year_view_mode'] = True
        self.year_view_calendar = Calendar(self.year_view_window, **year_view_config, 
                                         date_callback=self._on_year_view_month_selected)
        
        # Position the year view using geometry from Calendar
        self.year_view_window.update_idletasks()
        year_view_geometry = self.year_view_calendar.get_popup_geometry(self)
        self.year_view_window.geometry(year_view_geometry)
        
        self.year_view_calendar.pack(fill='both', expand=True)
        
        self.year_view_window.deiconify()
        self.year_view_window.lift()
        self.year_view_window.focus_force()
        self.year_view_window.update()
        self.year_view_window.lift()
            
    def hide_year_view(self):
        """Hide year view calendar."""
        if hasattr(self, 'year_view_window') and self.year_view_window:
            self.year_view_window.destroy()
            self.year_view_window = None
            self.year_view_calendar = None
            
    def _on_parent_configure(self, event):
        """Handle parent window configuration changes."""
        year_view_active = hasattr(self, 'year_view_window') and self.year_view_window and self.year_view_window.winfo_exists()
        
        if self.popup and self.popup.winfo_exists() and not year_view_active:
            # Recalculate and set geometry
            popup_geometry = self.calendar.get_popup_geometry(self)
            self.popup.geometry(popup_geometry)
            
        if year_view_active and hasattr(self, 'year_view_calendar'):
            # Recalculate and set geometry for year view
            year_view_geometry = self.year_view_calendar.get_popup_geometry(self)
            self.year_view_window.geometry(year_view_geometry)
            
    def _bind_parent_movement_events(self):
        """Bind events to monitor parent window movement."""
        if self.popup or (hasattr(self, 'year_view_window') and self.year_view_window):
            main_window = self.winfo_toplevel()
            main_window.bind('<Configure>', self._on_parent_configure)
            self._parent_configure_binding = main_window.bind('<Configure>', self._on_parent_configure)
            
    def _unbind_parent_movement_events(self):
        """Unbind parent window movement events."""
        if hasattr(self, '_parent_configure_binding'):
            main_window = self.winfo_toplevel()
            try:
                main_window.unbind('<Configure>', self._parent_configure_binding)
            except:
                pass
            delattr(self, '_parent_configure_binding')
            
    def _on_year_view_month_selected(self, year, month):
        """Handle month selection in year view."""
        self.hide_year_view()
        self.calendar_config['year'] = year
        self.calendar_config['month'] = month
        self.show_calendar()
            
    def show_calendar(self):
        """Show the popup calendar."""
        if self.popup:
            return
            
        self.popup = tk.Toplevel(self)
        self.popup.withdraw()
        self.popup.overrideredirect(True)
        self.popup.resizable(False, False)
        
        if hasattr(self, 'calendar_config') and 'theme' in self.calendar_config:
            theme = self.calendar_config['theme']
            try:
                theme_colors = get_calendar_theme(theme)
                self.popup.configure(bg=theme_colors['background'])
            except ValueError:
                theme_colors = get_calendar_theme('light')
                self.popup.configure(bg=theme_colors['background'])
        
        self.popup.transient(self.winfo_toplevel())
        self.popup.after(100, self._setup_focus)
        
        self.calendar = Calendar(self.popup, **self.calendar_config, 
                               date_callback=self._on_calendar_month_selected, 
                               year_view_callback=self._on_calendar_year_view_request)
        self.calendar.bind_date_selected(self._on_date_selected)
        
        self._bind_calendar_events(self.calendar)
        
        if self.today_color:
            self.calendar.set_today_color(self.today_color)
        
        self.calendar.pack(expand=True, fill='both', padx=2, pady=2)
        
        # Position the popup using geometry from Calendar
        self.popup.update_idletasks()
        popup_geometry = self.calendar.get_popup_geometry(self)
        self.popup.geometry(popup_geometry)
        
        self.popup.deiconify()
        self.popup.lift()
        
        self.popup.bind('<Escape>', lambda e: self.hide_calendar())
        self._setup_click_outside_handling()
        self._bind_parent_movement_events()
        self.calendar.focus_set()
        
    def hide_calendar(self):
        """Hide the popup calendar."""
        if self.popup:
            self._unbind_parent_movement_events()
            self.popup.destroy()
            self.popup = None
            self.calendar = None
            
        # Reset pressed state for DateEntry
        if hasattr(self, 'state'):
            self.state(['!pressed'])
            
    def get_date(self) -> Optional[datetime.date]:
        """Get the selected date."""
        return self.calendar.get_selected_date() if self.calendar else self.selected_date
        
    def set_selected_date(self, date: datetime.date):
        """Set the selected date."""
        self.selected_date = date
        if self.calendar:
            self.calendar.set_selected_date(date)
        self._update_entry_text(date.strftime(self.date_format))
        
    def get_date_string(self) -> str:
        """Get the selected date as a string."""
        selected_date = self.get_date()
        return selected_date.strftime(self.date_format) if selected_date else ""
        
    def _delegate_to_calendar(self, method_name, *args, **kwargs):
        """Delegate method calls to calendar if it exists."""
        if self.calendar and hasattr(self.calendar, method_name):
            getattr(self.calendar, method_name)(*args, **kwargs)
    
    def _update_config_and_delegate(self, config_key, value, method_name):
        """Update config and delegate to calendar."""
        self.calendar_config[config_key] = value
        self._delegate_to_calendar(method_name, value)
        
    def refresh_language(self):
        """Refresh the calendar language."""
        self._delegate_to_calendar('refresh_language')
            
    def set_today_color(self, color: str):
        """Set the today color."""
        self.today_color = color
        self._delegate_to_calendar('set_today_color', color)
            
    def set_theme(self, theme: str):
        """Set the calendar theme."""
        self._update_config_and_delegate('theme', theme, 'set_theme')
            
    def set_day_colors(self, day_colors: Dict[str, str]):
        """Set day of week colors dictionary."""
        self._update_config_and_delegate('day_colors', day_colors, 'set_day_colors')
            
    def set_week_start(self, week_start: str):
        """Set the week start day."""
        self._update_config_and_delegate('week_start', week_start, 'set_week_start')
        
    def set_show_week_numbers(self, show: bool):
        """Set whether to show week numbers."""
        self._update_config_and_delegate('show_week_numbers', show, 'set_show_week_numbers')
        
    def set_popup_size(self, width: Optional[int] = None, height: Optional[int] = None):
        """Set the popup size for both calendar and year view."""
        self._delegate_to_calendar('set_popup_size', width, height)


class DateFrame(tk.Frame, _DatePickerBase):
    """A DateFrame widget that shows a popup calendar with custom button."""
    
    def __init__(self, parent, date_format: str = "%Y-%m-%d", 
                 year: Optional[int] = None, month: Optional[int] = None,
                 show_week_numbers: bool = False, week_start: str = "Sunday",
                 day_colors: Optional[Dict[str, str]] = None,
                 holidays: Optional[Dict[str, str]] = None,
                 selectmode: str = "single", theme: str = "light", 
                 language: str = "en", today_color: str = "yellow", 
                 date_callback: Optional[callable] = None, button_text: str = "📅", **kwargs):
        tk.Frame.__init__(self, parent)
        _DatePickerBase.__init__(self, parent, date_format, year, month, show_week_numbers,
                                week_start, day_colors, holidays, selectmode, theme, 
                                language, today_color, date_callback, **kwargs)
        
        # Create entry and button
        self.entry = tk.Entry(self, state='readonly', width=15)
        self.entry.pack(side='left', fill='x', expand=True)
        
        self.button = tk.Button(self, text=button_text, command=self.show_calendar)
        self.button.pack(side='right')
        
    def _update_entry_text(self, text: str):
        """Update the entry text."""
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.config(state='readonly')
        
    def set_button_text(self, text: str):
        """Set the button text."""
        self.button.config(text=text)


class DateEntry(ttk.Entry, _DatePickerBase):
    """A DateEntry widget that looks like a Combobox with drop-down calendar."""
    
    def __init__(self, parent, date_format: str = "%Y-%m-%d", 
                 year: Optional[int] = None, month: Optional[int] = None,
                 show_week_numbers: bool = False, week_start: str = "Sunday",
                 day_colors: Optional[Dict[str, str]] = None,
                 holidays: Optional[Dict[str, str]] = None,
                 selectmode: str = "single", theme: str = "light", 
                 language: str = "en", today_color: str = "yellow", 
                 date_callback: Optional[callable] = None, button_text: str = None, **kwargs):
        
        # Remove button_text from kwargs as it's not supported for DateEntry
        if 'button_text' in kwargs:
            del kwargs['button_text']
        
        # Setup style to look like a combobox
        self.style = ttk.Style(parent)
        self._setup_style()
        
        # Initialize ttk.Entry with combobox-like style
        ttk.Entry.__init__(self, parent, style='DateEntryCombobox', **kwargs)
        _DatePickerBase.__init__(self, parent, date_format, year, month, show_week_numbers,
                                week_start, day_colors, holidays, selectmode, theme, 
                                language, today_color, date_callback, **kwargs)
        
        # Set readonly state
        self.configure(state='readonly')
        
        # Bind events for combobox-like behavior
        self.bind('<ButtonPress-1>', self._on_b1_press)
        self.bind('<Key>', self._on_key)
        

        
        # Bind focus out event for calendar
        self.bind('<FocusOut>', self._on_focus_out_entry)
        
    def _setup_style(self):
        """Setup style to make DateEntry look like a Combobox."""
        self.style.layout('DateEntryCombobox', self.style.layout('TCombobox'))
        
        conf = self.style.configure('TCombobox')
        if conf:
            self.style.configure('DateEntryCombobox', **conf)
        
        maps = self.style.map('TCombobox')
        if maps:
            self.style.map('DateEntryCombobox', **maps)
            

                
    def _on_b1_press(self, event):
        """Handle button press events."""
        x, y = event.x, event.y
        width = self.winfo_width()
        right_area = x > width - 20
        
        # Check if click is in the right area (dropdown button area)
        if right_area:
            self.state(['pressed'])
            self.drop_down()
            return "break"  # Consume the event
            
    def drop_down(self):
        """Display or withdraw the drop-down calendar depending on its current state."""
        if self.popup and self.popup.winfo_ismapped():
            self.hide_calendar()
        else:
            self.show_calendar()
            
    def _on_focus_out_entry(self, event):
        """Handle focus out event for the entry."""
        # Only hide if focus is not on the calendar
        if self.popup and self.popup.winfo_ismapped():
            focused_widget = self.focus_get()
            if focused_widget != self and not self._is_child_of_calendar(focused_widget, self.calendar):
                self.hide_calendar()
            
    def _on_key(self, event):
        """Handle key events."""
        if event.keysym in ('Down', 'space'):
            self.show_calendar()
            
    def _update_entry_text(self, text: str):
        """Update the entry text."""
        self.configure(state='normal')
        self.delete(0, tk.END)
        self.insert(0, text)
        self.configure(state='readonly')