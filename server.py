import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.gen
from tornado.options import define, options
import time
import multiprocessing

define("port", default=8080, help="run on the given port", type=int)
l = 0
clients = []

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('test.html')
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200
    
    def open(self):
        global l
        print ('new connection')
        WebSocketHandler.waiters.add(self)
        self.write_message(str(l))

    def on_message(self, message):
        global l
        print ('tornado received from client: %s' % message)
        l = l + int(message)
        WebSocketHandler.send_updates(str(l))

    @classmethod
    def send_updates(cls, message):
        for waiter in cls.waiters:
            waiter.write_message(message)

    def on_close(self):
        print ('connection closed')
        WebSocketHandler.waiters.remove(self)
 
################################ MAIN ################################
 
def main():
 
    taskQ = multiprocessing.Queue()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", WebSocketHandler)
        ], queue=taskQ
    )
    httpServer = tornado.httpserver.HTTPServer(app)
    httpServer.listen(options.port)
    print ("Listening on port:", options.port)
 
    mainLoop = tornado.ioloop.IOLoop.instance()
    mainLoop.start()
 
if __name__ == "__main__":
    main()