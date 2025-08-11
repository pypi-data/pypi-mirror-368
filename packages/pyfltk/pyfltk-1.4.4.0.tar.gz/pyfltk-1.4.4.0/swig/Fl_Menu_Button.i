/* File : Fl_Menu_Button.i */
//%module Fl_Menu_Button

%feature("docstring") ::Fl_Menu_Button
"""
This is a button that when pushed pops up a menu (or hierarchy of menus) 
defined by an array of Fl_Menu_Item objects.

Fl_Menu_Button widget.

Normally any mouse button will pop up a menu and it is lined up below the 
button as shown in the picture. However an Fl_Menu_Button may also control 
a pop-up menu. This is done by setting the type() , see below.

The menu will also pop up in response to shortcuts indicated by putting 
a '&' character in the label().

Typing the shortcut() of any of the menu items will cause callbacks exactly 
the same as when you pick the item with the mouse. The '&' character in menu 
item names are only looked at when the menu is popped up, however.

When the user picks an item off the menu, the item's callback is done with 
the menu_button as the Fl_Widget* argument. If the item does not have a 
callback the menu_button's callback is done instead. 
""" ;

%{
#include "FL/Fl_Menu_Button.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Menu_Button)

%include "FL/Fl_Menu_Button.H"
