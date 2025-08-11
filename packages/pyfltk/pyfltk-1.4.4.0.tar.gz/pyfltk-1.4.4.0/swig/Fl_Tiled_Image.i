/* File : Fl_Tiled_Image.i */
//%module Fl_Tiled_Image

%feature("docstring") ::Fl_Tiled_Image
"""
The Fl_Tiled_Image class supports tiling of images over a specified area. 
The source (tile) image is not copied unless you call the color_average(), 
desaturate(), or inactive() methods.
""" ;

%{
#include "FL/Fl_Tiled_Image.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_Tiled_Image)

%include "FL/Fl_Tiled_Image.H"
