from flask import Blueprint, render_template, request, jsonify, abort, make_response
import hashlib
import json as _json
from ...services.control_service import ControlService

controls_bp = Blueprint('controls', __name__)


@controls_bp.route('/')
def list_controls():
    svc = ControlService()
    controls = svc.list_controls(
        framework_code=request.args.get('framework'),
        q=request.args.get('q'),
        status=request.args.get('status'),
        owner=request.args.get('owner'),
        risk=request.args.get('risk'),
        org_id=request.args.get('org'),
    )
    filter_opts = svc.get_filter_options(request.args.get('org'))
    return render_template('controls/controls.html', controls=controls, filter_opts=filter_opts)


@controls_bp.route('/api/<uuid:control_id>')
def control_detail(control_id):
    svc = ControlService()
    data = svc.get_control_detail(control_id, org_id=request.args.get('org'))
    if not data:
        abort(404)
    payload = _json.dumps(data, sort_keys=True, default=str).encode('utf-8')
    etag = 'W/"' + hashlib.md5(payload).hexdigest() + '"'
    inm = request.headers.get('If-None-Match')
    if inm and inm == etag:
        resp = make_response('', 304)
        resp.headers['ETag'] = etag
        resp.headers['Cache-Control'] = 'public, max-age=30'
        return resp
    resp = make_response(jsonify(data))
    resp.headers['ETag'] = etag
    resp.headers['Cache-Control'] = 'public, max-age=30'
    return resp
