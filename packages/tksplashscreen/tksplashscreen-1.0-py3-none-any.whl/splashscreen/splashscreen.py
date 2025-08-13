import logging
import threading
import tkinter as tk
from typing import Dict, Optional, Tuple, Union

logging.basicConfig( level = logging.INFO )

EnumPlacement = {
    'BR': lambda w, h, sw, sh: ( sw - w - 10, sh - h - 50 ),         # Bottom Right
    'BL': lambda w, h, sw, sh: ( 10, sh - h - 50 ),                  # Bottom Left
    'TR': lambda w, h, sw, sh: ( sw - w - 10, 10 ),                  # Top Right
    'TL': lambda w, h, sw, sh: ( 10, 10 ),                           # Top Left
    'C':  lambda w, h, sw, sh: ( ( sw - w) // 2, ( sh - h ) // 2 ),  # Center
    'CL': lambda w, h, sw, sh: ( 10, ( sh - h) // 2 ),               # Center Left
    'CR': lambda w, h, sw, sh: ( sw - w - 10, (sh - h ) // 2 ),      # Center Right
    'BC': lambda w, h, sw, sh: ( ( sw - w ) // 2, sh - h - 50 ),     # Bottom Center
    'TC': lambda w, h, sw, sh: ( ( sw - w ) // 2, 10 ),              # Top Center
}

class Placement:
    """ Handles placement logic for the splash screen """
    def __init__( self, placement: Union[ str, Dict ] ):
        """ Initialize placement with either a string or a dict """
        if isinstance( placement, dict ):
            self._placement = placement
        elif isinstance( placement, str ):
            try:
                self._placement = EnumPlacement[ placement.upper() ]
            except KeyError:
                logging.warning( "Invalid placement '%s'; defaulting to BR", placement )
                self._placement = EnumPlacement[ 'BR' ]
        else:
            logging.warning( "Unsupported placement type %s; defaulting to BR", type( placement ) )
            self._placement = EnumPlacement[ 'BR' ]

    def compute_geometry( self, root: tk.Tk, label: tk.Label ):
        """ Compute the geometry string for the splash screen """
        root.update_idletasks()
        width = label.winfo_reqwidth() + 40
        height = label.winfo_reqheight() + 40
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()

        x, y = self._placement( width, height, sw, sh )

        return f"{ width }x{ height }+{ x }+{ y }"

class SplashScreen:
    """ A simple splash screen class using tkinter """
    def __init__( self,
                 message: str,
                 close_after: Optional[ float ] = None,
                 placement: Optional[ str ] = "BR",
                 font: Optional[ Union[ str, Tuple ] ] = None,
                 bg: str = "#00538F",
                 fg: str = "white"
                ):
        """ Initialize the splash screen

            message (str): The message to display on the splash screen.
            close_after (float): Time in seconds after which the splash screen will close automatically.
            placement (str): Placement of the splash screen on the screen.
            font (str | tuple): Font specification for the message.
            bg (str): Background color of the splash screen.
            fg (str): Foreground color of the message text.
        """
        self.message = message
        self.auto_close_after = close_after
        self.bg = bg
        self.fg = fg

        self.root = None
        self.label = None
        self._placement = Placement( placement )
        self._font = font

        self._ready_event = threading.Event()
        self._thread = threading.Thread( target = self._create_window )
        self._thread.start()
        self._ready_event.wait()

    def _close_window( self ):
        """ Close the splash screen window safely """
        if self.root:
            self.root.quit()     # exits the mainloop
            self.root.after( 0, self.root.destroy )

    def _create_window( self ):
        """ Create the splash screen window in a separate thread """
        try:
            self.root = tk.Tk()
            self.root.attributes( "-topmost", True )
            self.root.overrideredirect( True )
            self.root.configure( bg = self.bg )

            if isinstance( self._font, str ):
                try:
                    temptup =  tuple( self._font.split( ',' ) )
                    if len( temptup ) < 3:
                        raise
                    font = temptup[0].strip()
                    size = int( temptup[1].strip() ) or 18
                    style = temptup[2].strip() or "normal"
                    self._font = ( font, size, style )
                except:
                    logging.warning( "Invalid font format '%s'; using default", self._font )
                    temptup = ( "Calibri", 18, "bold" )
            elif isinstance( self._font, tuple ):
                temptup = self._font

            self.fg = self._normalize_color( self.fg, "white" )
            self.bg = self._normalize_color( self.bg, "#00538F" )

            self.label = tk.Label( self.root, text = self.message,
                                  font = self._font,
                                  fg = self.fg, bg = self.bg, justify = "left", wraplength = 400 )
            self.label.pack( padx = 20, pady = 20 )

            self._resize_and_position()
            self._ready_event.set()

            if self.auto_close_after:
                # Schedule the close from the main thread safely
                def close_wrapper():
                    self.close()
                self.root.after( int( self.auto_close_after * 1000 ), close_wrapper )

            self.root.mainloop()
        except Exception as e:
            logging.exception( "Failed to create splash screen: %s", e )

    def _normalize_color( self, value: str | tuple, default: str ):
        """Return a valid Tkinter color string, or default if invalid.

            value (str | tuple): Color value as a string or RGB tuple.
            default (str): Default color value to return if the input is invalid.
        Returns:
            str: Valid Tkinter color string.
        """

        if isinstance( value, str ):
            if self._is_valid_color( value ):
                return value
            else:
                logging.warning( "Invalid color '%s'; using default '%s'", value, default )
                return default
        elif isinstance( value, tuple ) and len( value ) == 3 and all( isinstance( c, int ) for c in value ):
            return f'#{ value[ 0 ]:02x }{ value[ 1 ]:02x }{ value[ 2 ]:02x }'
        else:
            return default

    def _resize_and_position( self ):
        """ Resize and position the splash screen based on the current placement """
        geom = self._placement.compute_geometry( self.root, self.label )

        self.root.geometry( geom )

    def _is_valid_color( self, color: str) -> bool:
        """ Check if the given color is valid """
        try:
            self.root.winfo_rgb( color )
            return True
        except tk.TclError:
            return False

    def update_message( self, new_text: str, append: Optional[ bool ] = False ):
        """ Update the splash screen message """
        if self.root:
            self.root.after( 0, lambda: self._update_text( new_text, append ) )

    def _update_text( self, new_text: str, append: Optional[ bool ] = False ):
        """ Update the label text in the main thread """
        if append:
            self.label.config( text = self.label[ "text" ] + new_text )
        else:
            self.label.config( text = new_text )
        self._resize_and_position()

    def update_color( self, new_color: str ):
        """ Update the splash screen background color """
        if self.root:
            def change_color():
                try:
                    self.root.config( bg = new_color )
                    self.label.config( bg = new_color )
                except tk.TclError as e:
                    logging.warning( "Invalid color '%s': %s", new_color, e )
            self.root.after( 0, change_color )

    def close( self, close_after_sec: float = 0 ):
        """ Close the splash screen after a specified time """
        if self.root:
            delay = int( close_after_sec * 1000 )
            self.root.after( delay, self._close_window )
