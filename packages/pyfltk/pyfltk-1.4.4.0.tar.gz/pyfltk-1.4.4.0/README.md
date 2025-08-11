pyFLTK:
=======

A Python Wrapper for the FLTK library
-------------------------------------

GOALS:

* To wrap FLTK1.4 in Python 
* To port all programs in test/ to Python using pyFLTK
 

If you'd like to help out, I'd suggest using the pyfltk mailing list
(at the bottom) to coordinate who's working on what. 

1) This wrapper requires:

* SWIG 4.0 or later
* Python 3.8 or later
* Fast Light Toolkit 1.4 or later 

2) Restrictions

At present, the Python wrapper has been ported and is quite stable. You might encounter certain parts that are not yet or only partailly wrapped.

   

3) The wrapper is available on PyPi: https://pypi.org/project/pyfltk/

4) see INSTALL file for instructions how to build or install the Python wrapper of FLTK
   
5) Do the following to run some tests:
	
	cd fltk/test
	
	python hello.py
    or
    	python3 hello.py (depending on your platform)


* ./test contains demo programs from the FLTK distribution reimplemented
  in Python.
* You can run ./test/demos.py for a little
  menu of the demos



### On the web:

pyFLTK home page: http://pyfltk.sourceforge.io


### License:

pyFLTK Copyright (C) 2003-2025 Andreas Held and others licensed under the
GNU Library General Public License, version 2.0, June 1991 

This library is free software you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License, version 2.0 as published by the Free Software Foundation.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with this library if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA.


### Leads:

Andreas Held  andreasheld[at]users.sourceforge.net

Robert Arkiletian



### Mailing List:

http://lists.sourceforge.net/lists/listinfo/pyfltk-user


### Thanks:

Especial thanks to Kevin Dalhausen, the originator of pyFLTK. He did
such a good job, the rest was easy.

Many thanks to the creators of fltk (www.fltk.org), the best, fastest
and lightest toolkit there is!

Finally, not to forget the creators of SWIG (www.swig.org) a unique
tool for doing what we've done here.












