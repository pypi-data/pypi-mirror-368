/* File : Fl_Table_Row.i */

%feature("docstring") ::Fl_Table_Row
"""
This class implements a simple table of rows and columns that specializes in the selection of rows. This widget is similar in behavior to a 'mail subject browser', similar to that found in mozilla, netscape and outlook mail browsers.

Most methods of importance will be found in the Fl_Table widget, such as rows() and cols().

To be useful it must be subclassed and at minimum the draw_cell() method must be overridden to provide the content of the cells. This widget does not manage the cell's data content; it is up to the parent class's draw_cell() method override to provide this.

Events on the cells and/or headings generate callbacks when they are clicked by the user. You control when events are generated based on the values you supply for when(). 
""" ;

%{
#include "FL/Fl_Table_Row.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Table_Row)

//%ignore Fl_Table_Row::draw_cell;
//%ignore Fl_Table_Row::find_cell;

%apply int& INOUT {int& X};
%apply int& INOUT {int& Y};
%apply int& INOUT {int& W};
%apply int& INOUT {int& H};

%include "FL/Fl_Table_Row.H"

