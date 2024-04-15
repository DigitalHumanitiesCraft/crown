from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD
import pandas as pd
import re

BASE_URL = "https://gams.uni-graz.at/"
PID_PERSON = 'o:crown.index.person'
PID_ORGANISATION = 'o:crown.index.organisation'

# excel files
# 
folder = "sample"
CROWN_Objects_4_Constituents = f'/home/chrisi/Documents/GitHub/CROWN/data/export/{folder}/CROWN_Objects_5_Constituents_2024_02_02.xlsx'

# substring before " ("; remove ", " and  " " so its a valid URI
def normalizeStringforURI(string):
     if(str(string).count(",") <= 1):
        if(" (" in string):
            return ((string.split(" (")[0]).replace(", ", "")).replace(" ", "")  
        else:
            return (string.replace(", ", "")).replace(" ", "")  
     else:
            return "anonym"

def normalizeStringforJSON(string):
    string = string.replace('"', '\\"')
    string = " ".join(string.split())
    return string 

# MAIN
# Objektinformationen

CROWN_Objects_4_Constituents_df = pd.read_excel(CROWN_Objects_4_Constituents, engine='openpyxl')

# make a persons graph
persons_graph = Graph()
GAMS = Namespace("https://gams.uni-graz.at/o:gams-ontology#")
VOID = Namespace("http://rdfs.org/ns/void#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
CROWN = Namespace("https://gams.uni-graz.at/o:crown.ontology#")
SCHEMA = Namespace("https://schema.org/")

# define namespace in output file
persons_graph.bind("gams", GAMS)
persons_graph.bind("void", VOID)
persons_graph.bind("dcterms", DCTERMS)
persons_graph.bind("dc", DC)
persons_graph.bind("crown", CROWN)
persons_graph.bind("schema", SCHEMA)

# void:Dataset
VOID_Dataset = URIRef(BASE_URL + PID_PERSON)
persons_graph.add((VOID_Dataset, RDF.type, VOID.Dataset))
# void 
persons_graph.add((VOID_Dataset, VOID.feature, URIRef("http://www.w3.org/ns/formats/RDF_XML")))
persons_graph.add((VOID_Dataset, VOID.dataDump, URIRef(BASE_URL + PID_PERSON + "/ONTOLOGY")))
persons_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:crown.ontology#")))
persons_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:gams-ontology#")))
persons_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("http://purl.org/dc/terms/")))

persons_graph.add((VOID_Dataset, DC.title, Literal("Personenindex")))
persons_graph.add((VOID_Dataset, DC.language, Literal('ger') ))
persons_graph.add((VOID_Dataset, DC.source, Literal('KHM') ))
# static metadata
persons_graph.add((VOID_Dataset, DC.relation, Literal( "CROWN. Untersuchungen zu Materialität, Technologie und Erhaltungszustand der Wiener Reichskrone." ) ))
persons_graph.add((VOID_Dataset, DC.relation, Literal( "http://gams.uni-graz.at/crown" ) ))
persons_graph.add((VOID_Dataset, DC.publisher, Literal( "Institute Centre for Information Modelling, University of Graz" ) ))
persons_graph.add((VOID_Dataset, DC.rights, Literal( "Creative Commons BY 4.0" ) ))
persons_graph.add((VOID_Dataset, DC.rights, Literal( "https://creativecommons.org/licenses/by/4.0" ) ))


# make a organisations graph
organisations_graph = Graph()
GAMS = Namespace("https://gams.uni-graz.at/o:gams-ontology#")
VOID = Namespace("http://rdfs.org/ns/void#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
CROWN = Namespace("https://gams.uni-graz.at/o:crown.ontology#")
SCHEMA = Namespace("https://schema.org/")

# define namespace in output file
organisations_graph.bind("gams", GAMS)
organisations_graph.bind("void", VOID)
organisations_graph.bind("dcterms", DCTERMS)
organisations_graph.bind("dc", DC)
organisations_graph.bind("crown", CROWN)
organisations_graph.bind("schema", SCHEMA)

# void:Dataset
VOID_Dataset = URIRef(BASE_URL + PID_ORGANISATION)
organisations_graph.add((VOID_Dataset, RDF.type, VOID.Dataset))
# void 
organisations_graph.add((VOID_Dataset, VOID.feature, URIRef("http://www.w3.org/ns/formats/RDF_XML")))
organisations_graph.add((VOID_Dataset, VOID.dataDump, URIRef(BASE_URL + PID_ORGANISATION + "/ONTOLOGY")))
organisations_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:crown.ontology#")))
organisations_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:gams-ontology#")))
organisations_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("http://purl.org/dc/terms/")))

organisations_graph.add((VOID_Dataset, DC.title, Literal("Organisationenindex")))

organisations_graph.add((VOID_Dataset, DC.language, Literal('ger') ))
organisations_graph.add((VOID_Dataset, DC.source, Literal('KHM') ))
# static metadata
organisations_graph.add((VOID_Dataset, DC.relation, Literal( "CROWN. Untersuchungen zu Materialität, Technologie und Erhaltungszustand der Wiener Reichskrone." ) ))
organisations_graph.add((VOID_Dataset, DC.relation, Literal( "http://gams.uni-graz.at/crown" ) ))
organisations_graph.add((VOID_Dataset, DC.publisher, Literal( "Institute Centre for Information Modelling, University of Graz" ) ))
organisations_graph.add((VOID_Dataset, DC.rights, Literal( "Creative Commons BY 4.0" ) ))
organisations_graph.add((VOID_Dataset, DC.rights, Literal( "https://creativecommons.org/licenses/by/4.0" ) ))

# iterate through the rows, every row is a constituent
for row in CROWN_Objects_4_Constituents_df.itertuples(index=True):
    
    # variables
    constituent_id = getattr(row, "ConstituentID")
    display_name = normalizeStringforJSON(str(getattr(row, "DisplayName")))
    
    # Creating the organisations
    if pd.notnull(constituent_id) and ((getattr(row, "Role") == "Bezug/Institution" or
        getattr(row, "Role") == "Sammlung" or getattr(row, "Role") == "Abbildung/Institution")):
        organisation = URIRef(BASE_URL + PID_ORGANISATION + '#organisation.' + str(constituent_id))
        organisations_graph.add((organisation, RDF.type, SCHEMA.Organisation))
        organisations_graph.add((organisation, GAMS.isMemberOfCollection, URIRef("https://gams.uni-graz.at/context:crown")))
        organisations_graph.add((organisation, SCHEMA.name, Literal(getattr(row, "DisplayName"))))
    
    # everything else is a person, some museums too because the are "Künstler/in"
    else:
        person = URIRef(BASE_URL + PID_PERSON + '#person.' + str(constituent_id))
        persons_graph.add((person, RDF.type, SCHEMA.Person))
        persons_graph.add((person, GAMS.isMemberOfCollection, URIRef("https://gams.uni-graz.at/context:crown")))
        persons_graph.add((person, SCHEMA.name, Literal(getattr(row, "DisplayName"))))

# OUTPUT file .xml
persons_graph.serialize(destination = 'rdf_output_indices/index_persons.xml', format="pretty-xml")
organisations_graph.serialize(destination = 'rdf_output_indices/index_organisations.xml', format="pretty-xml")