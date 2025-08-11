/* File : Fl_Tabs.i */
//%module Fl_Tabs

%feature("docstring") ::Fl_Tabs
"""
The Fl_Tabs widget is the 'file card tabs' interface that allows you to 
put lots and lots of buttons and switches in a panel, as popularized by 
many toolkits.

Clicking the tab makes a child visible() by calling show() on it, and 
all other children are made invisible by calling hide() on them. Usually 
the children are Fl_Group widgets containing several widgets themselves.

Each child makes a card, and it's label() is printed on the card tab, 
including the label font and style. The selection color of that child 
is used to color the tab, while the color of the child determines the 
background color of the pane.

The size of the tabs is controlled by the bounding box of the children 
(there should be some space between the children and the edge of the Fl_Tabs), 
and the tabs may be placed 'inverted' on the bottom, this is determined 
by which gap is larger. It is easiest to lay this out in fluid, using the 
fluid browser to select each child group and resize them until the tabs 
look the way you want them to. 
""" ;

%{
#include "FL/Fl_Tabs.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Tabs)

%include "FL/Fl_Tabs.H"
