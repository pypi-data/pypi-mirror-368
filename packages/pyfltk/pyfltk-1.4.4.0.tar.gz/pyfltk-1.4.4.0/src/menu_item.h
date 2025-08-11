// This struct manages callbacks into Python.  It is stored as the
// user data portion of a widget, and the PythonCallback function is
// set as the callback.  PythonCallback unmarshalls the pointer to
// the Python function and Python user data and calls back into
// Python. 
// 

#ifndef MENU_ITEM_h
#define MENU_ITEM_h

#include <FL/Fl_Menu_Item.H>
#include <Python.h>

extern Fl_Menu_Item *createFl_Menu_Item_Array(PyObject *self, PyObject *pyMenuList);

#endif
