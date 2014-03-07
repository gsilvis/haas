from flask import Flask, jsonify, abort, make_response, request
import haas.control as control
import haas.model
import haas.config


app = Flask(__name__)


"""
All the infrastructure config use POST,
get parameters from the request, and call the corresponding
function in haas.control
There is no need for type conversion.
Incorrect type should cause an error.
Returns success or exceptions.
"""


@app.route('/group/<group_name>', methods = ['DELETE'])
def destroy_group(group_name):
    control.destroy_group(group_name)
    return jsonify(),201
    

@app.route('/group', methods = ['POST'])
def create_group():
    parameters = map((lambda x: request.json[x]),("group_name",))
    print parameters
    control.create_group(*parameters)
    return jsonify(), 201


@app.route('/node',methods = ['POST'])
def create_node():
    print request.json
    parameters = map((lambda x: request.json[x]),('node_id',))
    control.create_node(*parameters)
    return jsonify(),201
    
@app.route('/nic',methods=['POST'])
def create_nic():
    parameters = map((lambda x: request.json[x]),('nic_id','mac_addr','name'))
    control.create_nic(*parameters)
    return jsonify(),201

@app.route('/switch',methods=['POST'])
def create_switch():
    parameters = map((lambda x: request.json[x]),('switch_id','script'))
    control.create_switch(*parameters)
    return jsonify(),201

@app.route('/port',methods=['POST'])
def create_port():
    parameters = map((lambda x: request.json[x]),('port_id','switch_id','port_no'))
    control.create_port(*parameters)
    return jsonify(),201
    
@app.route('/connection',methods=['POST'])
def connect_nic():
    parameters = map((lambda x: request.jon[x]),('nic_id',port_id))
    control.connect_nic(*parameters)
    return jsonify(),201
    
@app.route('/<table_name>',methods=['GET'])
def show_table(table_name):
    control.show_table(table_name)
    return jsonify(),201


"""
wishlist
add_node(node_id,group_name)
add_nic(nic_id,node_id)
create_vlan(vlan_id)
connect_vlan(vlan_id,group_name,nic_name)
headnode_create()
headnode_attach(vm_name,group_name)
deploy_group(group_name)
create_user(user_name,password)
show_all()
show_table(table_name)
"""


if __name__ == '__main__':
    app.run(debug = True)


