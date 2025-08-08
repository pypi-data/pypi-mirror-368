# PyXHCustApp

A library provide functionality process chia plot log.

# Installation

```python_script
pip install py-xh-custapp-xethhung12
```

# Demo

```python
from py_xh_custapp_xethhung12 import CustApp, Entry, Profile, Platform

# create app
CustApp.appDefault("abc_app")

# check if proxy is set for the app
print(app.has_proxy())

# set a entry of key `xxx` with vaule `yyy`
app.set_kv(Entry.simple('xxx'), "yyy")

# get the value of configuration entry
print(app.get_kv(Entry.simple('xxx')))

# remove the configuration entry
app.rm_kv(Entry.simple('xxx'))

# check if configuration entry exists
print(app.has_kv(Entry.simple('xxx')))

# create a entry with profile (some kind grouping of configuration)
entry = Entry.with_profile("key", "profile_name")

# print the app home directory
print(app.home)
```

```shell script
# `python -m py_xh_custapp_xethhung12` can be replace by `pyXhCustapp` as short cut script

pyXhCustapp apps #Show all apps found in the directory

pyXhCustapp app --name {app name} list #Show all all
pyXhCustapp app --name {app name} exist {key} #return true if {key} exists
pyXhCustapp app --name {app name} value {key} #return value of {key} or None
pyXhCustapp app --name {app name} set {key} {value} #set {value} to {key}
pyXhCustapp app --name {app name} remove {key} #remove {key}
```
