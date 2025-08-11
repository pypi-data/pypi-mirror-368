/* File : Fl_Overlay_Window.i */
//%module Fl_Overlay_Window

%feature("docstring") ::Fl_Overlay_Window
"""
This window provides double buffering and also the ability to draw the 
'overlay' which is another picture placed on top of the main image. The 
overlay is designed to be a rapidly-changing but simple graphic such as 
a mouse selection box. Fl_Overlay_Window uses the overlay planes provided 
by your graphics hardware if they are available.

If no hardware support is found the overlay is simulated by drawing directly 
into the on-screen copy of the double-buffered window, and 'erased' by 
copying the backbuffer over it again. This means the overlay will blink if 
you change the image in the window. 
""" ;

%feature("nodirector") Fl_Overlay_Window::show;

%{
#include "FL/Fl_Overlay_Window.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Overlay_Window)

%include "WindowShowTypemap.i"

// override method show
%extend Fl_Overlay_Window {
	MACRO_WINDOW_SHOW
}

// ignore original declaration
%ignore Fl_Overlay_Window::show();
%ignore Fl_Overlay_Window::show(int argc, char** argv);

%include "FL/Fl_Overlay_Window.H"
