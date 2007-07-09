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
#############################
# Variables:                #
#############################

# Folder, where the existing *.ics files are. The trailing slash is neccessary. This directory (and its files) must be readable for the user which runs this script
CALDIR = '/var/www/calendar/calendars/'

# Name (and path) where the merged ics-file should be written. This directory and file must be writeable for the user which runs this script
ICS_OUT = '/var/www/calendar/the_merged_file.ics'

# Name of this tool
MY_NAME = 'My Calendarmerger'

# Our domain (This and MY_NAME will be printed into the new ics, as 'generator' ;) )
MY_DOMAIN = 'default.com'

# a short, one word name for this tool, used in errormessages as identifier
MY_SHORTNAME = 'merge_ics.py'

# The Timezone for the new file. This is here, becaus Mozilla Sunbird 0.5 want it ;). It's the general Timezone of the file. Normaly, an entry has it one timezone.
OUR_TIMEZONE = 'Europe/Zurich'

# Name of the new calendar
CALENDARNAME = 'My new calendar'

# do we need logging?
DEBUG = True

# if DEBUG=True, where to log the data? (note: logfile (if it already exists) or directory must be writable by the user which runs this script)
DEBUGFILE = '/var/log/merge_ics.log'

#############################
# Script:                   #
#############################

# We need some stuff
import glob, sys
from time import *

DEBUGMSG = 'Log started\n'

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
