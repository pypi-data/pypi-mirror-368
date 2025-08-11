/* File : Fl_Output.i */
//%module Fl_Output

%feature("docstring") ::Fl_Output
"""
This widget displays a piece of text. When you set the value() , Fl_Output 
does a strcpy() to it's own storage, which is useful for program-generated 
values. The user may select portions of the text using the mouse and paste 
the contents into other fields or programs.

There is a single subclass, Fl_Multiline_Output, which allows you to 
display multiple lines of text.

The text may contain any characters except \0, and will correctly display 
anything, using ^X notation for unprintable control characters and \nnn 
notation for unprintable characters with the high bit set. It assumes the 
font can draw any characters in the ISO-Latin1 character set. 
""" ;

%{
#include "FL/Fl_Output.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Output)

%include "FL/Fl_Output.H"
