# import os
# os.environ["using-j-vault-rest-server"]="localhost,7910,false,harden"
import py_xh_custapp_xethhung12 as project
from j_vault_http_client_xethhung12 import client
import sys
import argparse
import os
from pathlib import Path




def main():
    client.load_to_env()

    parser = argparse.ArgumentParser(
                    prog='pyXhCustapp',
                    description='A app help manage local py apps',
                    # epilog='Text at the bottom of help'
                    )
    cmd_parsers = parser.add_subparsers(dest="cmd")
    cmd_parsers.add_parser("apps")

    app_parser=cmd_parsers.add_parser("app")

    app_parser.add_argument("--name", "-n", required=True, type=str, help="The name of the app")
    app_parser.add_argument("--profile", "-p", required=False, default=None, type=str, help="The profile to use")

    sub_parsers = app_parser.add_subparsers(dest="mainCmd")
    sub_cmd = sub_parsers.add_parser("list", help="listing all the configuration of select app")
    sub_cmd.add_argument("--no-profile", required=False, action='store_true', help="skip profile entry when search")

    sub_cmd = sub_parsers.add_parser("exists", help="check if key of config exists in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")

    sub_cmd = sub_parsers.add_parser("show", help="show the value of select config key in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")

    sub_cmd = sub_parsers.add_parser("set", help="set the config key and vaule in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")
    sub_cmd.add_argument("--value", "-v", required=True, type=str, help="The value of the  config to be set in app")

    sub_cmd = sub_parsers.add_parser("unset", help="unset a config key in app")
    sub_cmd.add_argument("--key", "-k", required=True, type=str, help="The key of config to be set in the app")

    data = parser.parse_args()
    # print(data)


    if data.cmd == "apps":
        p = project.CustApp.defaultAppPath(Path.home())

        folders = [name for name in os.listdir(p)
                if os.path.isdir(os.path.join(p, name))]
        if len(folders) == 0:
            print("No app created")
        else:
            print(f"Total {len(folders)} {'app' if len(folders)==1 else 'apps'} created")
        for f in folders:
            print(f"* `{f}`")
    elif data.cmd == "app":
        profile = project.Profile(data.profile)
        app = project.CustApp.appDefault(data.name)
        if data.mainCmd == "list":
            files = app.list(profile= profile, no_profile=data.no_profile)
            var_num = len(files)
            print("Number of variable: %s" % var_num)
            for file in files:
                # print("%s: %s" % (file, self.get_kv(file)))
                print("%s: [hidden]" % (file))
        elif data.mainCmd == "exists":
            key=data.key
            entry=project.Entry(key, profile)
            print(f"[{entry.name()}] {'not exists' if not app.has_kv(entry) else 'exists'}")
        elif data.mainCmd == "show":
            key=data.key
            entry=project.Entry(key, profile)
            v = app.get_kv(entry)
            if v is None:
                print(f"[{entry.name()}] not exists")
            else:
                print(f"[{entry.name()}]: {v}")
        elif data.mainCmd == "set":
            key=data.key
            value=data.value
            entry = project.Entry(key, profile)
            app.set_kv(entry, value)
            print(f"set [{entry.name()}] as {value}")
        elif data.mainCmd == "unset":
            key=data.key
            entry = project.Entry(key, profile)
            if app.has_kv(entry):
                app.rm_kv(entry)
                print(f"Removed [{entry.name()}]")
            else:
                print(f"key[{entry.name()}] not exists")
        else:
            raise Exception(f"No any match cmd args found: {sys.argv}")
    else:
        raise Exception(f"No any match cmd args found: {sys.argv}")
