/* File : Fl_PDF_File_Surface.i */

%feature("docstring") ::Fl_Device
"""
Declaration of classes Fl_Surface_Device and Fl_Display_Device.
""" ;

%{
#include "FL/Fl_Device.H"
%}

//%include "macros.i"

//CHANGE_OWNERSHIP(Fl_Device)
%ignore Fl_Xlib_Graphics_Driver;
%ignore Fl_Quartz_Graphics_Driver;
%ignore Fl_GDI_Graphics_Driver;
%ignore Fl_Device_Plugin::opengl_plugin();

%rename(_print) print;

%include "FL/Fl_Device.H"

%rename("") print;

