import tornado.ioloop
import tornado.web
import drift_collector
import threading
import time
import json
from datetime import datetime


def reduce(whole, reduce_to=1000):
    """reduce number of entries in list by skipping"""
    reducer = int(len(whole) / reduce_to)
    reduced = whole[::reducer]
    return reduced


def to_ts(date_strings):
    timestamps = []
    for key in date_strings:
        timestamp = datetime.timestamp(datetime.strptime(key, "%Y-%m-%d %H:%M:%S+00:00"))
        timestamps.append(int(timestamp))
    return timestamps


class ChartHandler(tornado.web.RequestHandler):
    def get(self, data):
        chart = ChartHandler.get_argument(self, "chart")
        start = ChartHandler.get_argument(self, "start")
        end = ChartHandler.get_argument(self, "end")
        resolution = ChartHandler.get_argument(self, "resolution")

        input_dict = drift_collector.read_input()

        maximum = input_dict["stats"]["last_block"]

        if end == "max":
            end = maximum
        if start == "min":
            start = 1793972  # contract origination
        if int(start) < 0:  # if negative number is used, subtract it from maximum
            start = maximum + int(start)
        if int(start) < 1793972 and start > 0:  # prevent oor operation (exclude negative numbers)
            start = 1793972
        if int(end) > maximum:  # prevent oor operation
            end = maximum

        block_range = list(range(int(start), int(end) + 1))  # +1 to include in range

        value_list = []
        for key, value in input_dict["data"].items():
            if int(start) <= int(key) <= int(end):
                value_list.append(value[chart])

        values = value_list
        labels = block_range

        if resolution != "max":
            if int(resolution) > int(end) - start:
                resolution = int(end) - start

            values = reduce(list(value_list), int(resolution))
            labels = reduce(list(block_range), int(resolution))

        self.render("chart.html",
                    labels=json.dumps(labels),
                    values=json.dumps(values),
                    title=chart
                    )


class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(drift_collector.read_input())


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dashboard.html")


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api", ApiHandler),
        (r"/chart(.*)", ChartHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


class ThreadedClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            drift_collector.collect(block_last=drift_collector.block_last_get(),
                                    block_start=drift_collector.block_start_get())
            print("Sleeping...")
            time.sleep(10)


if __name__ == "__main__":
    background = ThreadedClient()
    background.start()
    print("Background process started")

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
