# Let's get this party started!
from wsgiref.simple_server import make_server

import falcon
import pytest

import json
import os
import time, datetime
import subprocess
import random
from multiprocessing import Process
import threading

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.

# {{{ class RequireJSON(object):
class RequireJSON(object):

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable(
                'This API only supports responses encoded as JSON.',
                href='http://docs.examples.com/api/json')

        if req.method in ('POST'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON. but now passing {}'.format(req.content_type),
                    href='http://docs.examples.com/api/json')

# }}}

# {{{ class JSONTranslator(object):
class JSONTranslator(object):
    # NOTE: Starting with Falcon 1.3, you can simply
    # use req.media and resp.media for this instead.

    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

        if 'temp_file_names'not in resp.context:
            resp.context['temp_file_names'] = []

    #def process_response(self, req, resp, resource):
    def process_response(self, req, resp, resource, req_succeeded):
        if 'jsstr_result' in resp.context:
            resp.body = resp.context['jsstr_result']
            return

        if 'result' not in resp.context:
            return

        if 'temp_file_names' in resp.context:
            [ os.remove(tf) for tf in resp.context['temp_file_names'] if os.path.exists(tf) ]

        resp.body = json.dumps(resp.context['result'])
# }}}


class TestReportHtml(object):

    def on_put(self, req, resp):
        """Handles PUT requests"""

        marker = req.params.get("marker","applcm")
        ip_address = req.params.get("targetHostIp","192.168.82.35")

        outfile1 = "/pytester/report{}.htm".format("".join((ip_address.split(".")[-2:])))
        outfile2 = "/test/1.txt"
        # pytest.main(["--html=%s"%(outfile1), "--self-contained-html"])
        """
        cmd = "python3 -m pytest -m {} --ip_address {} --capture=tee-sys -vvv --html={} --self-contained-html".format(marker,ip_address,outfile1)

        f2 = open(outfile1,"w")
        p = subprocess.Popen(cmd.split(), cwd='/pytester',stdout=f2)
        out,errs = p.communicate() # blocking mode
        print(out)

        resp.status = falcon.HTTP_200
        resp.body = "/test/reports/{}\n/test/reports/{}\n".format(os.path.basename(outfile1), os.path.basename(outfile1))
        """
        if os.path.exists( "/tmp/e2etest_%s"%(ip_address)):
            resp.status = falcon.HTTP_201
            return

        open("/tmp/e2etest_%s"%(ip_address),"w").close()
        def _execPytestAsync(ip_address,outHtm,req):
            try:
                os.chdir("/pytester/tests")
                #args = ["-m",marker,"--ip_address",ip_address,"--capture=tee-sys", "-vvv", "--self-contained-html",
                #        "--html=".format(outHtm)]
                #pytest.main(args)
                os.environ["clientIp"] = reg.get("clientIp", "192.168.82.28")
                cmd = "python3 -m pytest -m {} --ip_address {} --capture=tee-sys -vvv --html={} --self-contained-html".format(marker,ip_address,outfile1)
                cout = os.popen(cmd,"r").read()
                for ln in cout.split("\n"):
                    print(ln)
            except:
                import sys, traceback
                msg = "{} {}".format(sys.exc_info(), traceback.format_exc())
                print(msg)
            finally:
                os.remove("/tmp/e2etest_%s"%(ip_address))

        
        threading.Thread(target=_execPytestAsync, args=(ip_address,outfile1,req)).start()

    def on_get(self, req, resp):
        # do some sanity check on the filename
        resp.status = falcon.HTTP_200
        ip_address = req.params.get("targetHostIp","192.168.82.35")
        if os.path.exists("/tmp/e2etest_%s"%(ip_address)):
            # os.stat_result(st_mode=33188, st_ino=193908016, st_dev=41, st_nlink=1, st_uid=0, st_gid=0, st_size=821, st_atime=1641170152, st_mtime=1641170152, st_ctime=1641281800)

            (mode,ino,dev,nlink,uid,gid,size,atime,mtime,ctime) = os.stat("/tmp/e2etest_%s"%(ip_address))
            resp.status = falcon.HTTP_201
            cost = str(datetime.timedelta(seconds=time.time()-ctime))
            resp.body = "{}\n e2e test on <{}> is still running\nstarted at <{}> , lasted {}\n".format(req.access_route, ip_address, time.ctime(ctime),cost) + os.popen("ps ax | grep applcm | grep -v grep").read()
            return
        outfile1 = "/pytester/report{}.htm".format("".join((ip_address.split(".")[-2:])))
        resp.content_type = 'text/html' 
        with open(outfile1, 'rb') as f:
            resp.body = f.read()
        return


class FakeApiHealth(object):

    def on_get(self, req, resp):
        res =  "online" if random.randrange(10) %2 == 0 else "error"
        finalRet = {
            "status": res
        }
        print(f'{finalRet},{res}, XXXX')
        resp.status = falcon.HTTP_200
        resp.context['result'] = finalRet

def init_app():

    app = falcon.API(middleware=[
        RequireJSON(),
        JSONTranslator()
    ])
    app.add_route('/test/reports', TestReportHtml())
    #app.add_route('/test/reports/{filename}', TestReportHtml())
    app.add_route('/health', FakeApiHealth())
    return app

if __name__ == '__main__':
    app = init_app()
    with make_server('0.0.0.0', 10287, app) as httpd:
        print('Serving on port 10287...')
        httpd.serve_forever()
