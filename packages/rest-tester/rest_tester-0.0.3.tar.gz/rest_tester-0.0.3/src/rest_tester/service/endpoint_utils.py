import time, random, json, math, os, sys, datetime
from flask import jsonify
from jinja2 import Environment

def make_generic_handler(response_json, response_delay_sec):

    env = Environment(
        autoescape=False
    )

    counter = 0

    def req2json(request):
        all_info = {}
        all_info['method'] = request.method
        all_info['url'] = request.url
        all_info['path'] = request.path
        all_info['remote_addr'] = request.remote_addr
        all_info['headers'] = dict(request.headers)
        all_info['query_params'] = request.args.to_dict()
        if request.method in ['POST', 'PUT'] and request.form:
            all_info['form_data'] = request.form.to_dict()
        if request.is_json:
            all_info['json_data'] = request.json
        all_info['cookies'] = request.cookies
        return all_info

    def handler(req):
        # Kombiniere response_json mit Request-Daten
        response_json_string = json.dumps(response_json, indent=2, ensure_ascii=False)

        json_template_response = env.from_string(response_json_string)
        rendered_json_response = json_template_response.render( **req2json(req), time=time, random=random, json=json, math = math, os=os, sys=sys, datetime=datetime, counter=counter)
        
        resp =json.loads(rendered_json_response)
        print(json.dumps(req2json(req), indent=2, ensure_ascii=False))

        time.sleep(response_delay_sec)
        return resp
    
    return handler
