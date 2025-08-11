/* File : Fl_Double_Window.i */
//%module Fl_Double_Window

%feature("docstring") ::Fl_Double_Window
"""
The Fl_Double_Window class provides a double-buffered window. If possible 
this will use the X double buffering extension (Xdbe). If not, it will draw 
the window data into an off-screen pixmap, and then copy it to the on-screen 
window.

It is highly recommended that you put the following code before the first 
show() of any window in your program:

      Fl.visual(FL_DOUBLE|FL_INDEX)

This makes sure you can use Xdbe on servers where double buffering does not 
exist for every visual.
""" ;

%feature("nodirector") Fl_Double_Window::show;

%{
#include "FL/Fl_Double_Window.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Double_Window)

%include "WindowShowTypemap.i"

// override method show
%extend Fl_Double_Window {
	MACRO_WINDOW_SHOW
}

// ignore original declaration
%ignore Fl_Double_Window::show();
%ignore Fl_Double_Window::show(int argc, char** argv);

%include "FL/Fl_Double_Window.H"


