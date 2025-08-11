/* File : Fl_Color_Chooser.i */
//%module Fl_Color_Chooser

%feature("docstring") ::Fl_Color_Chooser
"""
The Fl_Color_Chooser widget provides a standard RGB color chooser. You can 
place any number of these into a panel of your own design. This widget 
contains the hue box, value slider, and rgb input fields from the above 
diagram (it does not have the color chips or the Cancel or OK buttons). The 
callback is done every time the user changes the rgb value. It is not done 
if they move the hue control in a way that produces the same rgb value, such 
as when saturation or value is zero.
""" ;

%{
#include "FL/Fl_Color_Chooser.H"
%}

%ignore fl_color_chooser(const char* name, double& r, double &g,
double &b);

%include "typemaps.i"
%apply unsigned char& INOUT {unsigned char& r};
%apply unsigned char& INOUT {unsigned char& g};
%apply unsigned char& INOUT {unsigned char& b};

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Color_Chooser)

CHANGE_OWNERSHIP(Flcc_HueBox)

CHANGE_OWNERSHIP(Flcc_ValueBox)

CHANGE_OWNERSHIP(Flcc_Value_Input)

%include "FL/Fl_Color_Chooser.H"



