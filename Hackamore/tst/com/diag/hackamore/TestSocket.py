"""
@file
Copyright 2014 by the Digital Aggregates Corporation, Colorado, USA.
Licensed under the terms in the README.txt file.
"""

import unittest
import logging
import socket
import threading

import com.diag.hackamore.Logger
import com.diag.hackamore.Socket
import com.diag.hackamore.End
import com.diag.hackamore.Multiplex

from Parameters import SERVER
from Parameters import PORT
from Parameters import USERNAME
from Parameters import SECRET
from Parameters import LOCALHOST
from Parameters import SAMPLE
from Parameters import TYPESCRIPT

address = ""
port = 0
ready = threading.Condition()

proceed = False
complete = False
done = threading.Condition()

class Refuser(threading.Thread):
    
    def run(self):
        global address
        global port
        global ready
        global complete
        global done
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(("", 0))
        with ready:
            address, port2 = sock.getsockname()
            print("Refuser=" + str(port2))
            sock.close()
            port = port2
            ready.notifyAll()
        with done:
            while not complete:
                done.wait()

class Binder(threading.Thread):
    
    def run(self):
        global address
        global port
        global ready
        global complete
        global done
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(("", 0))
        with ready:
            address, port = sock.getsockname()
            print("Binder=" + str(port))
            ready.notifyAll()
        with done:
            while not complete:
                done.wait()
        sock.close()

class Listener(threading.Thread):
    
    def run(self):
        global address
        global port
        global ready
        global complete
        global done
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(("", 0))
        sock.listen(socket.SOMAXCONN)
        with ready:
            address, port = sock.getsockname()
            print("Listener=" + str(port))
            ready.notifyAll()
        with done:
            while not complete:
                done.wait()
        sock.close()

class Accepter(threading.Thread):
    
    def run(self):
        global address
        global port
        global ready
        global complete
        global done
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(("", 0))
        sock.listen(socket.SOMAXCONN)
        with ready:
            address, port = sock.getsockname()
            print("Accepter=" + str(port))
            ready.notifyAll()
        sock2, client = sock.accept()
        print("Requester=" + str(client))
        with done:
            while not complete:
                done.wait()
        sock2.close()
        sock.close()

class Producer(threading.Thread):
    
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path
    
    def run(self):
        global address
        global port
        global ready
        global complete
        global done
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(("", 0))
        sock.listen(socket.SOMAXCONN)
        with ready:
            address, port = sock.getsockname()
            print("Producer=" + str(port))
            ready.notifyAll()
        sock2, consumer = sock.accept()
        print("Consumer=" + str(consumer))
        stream = open(self.path, "r")
        if stream != None:
            while True:
                line = stream.readline(512)
                if line == None:
                    break
                elif not line:
                    break
                else:
                    sock2.sendall(line)
        stream.close()
        sock2.close()
        with done:
            while not complete:
                done.wait()
        sock.close()

class Server(threading.Thread):
    
    def __init__(self, path):
        threading.Thread.__init__(self)
        self.path = path
    
    def run(self):
        global address
        global port
        global ready
        global proceed
        global complete
        global done
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.bind(("", 0))
        sock.listen(socket.SOMAXCONN)
        with ready:
            address, port = sock.getsockname()
            print("Server=" + str(port))
            ready.notifyAll()
        while True:
            with done:
                while not proceed and not complete:
                    done.wait()
                if complete:
                    break
                proceed = False
            sock2, consumer = sock.accept()
            print("Client=" + str(consumer))
            stream = open(self.path, "r")
            if stream != None:
                while True:
                    line = stream.readline(512)
                    if line == None:
                        break
                    elif not line:
                        break
                    else:
                        sock2.sendall(line)
            stream.close()
            sock2.close()
        sock.close()

class Test(unittest.TestCase):

    def setUp(self):
        com.diag.hackamore.Logger.logger().setLevel(logging.DEBUG)

    def tearDown(self):
        pass
    
    def test010Assemble(self):
        source = com.diag.hackamore.Socket.Socket("", "", "", "", 0)
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 0)
        self.assertTrue(len(source.queue) == 0)
        source.assemble("OneOne: ")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 0)
        source.assemble("AlphaAlpha")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 2)
        self.assertTrue(len(source.queue) == 0)
        source.assemble("\r\n")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 1)
        source.assemble("OneTwo: ")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 2)
        self.assertTrue(len(source.queue) == 1)
        source.assemble("AlphaBeta\r\n")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 2)
        source.assemble("OneThree: AlphaGamma\r\n")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 3)
        source.assemble("OneFour: AlphaDelta\r")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 20)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 3)
        source.assemble("\nOneFive: AlphaEpsilon\r\n")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 5)        
        source.assemble("\r\n")
        print("PREFIX=\"" + str(source.prefix) + "\"")
        print("PARTIAL=" + str(source.partial))
        print("QUEUE=" + str(source.queue))
        self.assertTrue(len(source.prefix) == 0)
        self.assertTrue(len(source.partial) == 1)
        self.assertTrue(len(source.queue) == 6)
        event = source.get()
        print("EVENT=" + str(event))
        self.assertIn("OneOne", event)
        self.assertTrue(event["OneOne"] == "AlphaAlpha")
        self.assertIn("OneTwo", event)
        self.assertTrue(event["OneTwo"] == "AlphaBeta")
        self.assertIn("OneThree", event)
        self.assertTrue(event["OneThree"] == "AlphaGamma")
        self.assertIn("OneFour", event)
        self.assertTrue(event["OneFour"] == "AlphaDelta")
        self.assertIn("OneFive", event)
        self.assertTrue(event["OneFive"] == "AlphaEpsilon")
        
    def test020Construction(self):
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, SERVER, PORT)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == SERVER)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == PORT)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)

    def test030Refuser(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Refuser()
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertFalse(source.open())
        self.assertTrue(source.socket == None)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        try:
            line = source.read()
        except Exception:
            self.fail()
        else:
            self.assertTrue(line == None)
        finally:
            pass
        self.assertFalse(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
        
    def test040Binder(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Binder()
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertFalse(source.open())
        self.assertTrue(source.socket == None)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        try:
            line = source.read()
        except Exception:
            self.fail()
        else:
            self.assertTrue(line == None)
        finally:
            pass
        self.assertFalse(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
        
    def test050Listener(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Listener()
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        try:
            line = source.read()
        except Exception:
            pass
        else:
            self.assertTrue(line == None)
        finally:
            pass
        self.assertTrue(source.close())
        self.assertFalse(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()

    def test060Accepter(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Accepter()
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        try:
            line = source.read()
        except Exception:
            pass
        else:
            self.assertTrue(line == None)
        finally:
            pass
        self.assertTrue(source.close())
        self.assertFalse(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()

    def test070Read(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Producer(SAMPLE)
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        lines = 0
        eof = False
        while not eof:
            try:
                line = source.read()
            except com.diag.hackamore.End.End:
                eof = True
            else:
                if line == None:
                    continue
                lines = lines + 1
                if lines == 1:
                    self.assertTrue(line == "OneOne: AlphaAlpha")
                elif lines == 2:
                    self.assertTrue(line == "OneTwo: AlphaBeta")
                elif lines == 3:
                    self.assertTrue(line == "OneThree: AlphaGamma")
                elif lines == 4:
                    self.assertTrue(line == "")
                elif lines == 5:
                    self.assertTrue(line == "TwoOne: BetaAlpha")
                elif lines == 6:
                    self.assertTrue(line == "TwoTwo: BetaBeta")
                elif lines == 7:
                    self.assertTrue(line == "")
                elif lines == 8:
                    self.assertTrue(line == "ThreeOne: GammaAlpha")
                elif lines == 9:
                    self.assertTrue(line == "ThreeTwo: GammaBeta")
                elif lines == 10:
                    self.assertTrue(line == "ThreeThree: GammaGamma")
                elif lines == 11:
                    self.assertTrue(line == "")
                elif lines == 12:
                    self.assertTrue(line == "FourOne: DeltaAlpha")
                elif lines == 13:
                    self.assertTrue(line == "")
                else:
                    self.assertTrue(0 < lines < 13)
            finally:
                pass
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
        
    def test080Get(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Producer(SAMPLE)
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        events = 0
        eof = False
        while not eof:
            event = source.get()
            if event == None:
                continue
            events = events + 1
            self.assertTrue(event)
            if events == 1:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("OneOne" in event)
                self.assertTrue(event["OneOne"] == "AlphaAlpha")
                self.assertTrue("OneTwo" in event)
                self.assertTrue(event["OneTwo"] == "AlphaBeta")
                self.assertTrue("OneThree" in event)
                self.assertTrue(event["OneThree"] == "AlphaGamma")
            elif events == 2:
                self.assertTrue(len(event) == 4)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("TwoOne" in event)
                self.assertTrue(event["TwoOne"] == "BetaAlpha")
                self.assertTrue("TwoTwo" in event)
                self.assertTrue(event["TwoTwo"] == "BetaBeta")
            elif events == 3:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("ThreeOne" in event)
                self.assertTrue(event["ThreeOne"] == "GammaAlpha")
                self.assertTrue("ThreeTwo" in event)
                self.assertTrue(event["ThreeTwo"] == "GammaBeta")
                self.assertTrue("ThreeThree" in event)
                self.assertTrue(event["ThreeThree"] == "GammaGamma")
            elif events == 4:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("FourOne" in event)
                self.assertTrue(event["FourOne"] == "DeltaAlpha")
            elif events == 5:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertTrue(com.diag.hackamore.Source.END in event)
                self.assertTrue(event[com.diag.hackamore.Source.END] == str(5))
            else:
                self.assertTrue(0 < events < 6)
            if com.diag.hackamore.Source.END in event:
                eof = True
        self.assertTrue(events == 5)
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
        
    def test085Service(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Producer(SAMPLE)
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        events = 0
        eof = False
        while not eof:
            com.diag.hackamore.Multiplex.service()
            event = source.get(True)
            if event == None:
                continue
            events = events + 1
            self.assertTrue(event)
            if events == 1:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("OneOne" in event)
                self.assertTrue(event["OneOne"] == "AlphaAlpha")
                self.assertTrue("OneTwo" in event)
                self.assertTrue(event["OneTwo"] == "AlphaBeta")
                self.assertTrue("OneThree" in event)
                self.assertTrue(event["OneThree"] == "AlphaGamma")
            elif events == 2:
                self.assertTrue(len(event) == 4)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("TwoOne" in event)
                self.assertTrue(event["TwoOne"] == "BetaAlpha")
                self.assertTrue("TwoTwo" in event)
                self.assertTrue(event["TwoTwo"] == "BetaBeta")
            elif events == 3:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("ThreeOne" in event)
                self.assertTrue(event["ThreeOne"] == "GammaAlpha")
                self.assertTrue("ThreeTwo" in event)
                self.assertTrue(event["ThreeTwo"] == "GammaBeta")
                self.assertTrue("ThreeThree" in event)
                self.assertTrue(event["ThreeThree"] == "GammaGamma")
            elif events == 4:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("FourOne" in event)
                self.assertTrue(event["FourOne"] == "DeltaAlpha")
            elif events == 5:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertTrue(com.diag.hackamore.Source.END in event)
                self.assertTrue(event[com.diag.hackamore.Source.END] == str(5))
            else:
                self.assertTrue(0 < events < 6)
            if com.diag.hackamore.Source.END in event:
                eof = True
        self.assertTrue(events == 5)
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
    
    def test090Multiplex(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Producer(SAMPLE)
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        events = 0
        for event in com.diag.hackamore.Multiplex.multiplex():
            self.assertFalse(event == None)
            events = events + 1
            self.assertTrue(event)
            if events == 1:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("OneOne" in event)
                self.assertTrue(event["OneOne"] == "AlphaAlpha")
                self.assertTrue("OneTwo" in event)
                self.assertTrue(event["OneTwo"] == "AlphaBeta")
                self.assertTrue("OneThree" in event)
                self.assertTrue(event["OneThree"] == "AlphaGamma")
            elif events == 2:
                self.assertTrue(len(event) == 4)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("TwoOne" in event)
                self.assertTrue(event["TwoOne"] == "BetaAlpha")
                self.assertTrue("TwoTwo" in event)
                self.assertTrue(event["TwoTwo"] == "BetaBeta")
            elif events == 3:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("ThreeOne" in event)
                self.assertTrue(event["ThreeOne"] == "GammaAlpha")
                self.assertTrue("ThreeTwo" in event)
                self.assertTrue(event["ThreeTwo"] == "GammaBeta")
                self.assertTrue("ThreeThree" in event)
                self.assertTrue(event["ThreeThree"] == "GammaGamma")
            elif events == 4:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("FourOne" in event)
                self.assertTrue(event["FourOne"] == "DeltaAlpha")
            elif events == 5:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertTrue(com.diag.hackamore.Source.END in event)
                self.assertTrue(event[com.diag.hackamore.Source.END] == str(5))
            else:
                self.assertTrue(0 < events < 6)
            if com.diag.hackamore.Source.END in event:
                break
        self.assertTrue(events == 5)
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
        
    def test100Client(self):
        global address
        global port
        global ready
        global proceed
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        proceed = False
        complete = False
        thread = Server(SAMPLE)
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            proceed = True
            done.notifyAll()
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        events = 0
        eof = False
        while not eof:
            event = source.get()
            if event == None:
                continue
            events = events + 1
            self.assertTrue(event)
            if events == 1:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("OneOne" in event)
                self.assertTrue(event["OneOne"] == "AlphaAlpha")
                self.assertTrue("OneTwo" in event)
                self.assertTrue(event["OneTwo"] == "AlphaBeta")
                self.assertTrue("OneThree" in event)
                self.assertTrue(event["OneThree"] == "AlphaGamma")
            elif events == 2:
                self.assertTrue(len(event) == 4)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("TwoOne" in event)
                self.assertTrue(event["TwoOne"] == "BetaAlpha")
                self.assertTrue("TwoTwo" in event)
                self.assertTrue(event["TwoTwo"] == "BetaBeta")
            elif events == 3:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("ThreeOne" in event)
                self.assertTrue(event["ThreeOne"] == "GammaAlpha")
                self.assertTrue("ThreeTwo" in event)
                self.assertTrue(event["ThreeTwo"] == "GammaBeta")
                self.assertTrue("ThreeThree" in event)
                self.assertTrue(event["ThreeThree"] == "GammaGamma")
            elif events == 4:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("FourOne" in event)
                self.assertTrue(event["FourOne"] == "DeltaAlpha")
            elif events == 5:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertTrue(com.diag.hackamore.Source.END in event)
                self.assertTrue(event[com.diag.hackamore.Source.END] == str(5))
            else:
                self.assertTrue(0 < events < 6)
            if com.diag.hackamore.Source.END in event:
                eof = True
        self.assertTrue(events == 5)
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)        
        with done:
            proceed = True
            done.notifyAll()
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        events = 0
        eof = False
        while not eof:
            event = source.get()
            if event == None:
                continue
            events = events + 1
            self.assertTrue(event)
            if events == 1:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("OneOne" in event)
                self.assertTrue(event["OneOne"] == "AlphaAlpha")
                self.assertTrue("OneTwo" in event)
                self.assertTrue(event["OneTwo"] == "AlphaBeta")
                self.assertTrue("OneThree" in event)
                self.assertTrue(event["OneThree"] == "AlphaGamma")
            elif events == 2:
                self.assertTrue(len(event) == 4)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("TwoOne" in event)
                self.assertTrue(event["TwoOne"] == "BetaAlpha")
                self.assertTrue("TwoTwo" in event)
                self.assertTrue(event["TwoTwo"] == "BetaBeta")
            elif events == 3:
                self.assertTrue(len(event) == 5)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("ThreeOne" in event)
                self.assertTrue(event["ThreeOne"] == "GammaAlpha")
                self.assertTrue("ThreeTwo" in event)
                self.assertTrue(event["ThreeTwo"] == "GammaBeta")
                self.assertTrue("ThreeThree" in event)
                self.assertTrue(event["ThreeThree"] == "GammaGamma")
            elif events == 4:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertFalse(com.diag.hackamore.Source.END in event)
                self.assertTrue("FourOne" in event)
                self.assertTrue(event["FourOne"] == "DeltaAlpha")
            elif events == 5:
                self.assertTrue(len(event) == 3)
                self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
                self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
                self.assertTrue(com.diag.hackamore.Source.TIME in event)
                self.assertTrue(event[com.diag.hackamore.Source.TIME])
                self.assertTrue(com.diag.hackamore.Source.END in event)
                self.assertTrue(event[com.diag.hackamore.Source.END] == str(5))
            else:
                self.assertTrue(0 < events < 6)
            if com.diag.hackamore.Source.END in event:
                eof = True
        self.assertTrue(events == 5)
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
    
    def test110Typescript(self):
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        port = 0
        complete = False
        thread = Producer(TYPESCRIPT)
        thread.start()
        with ready:
            while port == 0:
                ready.wait()
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, LOCALHOST, port)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == LOCALHOST)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == port)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        events = 0
        for event in com.diag.hackamore.Multiplex.multiplex():
            self.assertFalse(event == None)
            events = events + 1
            self.assertTrue(event)
            self.assertTrue(com.diag.hackamore.Source.SOURCE in event)
            self.assertTrue(event[com.diag.hackamore.Source.SOURCE] == name)
            self.assertTrue(com.diag.hackamore.Source.TIME in event)
            self.assertTrue(event[com.diag.hackamore.Source.TIME])
            #del event[com.diag.hackamore.Source.TIME]; sorted(event, key=event.get); print("EVENT " + str(events) + " " + str(event))
            if com.diag.hackamore.Source.END in event:
                self.assertTrue(event[com.diag.hackamore.Source.END] == str(events))
                break
        self.assertTrue(events == 358) # 1 response, 356 events, 1 end
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        with done:
            complete = True
            done.notifyAll()
        thread.join()
    
    def test120Live(self):
        if not SERVER:
            print("Bypassing test with live server.")
            return
        global address
        global port
        global ready
        global complete
        global done
        name = self.id()
        com.diag.hackamore.Multiplex.deregister()
        self.assertFalse(name in com.diag.hackamore.Multiplex.sources)
        source = com.diag.hackamore.Socket.Socket(name, USERNAME, SECRET, SERVER, PORT)
        self.assertTrue(source != None)
        self.assertTrue(source.name != None)
        self.assertTrue(source.name == name)
        self.assertTrue(source.host != None)
        self.assertTrue(source.host == SERVER)
        self.assertTrue(source.port != None)
        self.assertTrue(source.port == PORT)
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)
        self.assertTrue(source.open())
        self.assertFalse(source.socket == None)
        self.assertTrue(source.name in com.diag.hackamore.Multiplex.sources)
        for event in com.diag.hackamore.Multiplex.multiplex():
            self.assertFalse(event == None)
            self.assertTrue(event)
            if ("Response" in event) and (event["Response"] == "Success"):
                source.logout()
            if com.diag.hackamore.Source.END in event:
                break
        self.assertTrue(source.close())
        self.assertFalse(source.name in com.diag.hackamore.Multiplex.sources)
        self.assertTrue(source.socket == None)

if __name__ == "__main__":
    unittest.main()
