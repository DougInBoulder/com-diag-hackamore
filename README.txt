Copyright 2014 Digital Aggregates Corporation, Colorado, USA.

----------------------------------------------------------------------

LICENSE

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

As a special exception, if other files instantiate templates or
use macros or inline functions from this file, or you compile
this file and link it with other works to produce a work based on
this file, this file does not by itself cause the resulting work
to be covered by the GNU Lesser General Public License. However
the source code for this file must still be made available in
accordance with the GNU Lesser General Public License.

This exception does not invalidate any other reasons why a work
based on this file might be covered by the GNU Lesser General
Public License.

Alternative commercial licensing terms are available from the copyright
holder. Contact Digital Aggregates Corporation for more information.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, contact

    Free Software Foundation, Inc.
    59 Temple Place, Suite 330
    Boston MA 02111-1307 USA
    http://www.gnu.org/copyleft/lesser.txt

----------------------------------------------------------------------

ABSTRACT

This is the Digital Aggregates Corporation Hackamore package. Hackamore is a
framework and application written in Python that maintains a dynamic model of
the call states of one or more Asterisk PBXes using the Asterisk Management
Interface (AMI). It was inspired by prior work done in C by Mark Jackson at
Aircell Business Aviation Services LLC. Hackamore is a work in progress.
This software is an original work of its author.

If you want to run any of the unit tests that execute against a live Asterisk
server, those unit tests need to know your server's hostname or IP address, AMI
port (if not 5038), and the username and secret that you administered in your

    /etc/asterisk/manager.conf

file. You can either define these in your environment as the values of the
variables
    
    COM_DIAG_HACKAMORE_SERVER,
    COM_DIAG_HACKAMORE_PORT,
    COM_DIAG_HACKAMORE_USERNAME, and
    COM_DIAG_HACKAMORE_SECRET
    
respectively, or you can define them in a file in your home directory named

    .com_diag_hackamore

and the unit tests will extract them from successive lines encoded in

    keyword=value
    
form where the keywords are the same as the environmental variable names above.
Note that this capability is not part of the unit test modules but part of the
Hackamore framework itself. So you can use this capability in your own Hackamore
application instead of embedding this sensitive information in your Python
program or in your Eclipse project metadata. If the value of the variable
COM_DIAG_HACKAMORE_SERVER is not defined or is an empty string, the unit tests
which run against a live server will automatically be bypassed.

Similarly, there are prototype Hackamore main programs that extracts the same
information for one or more Asterisk servers from the same dotfile in your home
directory. The dotfile would contains lines of the form shown in the examples
below.

    COM_DIAG_HACKAMORE_NAME1=PBX1
    COM_DIAG_HACKAMORE_SERVER1=pbx1.mydomain.com
    COM_DIAG_HACKAMORE_PORT1=5038
    COM_DIAG_HACKAMORE_USERNAME1=admin
    COM_DIAG_HACKAMORE_SECRET1=password
    COM_DIAG_HACKAMORE_NAME2=PBX2
    COM_DIAG_HACKAMORE_SERVER2=pbx2.mydomain.com
    COM_DIAG_HACKAMORE_PORT2=5038
    COM_DIAG_HACKAMORE_USERNAME2=admin
    COM_DIAG_HACKAMORE_SECRET2=password

The two main programs are

    src/com/diag/hackamore/Main, and
    src/com/diag/hackamore/Mains

in which Main is single threaded, multiplexes the AMI sockets using the
select(2) system call, and updates a common model, and Mains is multi-threaded,
processes each AMI socket from a different thread, and updates a common model
by serializing access to it.

----------------------------------------------------------------------

CONTACT

Chip Overclock
mailto:coverclock@diag.com
Digital Aggregates Corporation
3440 Youngfield Street, Suite 209
Wheat Ridge CO 80033 USA
http://www.diag.com
