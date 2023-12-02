from odoo import http
from odoo.http import request
import json
import os
from odoo.http import content_disposition, serialize_exception


class DownloadFile(http.Controller):
    @http.route('/controller/<fileid>', type='http', auth="public")
    def download(self, fileid, **kw):
        path = "/opt/odoo/custom/addons/dc_ewaybilll/Bills" + fileid + ".json"
#         path = "./custom/addons/dc_ewaybilll/Bills" + fileid + ".json"
        
        with open(path, 'r') as fobj:
            data = fobj.read()
            filename = "" + fileid + ".json"
            return request.make_response(data, [('Content-Type', 'application/octet-stream'),
                                                ('Content-Disposition', content_disposition(filename))])

