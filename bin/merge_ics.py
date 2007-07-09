#!/usr/bin/python
#
#      merge_ics.py: This script will get all .ics files (iCalendar files, as
#                    specified in the RFC 2445 specification), read it and
#                    aggregate all events to a new .ics file. If one of the
#                    sourcefiles is not readable (or is not RFC 2445 compatible),
#                    it will be ignored.
#
#      Copyright:    (C) 2007 by Thomas Deutsch <thomas@tuxpeople.org>
#
#      Version:      1.6(2007-07-09)
#
#      License:      GPL v2
#
#                    This program is free software; you can redistribute it and/or modify
#                    it under the terms of the GNU General Public License as published by
#                    the Free Software Foundation; either version 2 of the License, or
#                    (at your option) any later version.
#
#                    This program is distributed in the hope that it will be useful, but
#                    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#                    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
#                    for more details.
#
#                    You should have received a copy of the GNU General Public License along
#                    with this program; if not, write to the Free Software Foundation, Inc.,
#                    51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA 
#
#      Usage:        This script is made to be started by hand or as a cronjob.
#                    It needs no parameters or options, but you should configure
#                    the variables in the script before you run it ;)
#

# Where is the konfiguration?
CONF = /etc/merge_ics.cfg

#############################
# Script:                   #
#############################

DEBUGMSG = 'Log started\n'

# Read the config
DEBUGMSG = DEBUGMSG + 'try to read config\n'
try:
	execfile(CONF)
except:
	print MY_SHORTNAME + ": Error, unable to read config: ", sys.exc_info()[1]

# We need some stuff
import glob, sys
from time import *

lt = localtime()
DEBUGMSG = DEBUGMSG + strftime("Tag/Monat/Jahr: %d/%m/%Y", lt) + '\n'
DEBUGMSG = DEBUGMSG + strftime("Stunde:Minute:Sekunde: %H:%M:%S", lt) + '\n'

DEBUGMSG = DEBUGMSG + 'import of glob and sys done\n'

# We need the iCalendar package from http://codespeak.net/icalendar/
from icalendar import Calendar, Event
DEBUGMSG = DEBUGMSG + 'inport of icalendar done\n'

# Open the new calendarfile and adding the information about this script to it
newcal = Calendar()
newcal.add('prodid', '-//' + MY_NAME + '//' + MY_DOMAIN + '//')
newcal.add('version', '2.0')
newcal.add('x-wr-calname', CALENDARNAME)
DEBUGMSG = DEBUGMSG + 'new calendar started\n'

# we need to add a timezone, because some clients want it (e.g. sunbird 0.5)
newtimezone = Timezone()
newtimezone.add('tzid', OUR_TIMEZONE)
newcal.add_component(newtimezone)

# Looping through the existing calendarfiles
for s in glob.glob(CALDIR + '*.ics'):
   try:
      # open the file and read it
      calfile = open(s,'rb')
      cal = Calendar.from_string(calfile.read())
      # every part of the file...
      for component in cal.subcomponents:
         if component.name == 'VEVENT':
	    # ...which name is VEVENT will be added to the new file
            newcal.add_component(component)
      # close the existing file
      DEBUGMSG = DEBUGMSG + 'done with file ' + s +'\n'
      calfile.close()
   except:
      # if the file was not readable, we need a errormessage ;)
      print MY_SHORTNAME + ": Error: reading file:", sys.exc_info()[1]
      print s

# After the loop, we have all of our data and can write the file now
try:
   f = open(ICS_OUT, 'wb')
   f.write(newcal.as_string())
   f.close()
   DEBUGMSG = DEBUGMSG + 'new calendar written\n'
except:
   print MY_SHORTNAME + ": Error: ", sys.exc_info()[1]

if DEBUG == True:
   try:
      l = open(DEBUGFILE, 'wb')
      l.write(DEBUGMSG)
      l.close()
   except:
      print MY_SHORTNAME + ": Error, unable to write log: ", sys.exc_info()[1]
# all done...
