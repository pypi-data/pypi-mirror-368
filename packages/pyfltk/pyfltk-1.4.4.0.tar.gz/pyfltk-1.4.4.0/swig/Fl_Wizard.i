/* File : Fl_Wizard.i */
//%module Fl_Wizard

%feature("docstring") ::Fl_Wizard
"""
The Fl_Wizard widget is based off the Fl_Tabs widget, but instead of 
displaying tabs it only changes 'tabs' under program control. Its primary 
purpose is to support 'wizards' that step a user through configuration or 
troubleshooting tasks.

As with Fl_Tabs, wizard panes are composed of child (usually Fl_Group) 
widgets. Navigation buttons must be added separately. 
""" ;

%{
#include "FL/Fl_Wizard.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Wizard)

%include "FL/Fl_Wizard.H"
