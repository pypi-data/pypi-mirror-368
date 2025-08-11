/* File : Fl_PNM_Image.i */
//%module Fl_PNM_Image

%feature("docstring") ::Fl_PNM_Image
"""
The Fl_PNM_Image class supports loading, caching, and drawing of Portable 
Anymap (PNM, PBM, PGM, PPM) image files. The class loads bitmap, grayscale, 
and full-color images in both ASCII and binary formats.
""" ;

%{
#include "FL/Fl_PNM_Image.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_PNM_Image)

%include "FL/Fl_PNM_Image.H"
