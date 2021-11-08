import tornado.ioloop
import tornado.web
import ctez_collector
import ctez_chart
import threading
import time


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(ctez_collector.read_input())

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


class ThreadedClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            ctez_collector.collect()
            ctez_chart.chart()
            time.sleep(3600)


if __name__ == "__main__":

    background = ThreadedClient()
    background.start()
    print("Background process started")

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()