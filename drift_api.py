import tornado.ioloop
import tornado.web
import drift_collector
import threading
import time
import json
from datetime import datetime

def to_ts(date_strings):
    timestamps = []
    for key in date_strings:
        timestamp = datetime.timestamp(datetime.strptime(key, "%Y-%m-%d %H:%M:%S+00:00"))
        timestamps.append(int(timestamp))
    return timestamps

class ChartHandler(tornado.web.RequestHandler):
    def get(self):
        with open("outfile.json", "r+") as infile:
            input_dict = json.loads(infile.read())

        self.render("chart.html",
                    keys=json.dumps(list(input_dict.keys())),
                    values=json.dumps(list(input_dict.values()))
                    )


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(drift_collector.read_input())


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/chart", ChartHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


class ThreadedClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            drift_collector.collect()
            time.sleep(3600)


if __name__ == "__main__":
    background = ThreadedClient()
    background.start()
    print("Background process started")

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
