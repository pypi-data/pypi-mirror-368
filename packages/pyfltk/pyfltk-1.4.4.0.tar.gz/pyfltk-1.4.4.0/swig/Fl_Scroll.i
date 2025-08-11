/* File : Fl_Scroll.i */
//%module Fl_Scroll

%feature("docstring") ::Fl_Scroll
"""
This container widget lets you maneuver around a set of widgets much larger 
than your window. If the child widgets are larger than the size of this 
object then scrollbars will appear so that you can scroll over to them:

If all of the child widgets are packed together into a solid rectangle then 
you want to set box() to FL_NO_BOX or one of the _FRAME types. This will 
result in the best output. However, if the child widgets are a sparse 
arrangment you must set box() to a real _BOX type. This can result in some 
blinking during redrawing, but that can be solved by using a Fl_Double_Window.

This widget can also be used to pan around a single child widget 'canvas'. 
This child widget should be of your own class, with a draw() method that 
draws the contents. The scrolling is done by changing the x() and y() of 
the widget, so this child must use the x() and y() to position it's drawing. 
To speed up drawing it should test fl_push_clip() .

Another very useful child is a single Fl_Pack, which is itself a group that 
packs it's children together and changes size to surround them. Filling the 
Fl_Pack with Fl_Tabs groups (and then putting normal widgets inside those) 
gives you a very powerful scrolling list of individually-openable panels.

Fluid lets you create these, but you can only lay out objects that fit 
inside the Fl_Scroll without scrolling. Be sure to leave space for the 
scrollbars, as Fluid won't show these either.

You cannot use Fl_Window as a child of this since the clipping is not 
conveyed to it when drawn, and it will draw over the scrollbars and 
neighboring objects.
""" ;

%{
#include "FL/Fl_Scroll.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Scroll)

%ignore Fl_Scroll::scrollbar;
%ignore Fl_Scroll::hscrollbar;

%include "FL/Fl_Scroll.H"

%extend Fl_Scroll {
	Fl_Scrollbar* getScrollbar() {
		return &(self->scrollbar);
	}
	Fl_Scrollbar* getHScrollbar() {
		return &(self->hscrollbar);
	}
}	
