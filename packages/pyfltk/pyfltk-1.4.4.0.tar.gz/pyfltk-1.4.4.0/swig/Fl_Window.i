// File : Fl_Window.i 

%feature("docstring") ::Fl_Window
"""
This widget produces an actual window. This can either be a main window, 
with a border and title and all the window management controls, or a 
'subwindow' inside a window. This is controlled by whether or not the 
window has a parent().

Once you create a window, you usually add children Fl_Widget 's to it by 
using window->add(child) for each new widget. See Fl_Group for more 
information on how to add and remove children.

There are several subclasses of Fl_Window that provide double-buffering, 
overlay, menu, and OpenGL support.

The window's callback is done if the user tries to close a window using 
the window manager and Fl.modal() is zero or equal to the window. Fl_Window 
has a default callback that calls Fl_Window.hide(). 
""" ;

%feature("nodirector") Fl_Window::show;

%{
#include "FL/Fl_Window.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Window)

%ignore Fl_Window::hotspot(const Fl_Widget& p, int offscreen = 0);
%ignore Fl_Window::show();
%ignore Fl_Window::show(int argc, char** argv);
%ignore Fl_Window::combine_mask();

%include "WindowShowTypemap.i"

%include "FL/Fl_Window.H"

// override method show
%extend Fl_Window {
	MACRO_WINDOW_SHOW
}

