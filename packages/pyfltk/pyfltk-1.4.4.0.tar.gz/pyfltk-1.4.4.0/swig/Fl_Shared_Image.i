/* File : Fl_Shared_Image.i */
//%module Fl_Shared_Image

%feature("docstring") ::Fl_Shared_Image
"""
The Fl_Shared_Image class supports caching, loading, and drawing of image 
files. Most applications will also want to link against the fltk_images 
library and call the fl_register_images() function to support standard image 
formats such as BMP, GIF, JPEG, and PNG.
""" ;

%{
#include "FL/Fl_Shared_Image.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_Shared_Image)

%include "FL/Fl_Shared_Image.H"
