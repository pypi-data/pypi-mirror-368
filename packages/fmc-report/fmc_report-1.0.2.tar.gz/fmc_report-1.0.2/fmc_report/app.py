import os
import secrets
from time import sleep

import fmc_report.accessRules as accessRules
import csv

from pprint     import pprint
from flask      import Flask, render_template, request, redirect, session, url_for, send_file
from dotenv     import load_dotenv
from fireREST   import FMC
from typing     import Optional
from io         import StringIO

import requests.exceptions
import fireREST.exceptions

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))
load_dotenv()

@app.route('/', methods=['GET', 'POST'])
def index():
    access_policy_list: list = []
    prefilter_policy_list: list = []

    if request.method == 'GET':
        if check_and_set_credentials():
            hostname, username, password = get_credentials_from_session()
            fmc = login(hostname, username, password)
            if fmc:
                uuid = fmc.domain.get('uuid')
                access_policies = fmc.policy.accesspolicy.get(uuid=uuid)
                prefilter_policies = fmc.policy.prefilterpolicy.get(uuid=uuid)
                for policy in access_policies:
                    access_policy_list.append({"id": policy.get('id'), "name": policy.get('name')})
                for policy in prefilter_policies:
                    prefilter_policy_list.append({"id": policy.get('id'), "name": policy.get('name')})
                return render_template('index.html',
                                       access_policy_list=access_policy_list,
                                       prefilter_policy_list=prefilter_policy_list)
            return render_template('index.html', error="connection")
    return redirect(url_for('fmc_login'))

@app.route('/login', methods=['GET', 'POST'])
def fmc_login():
    if request.method == "POST":
        session['hostname'] = request.form.get('hostname')
        session['username'] = request.form.get('username')
        session['password'] = request.form.get('password')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/tables', methods=['GET', 'POST'])
def fmc_tables():
    if request.method == 'POST':
        access_policy_list, prefilter_policy_list, rules, network_group_list = get_data()
        current_access_list = get_access_list_name_from_id(
            access_list_id=request.form.get('access_lists'),
            access_policy_list=access_policy_list
        )
        return render_template('tables.html',
                               access_policy_list=access_policy_list,
                               prefilter_policy_list=prefilter_policy_list,
                               rules=rules,
                               network_group_list=network_group_list,
                               current_access_list=current_access_list,
                               current_access_list_id=request.form.get('access_lists'))
    return redirect(url_for('index'))

@app.route('/download', methods=['GET', 'POST'])
def fmc_download():
    if request.method == 'POST':
        access_policy_list, prefilter_policy_list, rules, network_group_list = get_data()
        current_access_list = get_access_list_name_from_id(
            access_list_id=request.form.get('access_lists'),
            access_policy_list=access_policy_list
        )
        create_csv(rules, network_group_list)
        return send_file("../export.csv", as_attachment=True, download_name="export.csv")

# @app.route('/tables', methods=['GET', 'POST'])
# def fmc_tables():
#     if request.method == 'POST':
#         if check_and_set_credentials():
#             access_policy_list, prefilter_policy_list, access_rules_list, rules, network_group_list, access_policy = sort_data()
#             find_network_groups(access_rules_list=access_rules_list)
#             if request.form.get('download'):
#                 create_csv(access_policy_list)
#                 return send_file("export.csv", as_attachment=True, download_name="export.csv")
#
#             return render_template('tables.html',
#                                    access_policy_list=access_policy_list,
#                                    prefilter_policy_list=prefilter_policy_list,
#                                    # access_policies=access_rules_list,
#                                    rules=rules,
#                                    network_group_list=network_group_list,
#                                    access_policy=access_policy)
#         return redirect(url_for('fmc_login'))
#     return redirect(url_for('index'))

def get_access_list_name_from_id(access_list_id: str, access_policy_list: list) -> Optional[str]:
    for access_policy in access_policy_list:
        if access_policy.get('id') == access_list_id:
            return access_policy.get('name')
    return None

def get_data():
    if check_and_set_credentials():
        hostname, username, password = get_credentials_from_session()
        fmc = login(hostname, username, password)
        uuid = get_uuid(fmc=fmc)
        access_policy_list = get_access_policies(fmc=fmc, uuid=uuid)
        prefilter_policy_list = get_prefilter_policies(fmc=fmc, uuid=uuid)
        access_policy = request.form.get('access_lists')
        rules = get_access_rules(fmc=fmc, uuid=uuid, access_policy_id=access_policy)
        access_rules_list = accessRules.create_access_rules_from_dicts(rules)
        network_group_list = get_network_group_list(fmc=fmc, uuid=uuid, access_rules_list=access_rules_list)
        return access_policy_list, prefilter_policy_list, rules, network_group_list

def get_prefilter_policies(fmc, uuid):
    prefilter_policies: list = fmc.policy.prefilterpolicy.get(uuid=uuid)
    return prefilter_policies

def get_network_group_list(fmc, uuid, access_rules_list):
    network_group_list = []
    network_group_names = find_network_groups(access_rules_list=access_rules_list)
    for network_group_name in network_group_names:
        network_group = get_network_group(fmc=fmc, uuid=uuid, group_name=network_group_name)
        objects = []
        try:
            for obj in get_objects_from_network_group(network_group):
                objects.append(obj.get("name"))
            network_group_list.append({"name": network_group_name, "objects": objects})
        except Exception as e:
            print(e)
    return network_group_list

def find_network_groups(access_rules_list: list[accessRules.AccessRule]):
    # Hier einfügen, dass liste mit dicts {NetworkGroupName: [ip-address, network, oderso]}
    network_groups: set = set()
    for rule in access_rules_list:
        # print(rule.name)
        # print(type(rule.sourceNetworks.get('objects')))
        try:
            if rule.sourceNetworks.get('objects'):
                for sourceNetwork in rule.sourceNetworks.get('objects'):
                    # print(sourceNetwork)
                    if sourceNetwork.get('type') == 'NetworkGroup':
                        network_groups.add(sourceNetwork.get('name'))
        except Exception as e:
            print(e)
        # if rule.destinationNetworks.get('type') == 'NetworkGroup':
        #     print(rule.destinationNetworks.get('name'))
    return network_groups

def check_for_entry(current_list: list, entry: dict[str, list]):
    for list_entry in current_list:
        for key, value in entry.items():
            if key in list_entry and list_entry[key] == value:
                return True
    return False

def get_fmc() -> Optional[FMC]:
    fmc: Optional[FMC] = None
    if check_and_set_credentials():
        hostname, username, password = get_credentials_from_session()
        fmc = login(hostname, username, password)
    return fmc

def get_uuid(fmc: FMC) -> Optional[str]:
    uuid: Optional[str] = fmc.domain.get('uuid')
    return uuid

def get_access_policies(fmc: FMC, uuid: str) -> Optional[list]:
    access_policies: Optional[list] = fmc.policy.accesspolicy.get(uuid=uuid)
    return access_policies

def get_access_rules(fmc: FMC, uuid: str, access_policy_id: str) -> Optional[list]:
    rules: list = fmc.policy.accesspolicy.accessrule.get(uuid=uuid, container_uuid=access_policy_id)
    return rules

def get_network_group(fmc: FMC, uuid: str, group_name: str) -> Optional[dict]:
    network_group: Optional[dict] = fmc.object.networkgroup.get(uuid=uuid, name=group_name)
    return network_group

def get_objects_from_network_group(network_group: dict) -> Optional[list]:
    objects: list = network_group.get('objects')
    return objects

def check_and_set_credentials():
    if not check_for_session():
        if check_for_environment():
            environment_to_session()
            return True
        return False
    return True

def check_for_environment() -> bool:
    hostname = os.getenv("HOSTNAME")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    return all(var is not None for var in [hostname, username, password])

def environment_to_session():
    if check_for_environment():
        session["hostname"] = os.getenv("HOSTNAME")
        session["username"] = os.getenv("USERNAME")
        session["password"] = os.getenv("PASSWORD")

def check_for_session() -> bool:
    hostname, username, password = get_credentials_from_session()
    return all(var is not None for var in [hostname, username, password])

def get_credentials_from_session() -> (str, str, str):
    hostname = session.get('hostname')
    username = session.get('username')
    password = session.get('password')
    return hostname, username, password

def login(hostname: str, username: str, password: str) -> Optional[FMC]:
    try:
        fmc = FMC(hostname=hostname, username=username, password=password, timeout=5)
        uuid = fmc.domain.get('uuid')
        return fmc
    except requests.exceptions.ConnectTimeout as exception:
        print(exception)
        return None
    except fireREST.exceptions.AuthError as exception:
        print(exception)
        return None

def create_csv(data, network_group_list: list) -> None:
    output = StringIO()
    current_directory = os.getcwd()
    csv_file_path = os.path.join(current_directory, 'export.csv')
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['Action',
                         'Name',
                         'Source Zones',
                         'Destination Zones',
                         'Source Networks',
                         'Destination Networks',
                         'Source Ports',
                         'Destination Ports',
                         'Source Security Group Tags',
                         'Applications'])

        for rule in data:
            row = []
            objects = []
            subobjects = []
            row.append(rule['action'])
            row.append(rule['name'])

            for object in rule.get('sourceZones', {'objects': [{'name': '-'}]}).get('objects'):
                objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []

            for object in rule.get('destinationZones', {'objects': [{'name': '-'}]}).get('objects'):
                objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []

            for object in rule.get('sourceNetworks', {'objects': [{'name': '-'}]}).get('objects'):
                if object.get('type') == 'NetworkGroup':
                    for network_group in network_group_list:
                        subobjects.append(', '.join(network_group.get('objects')))
                    objects.append(f"{object.get('name')}: {subobjects}")
                else:
                    objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []
            subobjects = []

            for object in rule.get('destinationNetworks', {'objects': [{'name': '-'}]}).get('objects'):
                if object.get('type') == 'NetworkGroup':
                    for network_group in network_group_list:
                        subobjects.append(', '.join(network_group.get('objects')))
                    objects.append(f"{object.get('name')}: {subobjects}")
                else:
                    objects.append(object.get('name'))
            row.append(',\n'.join(objects))

            objects = []
            subobjects = []

            for object in rule.get('sourcePorts', {'objects': [{'name': '-'}]}).get('objects'):
                objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []

            for object in rule.get('destinationPorts', {'objects': [{'name': '-'}]}).get('objects'):
                objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []

            for object in rule.get('sourceSecurityGroupTags', {'objects': [{'name': '-'}]}).get('objects'):
                objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []

            for object in rule.get('applications', {'applications': [{'name': '-'}]}).get('applications'):
                objects.append(object.get('name'))
            row.append(',\n'.join(objects))
            objects = []

            writer.writerow(row)

    # output.seek(0)
    # return output.getvalue()

if __name__ == '__main__':
    app.run()
