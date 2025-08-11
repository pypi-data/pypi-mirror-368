/* File : Fl_XPM_Image.i */
//%module Fl_XPM_Image

%feature("docstring") ::Fl_XPM_Image
"""
The Fl_XPM_Image class supports loading, caching, and drawing of X Pixmap (XPM) images, including transparency.
""" ;

%{
#include "FL/Fl_XPM_Image.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_XPM_Image)

%include "FL/Fl_XPM_Image.H"
