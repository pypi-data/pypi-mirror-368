/* File : Fl_Menu_Window.i */
//%module Fl_Menu_Window

%feature("docstring") ::Fl_Menu_Window
"""
The Fl_Menu_Window widget is a window type used for menus. By default the 
window is drawn in the hardware overlay planes if they are available so that 
the menu don't force the rest of the window to redraw.
""" ;

%{
#include "FL/Fl_Menu_Window.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Menu_Window)

%include "FL/Fl_Menu_Window.H"
