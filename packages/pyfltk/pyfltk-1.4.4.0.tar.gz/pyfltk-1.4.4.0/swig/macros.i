%include <std_string.i>
%include <typemaps.i>

// macro to delegate the ownership of a class to C++
%define CHANGE_OWNERSHIP(name)
#include "CallbackStruct.h"
%pythonappend name##::##name %{
if len(args) == 5:          
    # retain reference to label
    self.my_label = args[-1]
if self.parent() != None:   
    # delegate ownership to C++
    self.this.disown()
self.init_type("name")
#print("Adding type: ", name)
%}
%extend name {
  void init_type(char* name) {
    CallbackStruct *cb = new CallbackStruct( 0, 0, 0, 0 );
    memcpy(cb->type_name, name, strlen(name));
    self->user_data(cb);
  }
 }
%enddef

// macro to revert the ownership
%define REVERT_OWNERSHIP(name)
%pythonappend name %{
#self = args[0]
if self.parent() != None:   
    #delegate ownership to C++
    self.this.disown()
else:                       
    #give ownership back to Python
    self.this.own() 
%}
%enddef

%define DEFINE_CALLBACK(name)
#include "CallbackStruct.h"
%{
#include "CallbackStruct.h"
#include <FL/Fl_Button.H>

  //static PyObject *my_pycallback = NULL;
  static void name ## _PythonCallBack(name *widget, void *clientdata)
    {
      PyObject *func, *arglist;
      PyObject *result;
      PyObject *obj = 0;
      CallbackStruct* cb = (CallbackStruct*)clientdata;

      // This is the function .... 
      func = cb->func;

      if (cb->widget != 0) {
        // the parent widget
        obj = (PyObject *)( ((CallbackStruct *)clientdata)->widget);
      }
      else if (cb->type != 0) {
        // this is the type of widget
        swig_type_info *descr = (swig_type_info *)cb->type;
        if (descr != 0) {
          //printf("success\n");
          obj = SWIG_NewPointerObj(widget, (swig_type_info *)descr, 0);
        }
      }
      if (obj == 0) {
        // generic fallback
        obj = SWIG_NewPointerObj(widget, SWIGTYPE_p_ ## name, 0);
      }

      if (((CallbackStruct *)clientdata)->data)
	{
	  arglist = Py_BuildValue("(OO)", obj, (PyObject *)(((CallbackStruct *)clientdata)->data) ); 
	}
      else
	{
	  arglist = Py_BuildValue("(O)", obj ); 
	}

      result =  PyObject_CallObject(func, arglist);
   
      //Py_XDECREF(arglist);                           // Trash arglist
      Py_XDECREF(result);
      PyObject *error = PyErr_Occurred();
      {
	if (error != NULL) {
	  throw Swig::DirectorMethodException();
	}
      }
      //if (PyErr_Occurred())
      //{
      //  PyErr_Print();
      //}
   
      return /*void*/;
    }
  %}
%enddef

%define ADD_CALLBACK(name)

%extend name {
  void
    callback(PyObject *PyFunc, PyObject *PyWidget, PyObject *PyData = 0)
    {
      //CallbackStruct *cb = 0;
      CallbackStruct *cb = (CallbackStruct*)self->user_data();

      if (cb) {
	cb->func = PyFunc;
	cb->widget = PyWidget;
	if (PyData) {
	  cb->data = PyData;
	}
	cb->widget = PyWidget;
      }
      else
	cb = new CallbackStruct( PyFunc, PyData, PyWidget );

      // Add a reference to new callback
      Py_INCREF(PyFunc);			
      Py_XINCREF(PyData);
      Py_XINCREF(PyWidget);

      self->callback(name ## _PythonCallBack, (void *)cb);

    
    }
}
%enddef


%define ADD_USERDATA(name)
#include "CallbackStruct.h"
%extend name {
   void
    user_data(PyObject *PyData)
    {
      // Add a reference to new callback
      Py_XINCREF(PyData);
	
      CallbackStruct *cb = (CallbackStruct*)self->user_data();
      if (cb == NULL) {
	cb = new CallbackStruct(0, PyData, (PyObject*)0);
	self->user_data((void *)cb);
      }
      else {
	if (cb->data != NULL)
	  Py_XDECREF(cb->data);
	cb->data = PyData;
      }
    
    }

  PyObject* user_data() {
    PyObject *obj = 0;
    CallbackStruct *cb = (CallbackStruct*)self->user_data();
    if (cb) {
      if (cb->data) {
	obj = (PyObject*)cb->data;

	Py_XINCREF(obj);
	return obj;
      }
    }
    // nothing found
    Py_RETURN_NONE;
  }
}
%enddef
