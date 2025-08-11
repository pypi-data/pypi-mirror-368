/* File : Fl_BMP_Image.i */
//%module Fl_BMP_Image

%feature("docstring") ::Fl_BMP_Image
"""
The Fl_BMP_Image class supports loading, caching, and drawing of 
Windows Bitmap (BMP) image files.
""" ;

%{
#include "FL/Fl_BMP_Image.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_BMP_Image)

%include "FL/Fl_BMP_Image.H"
