/* File : Fl_Menu_Item.i */
//%module Fl_Menu_Item

%feature("docstring") ::Fl_Menu_Item
"""
The Fl_Menu_Item structure defines a single menu item that is used by the 
Fl_Menu_ class. This structure is defined as

      Fl_Menu_Item :
        text 		-> character array # label()
        shortcut_ 	-> unsigned long
        callback_	-> Fl_Callback
        user_data_	
        flags		-> int
        labeltype_	-> unsigned character
        labelfont_	-> unsigned character
        labelsize_	-> unsigned character
        labelcolor_	-> unsigned character
      

      enum: # values for flags:
        FL_MENU_INACTIVE	= 1,
        FL_MENU_TOGGLE		= 2,
        FL_MENU_VALUE		= 4,
        FL_MENU_RADIO		= 8,
        FL_MENU_INVISIBLE	= 0x10,
        FL_SUBMENU_POINTER	= 0x20,
        FL_SUBMENU		= 0x40,
        FL_MENU_DIVIDER		= 0x80,
        FL_MENU_HORIZONTAL	= 0x100
      

Typically menu items are statically defined; for example:

      MenuTable = (
        ('&alpha',   FL_ALT+ord('a'), the_cb, 1),
        ('&beta',    FL_ALT+ord('b'), the_cb, 2),
        ('gamma',    FL_ALT+ord('c'), the_cb, 3, FL_MENU_DIVIDER),
        ('&strange',  0,   strange_cb),
        ('&charm',    0,   charm_cb),
        ('&truth',    0,   truth_cb),
        ('b&eauty',   0,   beauty_cb),
        ('sub&menu',	0,   0, 0, FL_SUBMENU),
          ('one'),
          ('two'),
          ('three'),
        (None,),
        ('inactive', FL_ALT+'i', 0, 0, FL_MENU_INACTIVE|FL_MENU_DIVIDER),
        ('invisible',FL_ALT+'i', 0, 0, FL_MENU_INVISIBLE),
        ('check',    FL_ALT+'i', 0, 0, FL_MENU_TOGGLE|FL_MENU_VALUE),
        ('box',      FL_ALT+'i', 0, 0, FL_MENU_TOGGLE),
      (None,);

A submenu title is identified by the bit FL_SUBMENU in the flags field, 
and ends with a label() that is NULL. You can nest menus to any depth. A 
pointer to the first item in the submenu can be treated as an Fl_Menu array 
itself. It is also possible to make seperate submenu arrays with 
FL_SUBMENU_POINTER flags.

You should use the method functions to access structure members and not 
access them directly to avoid compatibility problems with future releases 
of FLTK. 
""" ;

%{
#include "FL/Fl_Menu_Item.H"
#include <CallbackStruct.h>
#include "FL/Fl_Multi_Label.H"
%}

//%include "macros.i"
//CHANGE_OWNERSHIP(Fl_Menu_Item)

%pythonappend Fl_Menu_Item::add_multi_label %{
        if len(args) > 0:
            args[0].this.disown()
%}

//%ignore Fl_Menu_Item::image(Fl_Image& a);
%ignore fl_old_shortcut(const char*);
%ignore Fl_Menu_Item::callback() const;
//%ignore Fl_Menu_Item::user_data();

%pythonappend Fl_Menu_Item::image %{
        if len(args) > 0:
            #delegate ownership to C++
            self.my_image = args[0]
            args[0].this.disown()
%}

%ignore Fl_Menu_Item::user_data(void *);
%ignore Fl_Menu_Item::user_data() const;

%include "FL/Fl_Menu_Item.H"



%extend Fl_Menu_Item {
    PyObject* callback() {
	CallbackStruct *cb = (CallbackStruct*)self->user_data_;
	PyObject *o = Py_BuildValue("O", cb->func);
	return o;
    }	

    PyObject* user_data() {
	CallbackStruct *cb = (CallbackStruct*)self->user_data_;
	PyObject *o = Py_BuildValue("O", cb->data);
	return o;
    }
  
    void add_multi_label(Fl_Pixmap* pixmap) {
      //save label text as self->image below clobbers it
      const char* itemtext= self->label();
      
      //Assign image to menu item
      self->image(*pixmap); //clobbers self->label()
      Fl_Multi_Label *ml = new Fl_Multi_Label();

      ml->typea = _FL_IMAGE_LABEL;
      ml->labela = (const char*)pixmap;
      ml->typeb = FL_NORMAL_LABEL;
      ml->labelb = itemtext;

      ml->label(self);
    }
}


%ignore Fl_Menu_Item::image(Fl_Image& a);
