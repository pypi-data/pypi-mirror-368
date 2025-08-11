/* File : Fl_Text_Buffer.i */
//%module Fl_Text_Buffer

%feature("docstring") ::Fl_Text_Buffer
"""
The Fl_Text_Buffer class is used by the Fl_Text_Display and Fl_Text_Editor 
to manage complex text data and is based upon the excellent NEdit text 
editor engine - see http://www.nedit.org/.
""" ;

%{
#include "FL/Fl_Text_Buffer.H"
%}

//ToDo
%ignore Fl_Text_Buffer::vprintf;

// deprecated in fltk-1.4
%ignore Fl_Text_Selection::position;

%{
#include "CallbackStruct.h"

struct modify_link {
  CallbackStruct *handle;
  modify_link *next;
  Fl_Text_Buffer* widget;
};

static modify_link *py_modify_funcs = NULL;

static void PythonModifyCallBack(int pos, int nInserted, int nDeleted, int nRestyled, const char* deletedText,  void* cbArg)
{
   PyObject *func, *arglist;
   PyObject *result;
   PyObject *obj;
   CallbackStruct *cb = (CallbackStruct*)cbArg;

   if (cb != NULL) {
     func = cb->func;


     // the user data
     obj = cb->data;

     if (obj == NULL) {
       arglist = Py_BuildValue("(iiiis)", pos, nInserted, nDeleted, nRestyled, deletedText );
     }
     else {
       arglist = Py_BuildValue("(iiiisO)", pos, nInserted, nDeleted, nRestyled, deletedText, obj );
     }
     result =  PyObject_CallObject(func, arglist);
     
     Py_XDECREF(arglist);                           // Trash arglist
     Py_XDECREF(result);
     if (PyErr_Occurred())
       {
	 PyErr_Print();
       }

   } 
   else
      PyErr_SetString(PyExc_TypeError, "PythonModifyCallBack: need a valid callback!");

   return;
}
%}

%apply int *OUTPUT { int* foundPos };




%include "FL/Fl_Text_Buffer.H"

%extend Fl_Text_Buffer {
  
  void add_modify_callback(PyObject *PyFunc, PyObject *PyTarget=0)
  {
  if (!PyCallable_Check(PyFunc)) 
    {
      PyErr_SetString(PyExc_TypeError, "Need a callable object!");
    }
  else
    {
      CallbackStruct *cb = new CallbackStruct( PyFunc, PyTarget, 0, 0 );
      self->add_modify_callback(PythonModifyCallBack, (void *)cb);


      Py_INCREF(PyFunc);    /* Add a reference to new callback */
      Py_XINCREF(PyTarget);

      // add it to global list and also add the widget!
      modify_link *cb_link = new modify_link;
      cb_link->next = py_modify_funcs;
      cb_link->handle = cb;
      cb_link->widget = self;
      py_modify_funcs = cb_link;
    }
  }

  void remove_modify_callback(PyObject *PyFunc, PyObject *PyWidget, PyObject *PyTarget)
  {
  // Search for the handler in the list...
  modify_link *l, *p;
  for (l = py_modify_funcs, p = 0; l && !(l->handle->func == PyFunc && (0==PyObject_RichCompareBool(l->handle->data,PyTarget, Py_EQ)) && l->widget == self); p = l, l = l->next);
  if (l) {
    // Found it, so remove it from the list...
    if (p) 
      p->next = l->next;
    else 
      py_modify_funcs = l->next;

    // remove the callback
    self->remove_modify_callback(PythonModifyCallBack, (void*)l->handle);
    
    // reference count
    Py_DECREF(l->handle->func);
    Py_XDECREF(l->handle->data);
    
    // And free the record...
    delete l->handle;
    delete l;
  }

  }
 }


%typemap(in) PyObject *PyFunc {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Need a callable object!");
      return NULL;
  }
  $1 = $input;
}

