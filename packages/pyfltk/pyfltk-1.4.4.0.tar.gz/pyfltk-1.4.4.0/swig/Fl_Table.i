/* File : Fl_Table.i */

%feature("docstring") ::Fl_Table
"""
This is the base class for table widgets. (eg. Fl_Table_Row). To be useful it must be subclassed and several virtual functions defined. Normally applications use widgets derived from this widget, and do not use this widget directly; this widget is usually too low level to be used directly by applications.

This widget does not handle the data in the table. The draw_cell() method must be overridden by a subclass to manage drawing the contents of the cells.

This widget can be used in several ways:

    * As a custom widget; see testtablerow.cxx. Very optimal for even extremely large tables.

    * As a table made up of a single FLTK widget instanced all over the table; see singleinput.cxx. Very optimal for even extremely large tables;

    * As a regular container of FLTK widgets, one widget per cell. See widgettable.cxx. Not recommended for large tables.

When acting as part of a custom widget, events on the cells and/or headings generate callbacks when they are clicked by the user. You control when events are generated based on the setting for Fl_Table::when().

When acting as a container for FLTK widgets, the FLTK widgets maintain themselves. Although the draw_cell() method must be overridden, its contents can be very simple. See the draw_cell() code in widgettable.cxx. 
""" ;

%{
#include "FL/Fl_Table.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Table)

//%ignore Fl_Table::draw_cell;
%ignore Fl_Table::array;


%include "FL/Fl_Table.H"

