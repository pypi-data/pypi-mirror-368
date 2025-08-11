/* File : Fl_Input.i */
//%module Fl_Input

%feature("docstring") ::Fl_Input
"""
This is the FLTK text input widget. It displays a single line of text and 
lets the user edit it. Normally it is drawn with an inset box and a white 
background. The text may contain any characters (even 0), and will correctly 
display anything, using ^X notation for unprintable control characters 
and \nnn notation for unprintable characters with the high bit set. It 
assumes the font can draw any characters in the ISO-8859-1 character set.
Mouse button 1	Moves the cursor to this point. Drag selects characters. 
Double click selects words. Triple click selects all text. Shift+click 
extends the selection. When you select text it is automatically copied 
to the clipboard.
Mouse button 2	Insert the clipboard at the point clicked. You can also 
select a region and replace it with the clipboard by selecting the region 
with mouse button 2.
Mouse button 3	Currently acts like button 1.
Backspace	Deletes one character to the left, or deletes the selected 
region.
Enter	May cause the callback, see when().
^A or Home	Go to start of line.
^B or Left	Move left
^C	Copy the selection to the clipboard
^D or Delete	Deletes one character to the right or deletes the selected 
region.
^E or End	Go to the end of line.
^F or Right	Move right
^K	Delete to the end of line (next \n character) or deletes a single \n 
character. These deletions are all concatenated into the clipboard.
^N or Down	Move down (for Fl_Multiline_Input only, otherwise it moves
to the next input field).
^P or Up	Move up (for Fl_Multiline_Input only, otherwise it moves to 
the previous input field).
^U	Delete everything.
^V or ^Y	Paste the clipboard
^X or ^W	Copy the region to the clipboard and delete it.
^Z or ^_	Undo. This is a single-level undo mechanism, but all adjacent 
deletions and insertions are concatenated into a single 'undo'. Often this 
will undo a lot more than you expected.
Shift+move	Move the cursor but also extend the selection.
RightCtrl or
Compose	Start a compose-character sequence. The next one or two keys typed 
define the character to insert (see table that follows.)

The character 'nbsp' (non-breaking space) is typed by using [compose][space].

The single-character sequences may be followed by a space if necessary to 
remove ambiguity. 

The same key may be used to 'quote' control characters into the text. If you 
need a ^Q character you can get one by typing [compose][Control+Q].

X may have a key on the keyboard defined as XK_Multi_key. If so this key 
may be used as well as the right-hand control key. You can set this up 
with the program xmodmap.

If your keyboard is set to support a foreign language you should also be 
able to type 'dead key' prefix characters. On X you will actually be able 
to see what dead key you typed, and if you then move the cursor without 
completing the sequence the accent will remain inserted. 
""" ;

%{
#include "FL/Fl_Input.H"
%}

%include "macros.i"

CHANGE_OWNERSHIP(Fl_Input)

%include "FL/Fl_Input.H"
