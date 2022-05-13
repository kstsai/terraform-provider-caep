#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# An example of a standalone application using the internal API of Gunicorn.
#
#   $ python standalone_app.py
#
# This file is part of gunicorn released under the MIT license.
# See the NOTICE for more information.

import multiprocessing

import gunicorn.app.base
import threading

def number_of_workers():
    return (1 * 2) + 1
    # return (multiprocessing.cpu_count() * 2) + 1

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options_=None):
        self.options = options_ or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':

    import pytestd
    import sys
    """/ecs_dev/hasidecar# docker run -ti --network host -v /var/run:/var/run -v /etc/kolla:/etc/kolla -v /etc/localtime:/etc/localtime hasidecar:ecs 10281
    ['hasicarMain.py', '10281']
    """
    port = sys.argv[1] if len(sys.argv) == 2 else '10287'
    options = {
        'bind': '%s:%s' % ('0.0.0.0', port),
        'workers': number_of_workers(),
        'timeout': 3000 
    }
    print("hasidecar main() ...{})".format(options))
    app = pytestd.init_app()

    StandaloneApplication(app, options).run()
