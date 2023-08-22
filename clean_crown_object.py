import xml.etree.ElementTree as ET
import os

# Namespaces need to registered, otherwise it will write out ns:0 etc.
ET.register_namespace("crown", "https://gams.uni-graz.at/o:crown.ontology#")
ET.register_namespace("dc","http://purl.org/dc/elements/1.1/")
ET.register_namespace("schema", "https://schema.org/")
ET.register_namespace("dcterms", "http://purl.org/dc/terms/")
ET.register_namespace("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
ET.register_namespace("void", "http://rdfs.org/ns/void#")
ET.register_namespace("gams", "https://gams.uni-graz.at/o:gams-ontology#")
ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")

directory = "rdf_output"
for filename in os.listdir(directory):
    tree = ET.parse(directory + "/" + filename)
    root = tree.getroot()
    crown_object = (root.find(".//{https://gams.uni-graz.at/o:crown.ontology#}Object") 
                    or root.find(".//{https://gams.uni-graz.at/o:crown.ontology#}AdditionalMaterial"))
    new_rdf_about = crown_object.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"].rstrip("o").rstrip(".")
    crown_object.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", new_rdf_about)
    tree.write(directory + "/" + filename, encoding="UTF-8")