/* File : Fl_Plugin.i */

%feature("docstring") ::Fl_Plugin
"""
 Fl_Plugin allows link-time and run-time integration of binary modules.
 
 Fl_Plugin and Fl_Plugin_Manager provide a small and simple solution for
 linking C++ classes at run-time, or optionally linking modules at compile
 time without the need to change the main application.

 Fl_Plugin_Manager uses static initialisation to create the plugin interface
 early during startup. Plugins are stored in a temporary database, organized
 in classes.
 
 Plugins should derive a new class from Fl_Plugin as a base:
 \code
 class My_Plugin : public Fl_Plugin {
 public:
   My_Plugin() : Fl_Plugin('effects', 'blur') { }
   void do_something(...);
 };
 My_Plugin blur_plugin();
 \endcode
 
 Plugins can be put into modules and either linked befor distribution, or loaded
 from dynamically linkable files. An Fl_Plugin_Manager is used to list and 
 access all currently loaded plugins.
 \code
 Fl_Plugin_Manager mgr('effects');
 int i, n = mgr.plugins();
 for (i=0; i<n; i++) {
   My_Plugin *pin = (My_Plugin*)mgr.plugin(i);
   pin->do_something();
 }
 \endcode
""" ;

%{
#include "FL/Fl_Plugin.H"
%}

//%include "macros.i"

//CHANGE_OWNERSHIP(Fl_Plugin)

%include "FL/Fl_Plugin.H"
