"""
@file
Copyright 2014 by the Digital Aggregates Corporation, Colorado, USA.
Licensed under the terms in the README.txt file.
"""

import Logger
import Event

class View:

    #####
    ##### CTOR/DTOR
    #####

    def __init__(self, model, logger = None):
        self.logger = Logger.logger() if logger == None else logger
        self.model = model
        self.logger.info("View: INIT. %s", str(self))

    def __del__(self):
        self.logger.info("View: FINI. %s", str(self))

    def __repr__(self):
        return "View(" + str(self.model) + ")"

    #####
    ##### PUBLIC
    #####
    
    def bridge(self, pbx, uniqueid1, channel1, callerid1, uniqueid2, channel2, callerid2):
        self.logger.debug("View: EVENT: %s %s %s %s %s %s %s %s", str(Event.BRIDGE), str(pbx), str(uniqueid1), str(channel1), str(callerid1), str(uniqueid2), str(channel2), str(callerid2))

    def confbridgeend(self, pbx, conference):
        self.logger.debug("View: EVENT: %s %s %s", str(Event.CONFBRIDGEEND), str(pbx), str(conference))

    def confbridgejoin(self, pbx, uniqueid, channel, conference):
        self.logger.debug("View: EVENT: %s %s %s %s %s", str(Event.CONFBRIDGEJOIN), str(pbx), str(uniqueid), str(channel), str(conference))

    def confbridgeleave(self, pbx, uniqueid, channel, conference):        
        self.logger.debug("View: EVENT: %s %s %s %s %s", str(Event.CONFBRIDGELEAVE), str(pbx), str(uniqueid), str(channel), str(conference))

    def confbridgestart(self, pbx, conference):        
        self.logger.debug("View: EVENT: %s %s %s", str(Event.CONFBRIDGESTART), str(pbx), str(conference))

    def dial(self, pbx, uniqueid, channel, destuniqueid, destination):
        self.logger.debug("View: %s %s %s %s %s %s", str(Event.DIAL), str(pbx), str(uniqueid), str(channel), str(destuniqueid), str(destination))

    def end(self, pbx):
        self.logger.debug("View: EVENT: %s %s", str(Event.END), str(pbx))

    def hangup(self, pbx, uniqueid, channel):
        self.logger.debug("View: EVENT: %s %s %s %s", str(Event.HANGUP), str(pbx), str(uniqueid), str(channel))

    def localbridge(self, pbx, uniqueid1, channel1, uniqueid2, channel2):
        self.logger.debug("View: EVENT: %s %s %s %s %s %s", str(Event.LOCALBRIDGE), str(pbx), str(uniqueid1), str(channel1), str(uniqueid2), str(channel2))

    def newchannel(self, pbx, uniqueid, channel, calleridnum, channelstate, channelstatedesc):
        self.logger.debug("View: EVENT: %s %s %s %s %s %s %s", str(Event.NEWCHANNEL), str(pbx), str(uniqueid), str(channel), str(calleridnum), str(channelstate), str(channelstatedesc))

    def newstate(self, pbx, uniqueid, channel, channelstate, channelstatedesc):
        self.logger.debug("View: EVENT: %s %s %s %s %s %s", str(Event.NEWSTATE), str(pbx), str(uniqueid), str(channel), str(channelstate), str(channelstatedesc))

    def rename(self, pbx, uniqueid, channel, newname):
        self.logger.debug("View: EVENT: %s %s %s %s %s", str(Event.RENAME), str(pbx), str(uniqueid), str(channel), str(newname))

    def sipcallid(self, pbx, uniqueid, channel, value):
        self.logger.debug("View: EVENT: %s %s %s %s %s", str(Event.SIPCALLID), str(pbx), str(uniqueid), str(channel), str(value))

    def display(self):
        pass
