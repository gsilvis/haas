from flask import Flask, jsonify, abort, make_response, request
import haas.control as control
import haas.model
import haas.config
from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)


class G():
    pass
g=G()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@auth.verify_password
def verify_password(username, password):
    g.username=username
    return True


@app.route('/groups', methods = ['GET'])
@auth.login_required
def get_groups():
    print g.username
    groups = []
    for group in  haas.control.query_db(haas.model.Group):
        print group
        groups.append({
                'group_name':group.group_name,
                'vm_name':group.vm_name,
                'network_id':group.network_id,
                'deployed':group.deployed
                })

    return jsonify({'groups': groups} )


@app.route('/groups/<group_name>', methods = ['GET'])
def get_group(group_name):
    group = haas.control.get_entity_by_cond(haas.model.Group,"group_name=='%s'"%group_name)

    group_dict ={
        'group_name': group.group_name,
        'vm_name': group.vm_name,
        'network_id': group.network_id,
        'deployed': group.deployed,
        }
    return jsonify(group_dict)

@app.route('/groups/<group_name>/nodes', methods = ['GET'])
def get_group_nodes(group_name):
    group = haas.control.get_entity_by_cond(haas.model.Group,"group_name=='%s'"%group_name)
    nodes = []
    print group
    for node in group.nodes:
        print node
        nodes.append(node.node_id)
    nodes_dict={"nodes":nodes}
    return jsonify(nodes_dict)

@app.route('/groups/<group_name>/nodes/add/<node_id>',methods = ['POST'])
def add_node_to_group(group_name,node_id):
    node_id = int(node_id)
    group = haas.control.get_entity_by_cond(haas.model.Group,'group_name == "%s"'%group_name)
    node = haas.control.get_entity_by_cond(haas.model.Node, 'node_id == %d'%node_id)
    if not group or not node or node.available == False:
        abort(404)
    node.group = group
    return get_group_nodes(group_name)

@app.route('/groups/<group_name>/nodes/remove/<node_id>',methods = ['DELETE'])
def remove_node_from_group(group_name,node_id):
    node_id = int(node_id)
    group = haas.control.get_entity_by_cond(haas.model.Group,'group_name == "%s"'%group_name)
    node = haas.control.get_entity_by_cond(haas.model.Node, 'node_id == %d'%node_id)
    if not group or not node:
        abort(404)
    node.group = None
    node.available = True
    return get_group_nodes(group_name)


"""
All the infrastructure config use POST,
get parameters from the request, and call the corresponding
function in haas.control
There is no need for type conversion.
Incorrect type should cause an error.
Returns success or exceptions.
"""


@app.route('/groups', methods = ['POST'])
def create_group():
    if not request.json or not 'group_name' in request.json:
        abort(400)
    group = {
        'group_name': request.json['group_name'],
        'vm_name': request.json['vm_name'],
        'network_id' : request.json['network_id'],
        'deployed' : False
    }
    print group
    haas.control.create_group(group['group_name'],group['vm_name'],group['network_id'])
    groups.append(group)
    return jsonify({ 'group':group}), 201

@app.route('/groups/<group_name>', methods = ['DELETE'])
def destroy_group(group_name):
    haas.control.destroy_group(group_name)
    return get_groups()


@app.route('/nodes',methods = ['POST'])
def create_node():
    parameters = map((lambda x: request.json[x]),('node_id'))
    control.create_node(*parameters)
    return jsonify(),201
    
@app.route('/nics',methods=['POST'])
def create_nic():
    parameters = map((lambda x: request.json[x]),('nic_id','mac_addr','name'))
    control.create_nic(*parameters)
    return jsonify(),201

@app.route('/switches',methods=['POST'])
def create_switch():
    parameters = map((lambda x: request.json[x]),('switch_id','script'))
    control.create_switch(*parameters)
    return jsonify(),201

@app.route('/ports',methods=['POST'])
def create_port():
    parameters = map((lambda x: request.json[x]),('port_id','switch_id','port_no'))
    control.create_port(*parameters)
    return jsonify(),201

if __name__ == '__main__':
    app.run(debug = True)


