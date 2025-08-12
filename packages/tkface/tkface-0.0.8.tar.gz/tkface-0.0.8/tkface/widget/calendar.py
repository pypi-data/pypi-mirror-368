import tkinter as tk
import calendar
import datetime
import configparser
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from .. import lang

# Default popup dimensions
DEFAULT_POPUP_WIDTH = 235
DEFAULT_POPUP_HEIGHT = 175
WEEK_NUMBERS_WIDTH_OFFSET = 20


class Calendar(tk.Frame):
    """
    A customizable calendar widget for Tkinter.
    
    Features:
    - Multiple months display
    - Week numbers
    - Customizable day colors
    - Holiday highlighting
    - Language support via tkface.lang
    - Configurable week start (Sunday/Monday)
    - Year view mode (3x4 month grid)
    """
    
    def __init__(self, parent, year: Optional[int] = None, month: Optional[int] = None,
                 months: int = 1, show_week_numbers: bool = False,
                 week_start: str = "Sunday", day_colors: Optional[Dict[str, str]] = None,
                 holidays: Optional[Dict[str, str]] = None, 
                 grid_layout: Optional[Tuple[int, int]] = None,
                 show_month_headers: bool = True, 
                 selectmode: str = "single",
                 show_navigation: bool = True, theme: str = "light",
                 date_callback: Optional[callable] = None,
                 year_view_callback: Optional[callable] = None,
                 popup_width: Optional[int] = None,
                 popup_height: Optional[int] = None,
                 **kwargs):
        """
        Initialize the Calendar widget.
        
        Args:
            parent: Parent widget
            year: Year to display (defaults to current year)
            month: Month to display (defaults to current month)
            months: Number of months to display horizontally
            show_week_numbers: Whether to show week numbers
            week_start: Week start day ("Sunday" or "Monday")
            day_colors: Dictionary mapping day names to colors
            holidays: Dictionary mapping date strings (YYYY-MM-DD) to colors
            **kwargs: Additional arguments passed to tk.Frame
        """
        self.date_callback = date_callback
        self.year_view_callback = year_view_callback
        
        # Extract date_format from kwargs before passing to super().__init__
        self.date_format = kwargs.pop('date_format', '%Y-%m-%d')
        
        # Set year view mode if specified
        self.year_view_mode = kwargs.pop('year_view_mode', False)
        
        super().__init__(parent, **kwargs)
        
        # Set default values
        if year is None:
            year = datetime.date.today().year
        if month is None:
            month = datetime.date.today().month
            
        # Validate week_start
        if week_start not in ["Sunday", "Monday", "Saturday"]:
            raise ValueError("week_start must be 'Sunday', 'Monday', or 'Saturday'")
            
        # Validate theme and initialize theme colors
        try:
            self.theme_colors = get_calendar_theme(theme)
            self.theme = theme
        except ValueError as e:
            themes = get_calendar_themes()
            raise ValueError(f"theme must be one of {list(themes.keys())}")
            
        self.year = year
        self.month = month
        self.months = months
        self.show_week_numbers = show_week_numbers
        self.week_start = week_start
        self.day_colors = day_colors or {}
        self.holidays = holidays or {}
        self.show_month_headers = show_month_headers
        self.selectmode = selectmode
        self.show_navigation = show_navigation
        
        # Popup size settings
        self.popup_width = popup_width if popup_width is not None else DEFAULT_POPUP_WIDTH
        self.popup_height = popup_height if popup_height is not None else DEFAULT_POPUP_HEIGHT
        
        # Selection state
        self.selected_date = None
        self.selected_range = None
        self.selection_callback = None
        
        # Today color (can be overridden)
        self.today_color = None
        self.today_color_set = True  # Default to showing today color
        
        # Store original colors for hover effect restoration
        self.original_colors = {}
        
        # Grid layout settings
        if grid_layout is not None:
            self.grid_rows, self.grid_cols = grid_layout
        else:
            # Auto-calculate grid layout based on number of months
            if months <= 3:
                self.grid_rows, self.grid_cols = 1, months
            elif months <= 6:
                self.grid_rows, self.grid_cols = 2, 3
            elif months <= 12:
                self.grid_rows, self.grid_cols = 3, 4
            else:
                self.grid_rows, self.grid_cols = 4, 4
        
        # Calendar instance - will be reused for efficiency
        self.cal = calendar.Calendar()
        self._update_calendar_week_start()
            
        # Widget storage
        self.month_frames = []
        self.day_labels = []
        self.week_labels = []
        self.year_view_labels = []  # For year view mode
        
        # Create widgets
        if self.year_view_mode:
            # Create year view content
            self._create_year_view_content()
        else:
            # Create normal calendar widgets
            self._create_widgets()
            self._update_display()
        
    def _update_calendar_week_start(self):
        """Update calendar week start setting efficiently."""
        if self.week_start == "Monday":
            self.cal.setfirstweekday(calendar.MONDAY)
        elif self.week_start == "Saturday":
            self.cal.setfirstweekday(calendar.SATURDAY)
        else:  # Sunday
            self.cal.setfirstweekday(calendar.SUNDAY)
    
    def _get_week_start_offset(self, date: datetime.date) -> int:
        """Get the offset for week start calculation efficiently."""
        if self.week_start == "Monday":
            return date.weekday()
        elif self.week_start == "Saturday":
            return (date.weekday() + 2) % 7
        else:  # Sunday
            return (date.weekday() + 1) % 7
        
    def _create_widgets(self):
        """Create the calendar widget structure."""
        # Set main frame background color
        self.configure(bg=self.theme_colors['background'])
        
        # Initialize containers based on number of months
        is_single_month = self.months == 1
        
        if is_single_month:
            self.months_container = tk.Frame(self, relief='flat', bd=1, bg=self.theme_colors['background'])
            self.months_container.pack(fill='both', expand=True, padx=2, pady=2)
        else:
            # Create scrollable container for multiple months
            self.canvas = tk.Canvas(self, bg=self.theme_colors['background'])
            self.scrollbar = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollable_frame = tk.Frame(self.canvas, bg=self.theme_colors['background'])
            
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(xscrollcommand=self.scrollbar.set)
            
            # Pack scrollbar and canvas
            self.scrollbar.pack(side="bottom", fill="x")
            self.canvas.pack(side="top", fill="both", expand=True)
            
            # Configure grid weights for the scrollable frame
            for i in range(self.grid_cols):
                self.scrollable_frame.columnconfigure(i, weight=1)
            for i in range(self.grid_rows):
                self.scrollable_frame.rowconfigure(i, weight=1)
        
        # Initialize label lists
        self.year_labels = []
        self.month_headers = []
        
        # Create month frames in grid layout
        for i in range(self.months):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            if is_single_month:
                month_frame = tk.Frame(self.months_container, relief='flat', bd=1, bg=self.theme_colors['background'])
                month_frame.pack(fill='both', expand=True, padx=2, pady=2)
            else:
                month_frame = tk.Frame(self.scrollable_frame, relief='flat', bd=1, bg=self.theme_colors['background'])
                month_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
            
            self.month_frames.append(month_frame)
            
            # Month header with navigation
            if self.show_month_headers:
                header_frame = tk.Frame(month_frame, bg=self.theme_colors['month_header_bg'])
                header_frame.pack(fill='x', pady=(2, 0))
                
                # Navigation buttons (removed - using year/month navigation instead)
                
                # Year and month navigation
                nav_frame = tk.Frame(header_frame, bg=self.theme_colors['month_header_bg'])
                nav_frame.pack(expand=True, fill='x')
                
                # Center container for year and month navigation
                center_frame = tk.Frame(nav_frame, bg=self.theme_colors['month_header_bg'])
                center_frame.pack(expand=True)
                
                # Create navigation elements
                year_first = self._is_year_first_in_format()
                
                # Define navigation items in order based on date format
                nav_items = [
                    ('year', '<<', '>>', self._on_prev_year, self._on_next_year),
                    ('month', '<', '>', self._on_prev_month, self._on_next_month)
                ] if year_first else [
                    ('month', '<', '>', self._on_prev_month, self._on_next_month),
                    ('year', '<<', '>>', self._on_prev_year, self._on_next_year)
                ]
                
                # Create navigation widgets
                for item_type, prev_text, next_text, prev_cmd, next_cmd in nav_items:
                    # Previous button
                    prev_btn = tk.Label(center_frame, text=prev_text,
                                      font=self.theme_colors['navigation_font'],
                                      bg=self.theme_colors['navigation_bg'],
                                      fg=self.theme_colors['navigation_fg'],
                                      cursor='hand2')
                    prev_btn.pack(side='left', padx=(5, 0))
                    prev_btn.bind('<Button-1>', lambda e, m=i, cmd=prev_cmd: cmd(m))
                    prev_btn.bind('<Enter>', lambda e, btn=prev_btn: btn.config(bg=self.theme_colors['navigation_hover_bg'], fg=self.theme_colors['navigation_hover_fg']))
                    prev_btn.bind('<Leave>', lambda e, btn=prev_btn: btn.config(bg=self.theme_colors['navigation_bg'], fg=self.theme_colors['navigation_fg']))
                    
                    # Label
                    is_year = item_type == 'year'
                    label = tk.Label(center_frame, font=('TkDefaultFont', 9, 'bold'),
                                   relief='flat', bd=0,
                                   bg=self.theme_colors['month_header_bg'],
                                   fg=self.theme_colors['month_header_fg'],
                                   cursor='hand2' if not is_year else '')
                    
                    if not is_year:
                        # Ensure month header is clickable
                        label.bind('<Button-1>', lambda e, m=i: self._on_month_header_click(m))
                        label.bind('<Enter>', lambda e, lbl=label: lbl.config(bg=self.theme_colors['navigation_hover_bg'], fg=self.theme_colors['navigation_hover_fg']))
                        label.bind('<Leave>', lambda e, lbl=label: lbl.config(bg=self.theme_colors['month_header_bg'], fg=self.theme_colors['month_header_fg']))
                        self.month_headers.append(label)
                    else:
                        self.year_labels.append(label)
                    
                    label.pack(side='left', padx=2)
                    
                    # Next button
                    next_btn = tk.Label(center_frame, text=next_text,
                                      font=self.theme_colors['navigation_font'],
                                      bg=self.theme_colors['navigation_bg'],
                                      fg=self.theme_colors['navigation_fg'],
                                      cursor='hand2')
                    next_btn.pack(side='left', padx=(0, 10 if item_type == ('year' if year_first else 'month') else 5))
                    next_btn.bind('<Button-1>', lambda e, m=i, cmd=next_cmd: cmd(m))
                    next_btn.bind('<Enter>', lambda e, btn=next_btn: btn.config(bg=self.theme_colors['navigation_hover_bg'], fg=self.theme_colors['navigation_hover_fg']))
                    next_btn.bind('<Leave>', lambda e, btn=next_btn: btn.config(bg=self.theme_colors['navigation_bg'], fg=self.theme_colors['navigation_fg']))
                
                # Store references for updating (now handled in the loop above)
            
            # Calendar grid (including header)
            self._create_calendar_grid(month_frame, i)
        
    def _create_calendar_grid(self, month_frame, month_index):
        """Create the calendar grid for a specific month."""
        grid_frame = tk.Frame(month_frame, bg=self.theme_colors['background'])
        grid_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Configure grid weights
        if self.show_week_numbers:
            grid_frame.columnconfigure(0, weight=1)
            for i in range(7):
                grid_frame.columnconfigure(i + 1, weight=1)
        else:
            for i in range(7):
                grid_frame.columnconfigure(i, weight=1)
        
        # Configure row weights (header row + 6 week rows)
        grid_frame.rowconfigure(0, weight=0)  # Header row (no expansion)
        for week in range(6):  # Maximum 6 weeks
            grid_frame.rowconfigure(week + 1, weight=1)
        
        # Create day name headers (row 0)
        day_names = self._get_day_names(short=True)
        if self.show_week_numbers:
            # Empty header for week number column
            empty_header = tk.Label(grid_frame, text="", 
                                  font=('TkDefaultFont', 8), 
                                  width=2, height=1, relief='flat', bd=0,
                                  bg=self.theme_colors['day_header_bg'],
                                  fg=self.theme_colors['day_header_fg'])
            empty_header.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        
        for day, day_name in enumerate(day_names):
            day_header = tk.Label(grid_frame, text=day_name, 
                                font=self.theme_colors['day_header_font'], 
                                width=3, height=1, relief='flat', bd=0,
                                bg=self.theme_colors['day_header_bg'],
                                fg=self.theme_colors['day_header_fg'])
            col = day + 1 if self.show_week_numbers else day
            day_header.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
                
        # Create labels for each week and day
        for week in range(6):  # Maximum 6 weeks
            
            # Week number label
            if self.show_week_numbers:
                week_label = tk.Label(grid_frame, 
                                    font=self.theme_colors['week_number_font'], 
                                    relief='flat', bd=0, 
                                    bg=self.theme_colors['week_number_bg'], 
                                    fg=self.theme_colors['week_number_fg'])
                week_label.grid(row=week + 1, column=0, sticky='nsew', padx=1, pady=1)
                self.week_labels.append(week_label)
            
            # Day labels (clickable)
            for day in range(7):
                day_label = tk.Label(grid_frame, 
                                   font=self.theme_colors['day_font'], 
                                   relief='flat', bd=0, anchor='center',
                                   bg=self.theme_colors['day_bg'],
                                   fg=self.theme_colors['day_fg'],
                                   cursor='hand2',
                                   width=3, height=1)
                col = day + 1 if self.show_week_numbers else day
                day_label.grid(row=week + 1, column=col, sticky='nsew', padx=1, pady=1)
                
                # Store original colors for this label
                self.original_colors[day_label] = {
                    'bg': self.theme_colors['day_bg'],
                    'fg': self.theme_colors['day_fg']
                }
                
                # Bind click events
                day_label.bind('<Button-1>', lambda e, m=month_index, w=week, d=day: self._on_date_click(m, w, d))
                day_label.bind('<Enter>', lambda e, label=day_label: self._on_mouse_enter(label))
                day_label.bind('<Leave>', lambda e, label=day_label: self._on_mouse_leave(label))
                
                self.day_labels.append((month_index, week, day, day_label))
        
    def _get_day_names(self, short: bool = False) -> List[str]:
        """Get localized day names."""
        # Define base day names
        full_days = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                    "Friday", "Saturday", "Sunday"]
        short_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        # Choose day list based on short parameter
        days = short_days if short else full_days
        
        # Shift days based on week_start
        if self.week_start == "Sunday":
            # Move Sunday to the beginning
            days = days[-1:] + days[:-1]
        elif self.week_start == "Saturday":
            # Move Saturday to the beginning
            days = days[-2:] + days[:-2]
        
        # Get translations and handle short names
        day_names = []
        for day in days:
            if short:
                # For short names, get full name translation first, then truncate
                full_name = full_days[short_days.index(day)]
                full_translated = lang.get(full_name, self.winfo_toplevel())
                translated = full_translated[:3] if len(full_translated) >= 3 else full_translated
            else:
                translated = lang.get(day, self.winfo_toplevel())
            day_names.append(translated)
        
        return day_names
        
    def _get_month_name(self, month: int, short: bool = False) -> str:
        """Get localized month name."""
        # Define base month names
        full_months = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        short_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        # Get the month name based on short parameter
        if short:
            # For short names, get full name translation first, then truncate
            full_name = full_months[month - 1]
            full_translated = lang.get(full_name, self.winfo_toplevel())
            return full_translated[:3] if len(full_translated) >= 3 else full_translated
        else:
            month_name = full_months[month - 1]
            return lang.get(month_name, self.winfo_toplevel())
        
    def _is_year_first_in_format(self) -> bool:
        """Determine if year comes first in the date format by analyzing format string."""
        try:
            year_pos = self.date_format.find('%Y')
            month_pos = self.date_format.find('%m')
            day_pos = self.date_format.find('%d')
            
            # If no year in format, default to year first
            if year_pos == -1:
                return True
            
            # Check if year appears before month or day
            if month_pos != -1 and year_pos < month_pos:
                return True
            if day_pos != -1 and year_pos < day_pos:
                return True
            
            return False
        except:
            # Default to year first on any error
            return True
        
    def _get_display_date(self, month_index: int) -> datetime.date:
        """Get the date for a specific month frame, handling overflow."""
        # Use datetime arithmetic for more efficient month overflow handling
        base_date = datetime.date(self.year, self.month, 1)
        # Calculate target month and year using calendar module
        target_month = base_date.month + month_index
        target_year = base_date.year + (target_month - 1) // 12
        target_month = ((target_month - 1) % 12) + 1
        return datetime.date(target_year, target_month, 1)
    
    def _on_prev_month(self, month_index: int):
        """Handle previous month navigation."""
        current_date = self._get_display_date(month_index)
        # Use datetime replace for cleaner arithmetic
        if current_date.month == 1:
            prev_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            prev_date = current_date.replace(month=current_date.month - 1)
        
        self.set_date(prev_date.year, prev_date.month)
        
    def _on_next_month(self, month_index: int):
        """Handle next month navigation."""
        current_date = self._get_display_date(month_index)
        # Use datetime replace for cleaner arithmetic
        if current_date.month == 12:
            next_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_date = current_date.replace(month=current_date.month + 1)
        
        self.set_date(next_date.year, next_date.month)
        
    def _on_prev_year(self, month_index: int):
        """Handle previous year navigation."""
        current_date = self._get_display_date(month_index)
        prev_date = current_date.replace(year=current_date.year - 1)
        self.set_date(prev_date.year, prev_date.month)
        
    def _on_next_year(self, month_index: int):
        """Handle next year navigation."""
        current_date = self._get_display_date(month_index)
        next_date = current_date.replace(year=current_date.year + 1)
        self.set_date(next_date.year, next_date.month)
        
    def _on_month_header_click(self, month_index: int):
        """Handle month header click - switch to year view."""
        if self.year_view_callback:
            self.year_view_callback()
        
    def _on_mouse_enter(self, label):
        """Handle mouse enter event."""
        # Only highlight if not already selected
        current_bg = label.cget("bg")
        if current_bg not in [self.theme_colors['selected_bg'], self.theme_colors['range_bg']]:
            # Store current colors before changing to hover
            if label not in self.original_colors:
                self.original_colors[label] = {
                    'bg': current_bg,
                    'fg': label.cget("fg")
                }
            label.config(bg=self.theme_colors['hover_bg'], fg=self.theme_colors['hover_fg'])
        
    def _on_mouse_leave(self, label):
        """Handle mouse leave event."""
        # Only restore if not selected
        current_bg = label.cget("bg")
        if current_bg == self.theme_colors['hover_bg'] and label in self.original_colors:
            # Restore original colors
            original = self.original_colors[label]
            label.config(bg=original['bg'], fg=original['fg'])
        
    def _on_date_click(self, month_index: int, week: int, day: int):
        """Handle date button click."""
        # Get the first day of the month using existing helper
        first_day = self._get_display_date(month_index)
        
        # Get the first day of the week for this month efficiently
        first_weekday = self._get_week_start_offset(first_day)
        
        # Calculate the date for this position using datetime arithmetic
        days_from_start = week * 7 + day - first_weekday
        clicked_date = first_day + datetime.timedelta(days=days_from_start)
        
        # Handle selection based on mode
        if self.selectmode == "single":
            self.selected_date = clicked_date
            self.selected_range = None
        elif self.selectmode == "range":
            if self.selected_range is None:
                self.selected_range = (clicked_date, clicked_date)
            else:
                start_date, end_date = self.selected_range
                if clicked_date < start_date:
                    self.selected_range = (clicked_date, start_date)
                else:
                    self.selected_range = (start_date, clicked_date)
        
        # Update display
        self._update_display()
        
        # Call callback if set
        if self.selection_callback:
            if self.selectmode == "single":
                self.selection_callback(clicked_date)
            else:
                self.selection_callback(self.selected_range)
        
    def _update_display(self):
        if not self.winfo_exists():
            return
        # Check if in year view mode
        if self.year_view_mode:
            self._update_year_view()
            return
            
        week_label_index = 0
        
        for month_offset in range(self.months):
            # Get display date using existing helper
            display_date = self._get_display_date(month_offset)
            display_year = display_date.year
            display_month = display_date.month
                
            # Update year and month headers
            if self.show_month_headers:
                if hasattr(self, 'year_labels') and month_offset < len(self.year_labels):
                    year_label = self.year_labels[month_offset]
                    year_label.config(text=str(display_year))
                if hasattr(self, 'month_headers') and month_offset < len(self.month_headers):
                    month_label = self.month_headers[month_offset]
                    month_label.config(text=self._get_month_name(display_month, short=True))
            
            # Update day name headers
            children = self.month_frames[month_offset].winfo_children()
            if self.show_month_headers and len(children) > 1:
                days_frame = children[1]
            else:
                days_frame = children[0]
            day_names = self._get_day_names(short=True)
            
            # Find day header labels and update them
            day_header_index = 0
            for child in days_frame.winfo_children():
                if isinstance(child, tk.Label) and child.cget("text") == "":
                    # Skip empty header (week number column)
                    continue
                elif isinstance(child, tk.Label):
                    # This is a day header
                    if day_header_index < len(day_names):
                        child.config(text=day_names[day_header_index])
                        day_header_index += 1
            
            # Get calendar data efficiently using monthrange
            _, last_day = calendar.monthrange(display_year, display_month)
            month_days = list(self.cal.itermonthdays(display_year, display_month))
            
            # Update week numbers
            if self.show_week_numbers:
                # Reuse existing calendar object for efficiency
                month_calendar = self.cal.monthdatescalendar(display_year, display_month)
                
                for week in range(6):
                    if week_label_index + week < len(self.week_labels):
                        week_label = self.week_labels[week_label_index + week]
                        
                        if week < len(month_calendar):
                            # Get the week dates
                            week_dates = month_calendar[week]
                            
                            # Check if this week contains days from the current month
                            week_has_month_days = any(
                                date.year == display_year and date.month == display_month 
                                for date in week_dates
                            )
                            
                            if week_has_month_days:
                                # For ISO week numbers, we need to use the Monday of the week
                                # as the reference date for week number calculation
                                if self.week_start == "Monday":
                                    # Monday is already the first day of the week
                                    reference_date = week_dates[0]
                                elif self.week_start == "Saturday":
                                    # Saturday start: Monday is the third day (index 2)
                                    reference_date = week_dates[2]
                                else:  # Sunday
                                    # Sunday start: Monday is the second day (index 1)
                                    reference_date = week_dates[1]
                                
                                week_num = reference_date.isocalendar()[1]
                                week_label.config(text=str(week_num))
                            else:
                                week_label.config(text="")
                        else:
                            week_label.config(text="")
            
            # Update day labels
            for week in range(6):
                for day in range(7):
                    day_index = week * 7 + day
                    
                    # Find the corresponding label
                    for m, w, d, label in self.day_labels:
                        if m == month_offset and w == week and d == day:
                            if day_index < len(month_days):
                                day_num = month_days[day_index]
                                if day_num == 0:
                                    # Empty day - show previous/next month days
                                    self._set_adjacent_month_day(label, display_year, display_month, week, day)
                                else:
                                    # Valid day
                                    label.config(text=str(day_num))
                                    
                                    # Set colors
                                    self._set_day_colors(label, display_year, display_month, day_num)
                            else:
                                # Beyond month days
                                self._set_adjacent_month_day(label, display_year, display_month, week, day)
                            break
            
            # Update week label index for next month
            if self.show_week_numbers:
                week_label_index += 6
        
    def _set_adjacent_month_day(self, label, year: int, month: int, week: int, day: int):
        """Set display for adjacent month days."""
        # Calculate the date for this position using datetime arithmetic
        first_day = datetime.date(year, month, 1)
        
        # Get the first day of the week for this month efficiently
        first_weekday = self._get_week_start_offset(first_day)
        
        # Calculate the date for this position
        days_from_start = week * 7 + day - first_weekday
        clicked_date = first_day + datetime.timedelta(days=days_from_start)
        
        # Check if the date is valid (not in current month) using calendar module
        _, last_day = calendar.monthrange(year, month)
        current_month_start = datetime.date(year, month, 1)
        current_month_end = datetime.date(year, month, last_day)
        
        if clicked_date < current_month_start or clicked_date > current_month_end:
            # Adjacent month day
            label.config(text=str(clicked_date.day), 
                       bg=self.theme_colors['adjacent_day_bg'], 
                       fg=self.theme_colors['adjacent_day_fg'])
        else:
            # Empty day
            label.config(text="", 
                       bg=self.theme_colors['day_bg'], 
                       fg=self.theme_colors['day_fg'])
        
    def _set_day_colors(self, label, year: int, month: int, day: int):
        """Set colors for a specific day."""
        # Default colors
        bg_color = self.theme_colors['day_bg']
        fg_color = self.theme_colors['day_fg']
        
        # Create date object for comparison
        date_obj = datetime.date(year, month, day)
        
        # Check if it's selected
        if self.selectmode == "single" and self.selected_date == date_obj:
            bg_color = self.theme_colors['selected_bg']
            fg_color = self.theme_colors['selected_fg']
        elif self.selectmode == "range" and self.selected_range:
            start_date, end_date = self.selected_range
            if start_date <= date_obj <= end_date:
                if date_obj == start_date or date_obj == end_date:
                    bg_color = self.theme_colors['selected_bg']
                    fg_color = self.theme_colors['selected_fg']
                else:
                    bg_color = self.theme_colors['range_bg']
                    fg_color = self.theme_colors['range_fg']
        
        # Check if it's today (only if not selected)
        if bg_color == self.theme_colors['day_bg']:
            today = datetime.date.today()
            if year == today.year and month == today.month and day == today.day:
                if self.today_color is not None:
                    bg_color = self.today_color
                    fg_color = 'black'  # Default foreground for custom today color
                elif self.today_color is None and hasattr(self, 'today_color_set') and not self.today_color_set:
                    # Skip today color if explicitly set to "none"
                    pass
                else:
                    bg_color = self.theme_colors['today_bg']
                    fg_color = self.theme_colors['today_fg']
                
        # Check holiday colors (only if not selected)
        if bg_color == self.theme_colors['day_bg']:
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            if date_str in self.holidays:
                bg_color = self.holidays[date_str]
                
        # Check day of week colors (only if not selected)
        if bg_color == self.theme_colors['day_bg']:
            day_name = date_obj.strftime("%A")
            if day_name in self.day_colors:
                bg_color = self.day_colors[day_name]
            # Apply default weekend colors for Saturday and Sunday if no custom colors set
            elif day_name in ["Saturday", "Sunday"]:
                bg_color = self.theme_colors['weekend_bg']
                fg_color = self.theme_colors['weekend_fg']
                
        # Apply colors
        label.config(bg=bg_color, fg=fg_color)
        
        # Update original colors for hover effect restoration
        if label in self.original_colors:
            self.original_colors[label] = {
                'bg': bg_color,
                'fg': fg_color
            }
        
    def set_date(self, year: int, month: int):
        """Set the displayed year and month."""
        self.year = year
        self.month = month
        # If in year view mode, update year view
        if self.year_view_mode:
            self._update_year_view()
        else:
            self._update_display()
        
    def set_holidays(self, holidays: Dict[str, str]):
        """Set holiday colors dictionary."""
        self.holidays = holidays
        if not self.year_view_mode:
            self._update_display()
        
    def set_day_colors(self, day_colors: Dict[str, str]):
        """Set day of week colors dictionary."""
        self.day_colors = day_colors
        if not self.year_view_mode:
            self._update_display()
        
    def set_theme(self, theme: str):
        """Set the calendar theme."""
        try:
            self.theme_colors = get_calendar_theme(theme)
            self.theme = theme
        except ValueError as e:
            themes = get_calendar_themes()
            raise ValueError(f"theme must be one of {list(themes.keys())}")
        
        if self.year_view_mode and hasattr(self, 'year_view_window') and self.year_view_window:
            # Recreate year view with new theme
            self.year_view_window.destroy()
            self.year_view_window = None
            self.year_view_year_label = None
            self.year_view_labels.clear()
            self._create_year_view()
        else:
            self._update_display()
        
    def set_today_color(self, color: str):
        """Set the today color."""
        if color == "none":
            self.today_color = None
            self.today_color_set = False
        else:
            self.today_color = color
            self.today_color_set = True
        if not self.year_view_mode:
            self._update_display()
        
    def _recreate_widgets(self):
        """Recreate all widgets while preserving current settings."""
        # Store current settings
        current_day_colors = self.day_colors.copy()
        current_holidays = self.holidays.copy()
        current_show_week_numbers = self.show_week_numbers
        current_year_view_mode = self.year_view_mode
            
        # Destroy all existing widgets completely
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
        if hasattr(self, 'year_container'):
            self.year_container.destroy()
        
        # Clear all lists
        self.month_frames.clear()
        self.day_labels.clear()
        self.week_labels.clear()
        self.original_colors.clear()
        self.year_view_labels.clear()
        
        # Restore settings
        self.day_colors = current_day_colors
        self.holidays = current_holidays
        self.show_week_numbers = current_show_week_numbers
        self.year_view_mode = current_year_view_mode
        
        # Recreate everything
        if self.year_view_mode:
            self._create_year_view()
        else:
            self._create_widgets()
            self._update_display()
        
    def set_week_start(self, week_start: str):
        """Set the week start day."""
        if week_start not in ["Sunday", "Monday", "Saturday"]:
            raise ValueError("week_start must be 'Sunday', 'Monday', or 'Saturday'")
            
        self.week_start = week_start
        self._update_calendar_week_start()
        self._recreate_widgets()
        
    def set_show_week_numbers(self, show: bool):
        """Set whether to show week numbers."""
        self.show_week_numbers = show
        self._recreate_widgets()
        
    def refresh_language(self):
        """Refresh the display to reflect language changes."""
        if self.year_view_mode and hasattr(self, 'year_view_window') and self.year_view_window:
            # Recreate year view with new language
            self.year_view_window.destroy()
            self.year_view_window = None
            self.year_view_year_label = None
            self.year_view_labels.clear()
            self._create_year_view()
        else:
            self._update_display()
        
    def set_months(self, months: int):
        """Set the number of months to display."""
        if months < 1:
            raise ValueError("months must be at least 1")
            
        self.months = months
        
        # Update grid layout
        if months <= 3:
            self.grid_rows, self.grid_cols = 1, months
        elif months <= 6:
            self.grid_rows, self.grid_cols = 2, 3
        elif months <= 12:
            self.grid_rows, self.grid_cols = 3, 4
        else:
            self.grid_rows, self.grid_cols = 4, 4
        
        # Store current settings
        current_day_colors = self.day_colors.copy()
        current_holidays = self.holidays.copy()
        current_year_view_mode = self.year_view_mode
        
        # Destroy all existing widgets completely
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
        if hasattr(self, 'months_container'):
            self.months_container.destroy()
        if hasattr(self, 'year_container'):
            self.year_container.destroy()
        
        # Clear all lists
        self.month_frames.clear()
        self.day_labels.clear()
        self.week_labels.clear()
        self.original_colors.clear()
        if hasattr(self, 'month_headers'):
            self.month_headers.clear()
        if hasattr(self, 'year_labels'):
            self.year_labels.clear()
        self.year_view_labels.clear()
        
        # Restore settings
        self.day_colors = current_day_colors
        self.holidays = current_holidays
        self.year_view_mode = current_year_view_mode
        
        # Recreate everything
        if self.year_view_mode:
            self._create_year_view()
        else:
            self._create_widgets()
            self._update_display()
        
    def get_selected_date(self) -> Optional[datetime.date]:
        """Get the currently selected date (if any)."""
        return self.selected_date
        
    def get_selected_range(self) -> Optional[Tuple[datetime.date, datetime.date]]:
        """Get the currently selected date range (if any)."""
        return self.selected_range
        
    def get_popup_geometry(self, parent_widget: tk.Widget) -> str:
        """
        Calculate the optimal geometry for popup windows (calendar and year view).
        
        Args:
            parent_widget: The widget to which the popup is anchored.
        
        Returns:
            str: The geometry string for the popup window.
        """
        parent_widget.update_idletasks()
        x = parent_widget.winfo_rootx()
        y = parent_widget.winfo_rooty() + parent_widget.winfo_height()
        
        # Calculate width and height
        width = self.popup_width
        if self.show_week_numbers:
            width += WEEK_NUMBERS_WIDTH_OFFSET
        width *= self.months
        
        height = self.popup_height
        
        return f"{width}x{height}+{x}+{y}"
        
    def bind_date_selected(self, callback):
        """Bind a callback function to date selection events."""
        self.selection_callback = callback
        
    def set_selected_date(self, date: datetime.date):
        """Set the selected date."""
        self.selected_date = date
        self.selected_range = None
        if not self.year_view_mode:
            self._update_display()
        
    def set_selected_range(self, start_date: datetime.date, end_date: datetime.date):
        """Set the selected date range."""
        self.selected_range = (start_date, end_date)
        self.selected_date = None
        if not self.year_view_mode:
            self._update_display()
        
    def _create_year_view(self):
        """Create year view - placeholder method."""
        pass

    def _create_year_view_content(self):
        """Create year view content with 3x4 month grid."""
        
        # Set main frame background color
        self.configure(bg=self.theme_colors['background'])
        
        # Year header with navigation
        if self.show_navigation:
            header_frame = tk.Frame(self, bg=self.theme_colors['month_header_bg'])
            header_frame.pack(fill='x', pady=(5, 0))
            
            nav_frame = tk.Frame(header_frame, bg=self.theme_colors['month_header_bg'])
            nav_frame.pack(expand=True, fill='x')
            
            center_frame = tk.Frame(nav_frame, bg=self.theme_colors['month_header_bg'])
            center_frame.pack(expand=True)
            
            # Previous year button
            prev_btn = tk.Label(center_frame, text="<<",
                              font=self.theme_colors['navigation_font'],
                              bg=self.theme_colors['navigation_bg'],
                              fg=self.theme_colors['navigation_fg'],
                              cursor='hand2')
            prev_btn.pack(side='left', padx=(5, 0))
            prev_btn.bind('<Button-1>', lambda e: self._on_prev_year_year_view())
            prev_btn.bind('<Enter>', lambda e, btn=prev_btn: btn.config(bg=self.theme_colors['navigation_hover_bg'], fg=self.theme_colors['navigation_hover_fg']))
            prev_btn.bind('<Leave>', lambda e, btn=prev_btn: btn.config(bg=self.theme_colors['navigation_bg'], fg=self.theme_colors['navigation_fg']))
            
            # Year label
            self.year_view_year_label = tk.Label(center_frame, text=str(self.year),
                                               font=('TkDefaultFont', 12, 'bold'),
                                               relief='flat', bd=0,
                                               bg=self.theme_colors['month_header_bg'],
                                               fg=self.theme_colors['month_header_fg'])
            self.year_view_year_label.pack(side='left', padx=10)
            
            # Next year button
            next_btn = tk.Label(center_frame, text=">>",
                              font=self.theme_colors['navigation_font'],
                              bg=self.theme_colors['navigation_bg'],
                              fg=self.theme_colors['navigation_fg'],
                              cursor='hand2')
            next_btn.pack(side='left', padx=(0, 10))
            next_btn.bind('<Button-1>', lambda e: self._on_next_year_year_view())
            next_btn.bind('<Enter>', lambda e, btn=next_btn: btn.config(bg=self.theme_colors['navigation_hover_bg'], fg=self.theme_colors['navigation_hover_fg']))
            next_btn.bind('<Leave>', lambda e, btn=next_btn: btn.config(bg=self.theme_colors['navigation_bg'], fg=self.theme_colors['navigation_fg']))
        
        # Create month grid (3x4) in the year view window
        month_grid_frame = tk.Frame(self, bg=self.theme_colors['background'])
        month_grid_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Configure grid weights
        for i in range(4):
            month_grid_frame.columnconfigure(i, weight=1)
        for i in range(3):
            month_grid_frame.rowconfigure(i, weight=1)
        
        # Create month buttons
        self.year_view_labels = []
        for month in range(1, 13):
            row = (month - 1) // 4
            col = (month - 1) % 4
            
            month_name = self._get_month_name(month, short=True)
            
            month_label = tk.Label(month_grid_frame,
                                 text=month_name,
                                 font=('TkDefaultFont', 10, 'bold'),
                                 relief='flat', bd=1,
                                 bg=self.theme_colors['day_bg'],
                                 fg=self.theme_colors['day_fg'],
                                 cursor='hand2',
                                 width=6, height=2)
            month_label.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
            
            # Highlight current month
            if month == self.month:
                month_label.config(bg=self.theme_colors['selected_bg'],
                                 fg=self.theme_colors['selected_fg'])
            
            # Bind click events
            month_label.bind('<Button-1>', lambda e, m=month: self._on_year_view_month_click(m))
            month_label.bind('<Enter>', lambda e, label=month_label: self._on_year_view_mouse_enter(label))
            month_label.bind('<Leave>', lambda e, label=month_label: self._on_year_view_mouse_leave(label))
            
            self.year_view_labels.append((month, month_label))

    def _on_prev_year_year_view(self):
        """Handle previous year navigation in year view."""
        self.year -= 1
        self._update_year_view()

    def _on_next_year_year_view(self):
        """Handle next year navigation in year view."""
        self.year += 1
        self._update_year_view()

    def _on_year_view_month_click(self, month: int):
        """Handle month click in year view."""
        self.month = month
        self.year_view_mode = False
        
        # Call date callback if available
        if self.date_callback:
            self.date_callback(self.year, month)

    def _on_year_view_mouse_enter(self, label):
        """Handle mouse enter event in year view."""
        current_bg = label.cget("bg")
        if current_bg != self.theme_colors['selected_bg']:
            label.config(bg=self.theme_colors['hover_bg'], fg=self.theme_colors['hover_fg'])

    def _on_year_view_mouse_leave(self, label):
        """Handle mouse leave event in year view."""
        current_bg = label.cget("bg")
        if current_bg == self.theme_colors['hover_bg']:
            # Check if this is the current month
            for month, month_label in self.year_view_labels:
                if month_label == label:
                    if month == self.month:
                        label.config(bg=self.theme_colors['selected_bg'], fg=self.theme_colors['selected_fg'])
                    else:
                        label.config(bg=self.theme_colors['day_bg'], fg=self.theme_colors['day_fg'])
                    break

    def _update_year_view(self):
        """Update year view display."""
        if hasattr(self, 'year_view_year_label'):
            self.year_view_year_label.config(text=str(self.year))
            
        # Update month labels
        for month, label in self.year_view_labels:
            # Reset to default colors
            label.config(bg=self.theme_colors['day_bg'],
                        fg=self.theme_colors['day_fg'])
            
            # Highlight current month
            if month == self.month:
                label.config(bg=self.theme_colors['selected_bg'],
                           fg=self.theme_colors['selected_fg'])


            
    def set_popup_size(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        Set the popup size for both calendar and year view.
        
        Args:
            width: Width in pixels (None to use default)
            height: Height in pixels (None to use default)
        """
        if width is not None:
            self.popup_width = width
        else:
            self.popup_width = DEFAULT_POPUP_WIDTH
            
        if height is not None:
            self.popup_height = height
        else:
            self.popup_height = DEFAULT_POPUP_HEIGHT


# Theme loading functions
def _parse_font(font_str: str) -> tuple:
    """
    Parse font string from .ini file to tuple format.
    
    Args:
        font_str: Font string in format "family, size, style"
        
    Returns:
        tuple: Font tuple (family, size, style)
    """
    parts = [part.strip() for part in font_str.split(',')]
    if len(parts) >= 2:
        family = parts[0]
        try:
            size = int(parts[1])
        except ValueError:
            size = 9
        style = parts[2] if len(parts) > 2 else 'normal'
        return (family, size, style)
    return ("TkDefaultFont", 9, "normal")


def _load_theme_file(theme_name: str) -> Dict[str, Any]:
    """
    Load theme from .ini file.
    
    Args:
        theme_name: Name of the theme file (without .ini extension)
        
    Returns:
        dict: Theme definition dictionary
        
    Raises:
        FileNotFoundError: If theme file doesn't exist
        configparser.Error: If .ini file is malformed
    """
    # Get the directory where this module is located
    current_dir = Path(__file__).parent.parent / "themes"
    theme_file = current_dir / f"{theme_name}.ini"
    
    if not theme_file.exists():
        raise FileNotFoundError(f"Theme file not found: {theme_file}")
    
    config = configparser.ConfigParser()
    config.read(theme_file)
    
    if theme_name not in config:
        raise configparser.Error(f"Theme section '{theme_name}' not found in {theme_file}")
    
    theme_section = config[theme_name]
    theme_dict = {}
    
    for key, value in theme_section.items():
        # Parse font values
        if 'font' in key.lower():
            theme_dict[key] = _parse_font(value)
        else:
            theme_dict[key] = value
    
    return theme_dict


def get_calendar_themes() -> Dict[str, Dict[str, Any]]:
    """
    Get all available calendar themes.
    
    Returns:
        dict: Dictionary containing all theme definitions
    """
    themes = {}
    current_dir = Path(__file__).parent.parent / "themes"
    
    # Look for .ini files in the theme directory
    for theme_file in current_dir.glob("*.ini"):
        theme_name = theme_file.stem  # filename without extension
        try:
            themes[theme_name] = _load_theme_file(theme_name)
        except (FileNotFoundError, configparser.Error) as e:
            # Skip malformed theme files
            continue
    
    return themes


def get_calendar_theme(theme_name: str) -> Dict[str, Any]:
    """
    Get a specific calendar theme by name.
    
    Args:
        theme_name: Name of the theme
        
    Returns:
        dict: Theme definition for the specified theme name
        
    Raises:
        ValueError: If the theme name is not found
    """
    try:
        return _load_theme_file(theme_name)
    except FileNotFoundError:
        available_themes = list(get_calendar_themes().keys())
        raise ValueError(f"Theme '{theme_name}' not found. Available themes: {available_themes}")
    except configparser.Error as e:
        raise ValueError(f"Error loading theme '{theme_name}': {e}") 
