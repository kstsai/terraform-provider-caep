import xml.etree.cElementTree as ET
import ast
import os
owner=''
owner_str="{'resource_management':'@Marko', 'dpagent':'@Kuo-Shou', 'comprehensive_cases':'@Jason Yuan'}"

properties = 'buildStatus=SUCCESS'

if 'MODULE_OWNER' in os.environ:
    owner_str=os.environ['MODULE_OWNER']
print (owner_str)

owner_dict=ast.literal_eval(owner_str)

tree = ET.ElementTree(file='pytest_r3_e2e.xml')
root = tree.getroot()
for child_of_root in root[0]:
    for child_of_child in child_of_root:
        if child_of_child.tag != 'failure':
            continue
        for owner_key in owner_dict:
            if owner_key in child_of_root.attrib.get('classname') and owner_dict[owner_key] not in owner:              
                owner = owner + '`' + owner_dict[owner_key] + '` '
if owner:
    properties = 'buildStatus=Error count:'+root[0].get('failures')+'/'+root[0].get('tests')+'. Error owner: ' + owner

f = open( 'ownlist.properties', 'w' )
f.write( properties + '\n')
f.close()