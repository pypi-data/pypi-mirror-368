/* File : Fl_Single_Window.i */
//%module Fl_Single_Window

%feature("docstring") ::Fl_Single_Window
"""
This is the same as Fl_Window. However, it is possible that some 
implementations will provide double-buffered windows by default. This 
subclass can be used to force single-buffering. This may be useful for 
modifying existing programs that use incremental update, or for some 
types of image data, such as a movie flipbook.
""" ;

%feature("nodirector") Fl_Single_Window::show;

%{
#include "FL/Fl_Single_Window.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Single_Window)

%ignore Fl_Single_Window::make_current();


%include "WindowShowTypemap.i"

// override method show
%extend Fl_Single_Window {
	MACRO_WINDOW_SHOW
}

// ignore original declaration
%ignore Fl_Single_Window::show();
%ignore Fl_Single_Window::show(int argc, char** argv);

%include "FL/Fl_Single_Window.H"
