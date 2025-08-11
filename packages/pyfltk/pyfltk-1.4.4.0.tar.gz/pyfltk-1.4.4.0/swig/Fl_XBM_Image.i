/* File : Fl_XBM_Image.i */
//%module Fl_XBM_Image

%feature("docstring") ::Fl_XBM_Image
"""
The Fl_XBM_Image class supports loading, caching, and drawing of X Bitmap 
(XBM) bitmap files.
""" ;

%{
#include "FL/Fl_XBM_Image.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_XBM_Image)

%include "FL/Fl_XBM_Image.H"
