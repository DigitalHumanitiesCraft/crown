import pandas as pd
import xml.etree.ElementTree as ET
from xml.dom import minidom

# excel file
Crown_Userfields = 'data/Crown_Userfields.xlsx'

# read excel file in pandas df
df = pd.read_excel(Crown_Userfields, engine='openpyxl')

# creating xml root element "entries"
root = ET.Element('entries')

# iterating through all unique userfield names, creating an entry element for each 
# with two subelements "userfield name" and "property path"

for userfield in  df["UserfieldName"].unique():
    entry = ET.SubElement(root, "entry")
    userfield_name = ET.SubElement(entry, "userfieldName")
    userfield_name.text = str(userfield)
    property_path = ET.SubElement(entry, "propertyPath")
    property_path.text = " "

# creating the tree
tree = ET.ElementTree(root)

# creating an indented xml file and writing 
pretty_xml = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
with open("mapping_userfields.xml", "w", encoding="utf-8") as fh:
    fh.write(pretty_xml)


