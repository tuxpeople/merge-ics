#!/usr/bin/python
#
#   merge_ics.py:   This script will get all .ics files (iCalendar files, as
#                   specified in the RFC 2445 specification), read it and
#                   aggregate all events to a new .ics file. If one of the
#                   sourcefiles is not readable (or is not RFC 2445 compatible),
#                   it will be ignored.
#
#   Copyright:      (C) 2007 by Thomas Deutsch <thomas@tuxpeople.org>
#
#   Version:        1.7(2007-05-28)
#
#   License:        GPL v2
#
#                   This program is free software; you can redistribute it and/or modify
#                   it under the terms of the GNU General Public License as published by
#                   the Free Software Foundation; either version 2 of the License, or
#                   (at your option) any later version.
#
#                   This program is distributed in the hope that it will be useful, but
#                   WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#                   or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
#                   for more details.
#
#                   You should have received a copy of the GNU General Public License along
#                   with this program; if not, write to the Free Software Foundation, Inc.,
#                   51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#
#   Usage:          This script is made to be started by hand or as a cronjob.
#                   It needs no parameters or options, but you should configure
#                   the variables in the script before you run it ;)
#

# Where is the configuration?
CONF = '/etc/merge_ics.cfg'

#############################
# Script:                   #
#############################

DEBUGMSG = 'Log started\n'

# Read the config
DEBUGMSG += 'try to read config\n'
try:
    execfile(CONF)
except:
    print MY_SHORTNAME + ': Error, unable to read config: ', sys.exc_info()[1]

# imports
import glob, sys, datetime

DEBUGMSG += 'start init\n'

now = datetime.datetime.now()
DEBUGMSG += now.strftime('now: %Y/%m/%d - %H:%M:%S') + '\n'
# limit
limitdate = now - datetime.timedelta(days=HISTORY_DAYS)
limit = limitdate.strftime('%Y%m%d')
if HISTORY_DAYS > 0:
    DEBUGMSG += '- ignore events before ' + limitdate.strftime('%Y/%m/%d') + '\n'
# this set will be used fo find duplicate events
eventSet = set()
if IGNORE_DUPLICATE:
    DEBUGMSG += '- ignore duplicated events\n'
DEBUGMSG += 'init done\n'

# We need the iCalendar package from http://codespeak.net/icalendar/
from icalendar import Calendar, Event, Timezone

# Open the new calendarfile and adding the information about this script to it
newcal = Calendar()
newcal.add('prodid', '-//' + MY_NAME + '//' + MY_DOMAIN + '//')
newcal.add('version', '2.0')
newcal.add('x-wr-calname', CALENDARNAME)
DEBUGMSG += 'new calendar ' + ICS_OUT + ' started\n'

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
        DEBUGMSG += 'reading file ' + s + '\n'
        # every part of the file...
        for component in cal.subcomponents:
            # ...which name is VEVENT will be added to the new file
            if component.name == 'VEVENT':
                try:
                    if HISTORY_DAYS > 0:
                        eventStart = component.decoded('dtstart').strftime('%Y%m%d')
                        if eventStart < limit:
                            DEBUGMSG += '  skipped historic event: ' + eventStart + ' is before ' + limit + '\n'
                            continue
                    if IGNORE_DUPLICATE:
                        eventId = str(component['dtstart']) + ' | ' + str(component['dtend']) + ' | ' + str(component['summary'])
                        if eventId not in eventSet:
                            eventSet.add(eventId)
                        else:
                            DEBUGMSG += '  skipped duplicated event: ' + eventId + '\n'
                            continue
                except:
                    # ignore events with missing dtstart, dtend or summary
                    continue
                newcal.add_component(component)
        # close the existing file
        calfile.close()
    except:
        # if the file was not readable, we need a errormessage ;)
        print MY_SHORTNAME + ': Error: reading file:', sys.exc_info()[1]
        print s


# After the loop, we have all of our data and can write the file now
try:
    f = open(ICS_OUT, 'wb')
    f.write(newcal.as_string())
    f.close()
    DEBUGMSG += 'new calendar written\n'
except:
    print MY_SHORTNAME + ': Error: ', sys.exc_info()[1]

if DEBUG == True:
    try:
        l = open(DEBUGFILE, 'wb')
        l.write(DEBUGMSG)
        l.close()
    except:
        print MY_SHORTNAME + ': Error, unable to write log: ', sys.exc_info()[1]
# all done...
