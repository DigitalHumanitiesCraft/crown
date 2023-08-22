from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD
import pandas as pd
from datetime import date


### global variables
########################################################################################
BASE_URL = "https://gams.uni-graz.at/"
PID_THESAURUS = 'o:crown.thesaurus#'

# excel files
KHM_Thesaurus = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/CROWN_Export/Crown_Material_Thesaurus.xlsx'
CROWN_Thesaurus = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/CROWN_Export/Crown_Material_Thesaurus_Xref_Objects.xlsx'

### functions
########################################################################################
# substring before " ("; remove ", " and  " " so its a valid URI
def normalizeStringforURI(string):
     if(str(string).count(",") <= 1):
        if(" (" in string):
            return ((string.split(" (")[0]).replace(", ", "")).replace(" ", "")  
        else:
            return (string.replace(", ", "")).replace(" ", "")  
     else:
            return "anonym"
########################################################################################
def normalizeStringforJSON(string):
    string = string.replace('"', '\\"')
    string = " ".join(string.split())
    return string 
########################################################################################
def get_SKOS(URI, broader_term_ID):

    """
    This function creates skos:broader and skos:narrower URIs and name tags and creates,
    if called repeatedly, a skos thesaurus. It returns an URI and a broader_term_ID
    which both are used in the next call to create a hierarchical structur.

    """
    # creating a df consisting of the broader terms and dropping rows with the same term master id so that we 
    # have only one row and we can access its term master ID to create an URI
    broader_term_df = KHM_Thesaurus_df.loc[KHM_Thesaurus_df["CN"] == broader_term_ID].drop_duplicates(subset=["TermMasterID"])
    broader_URI = URIRef(BASE_URL + PID_THESAURUS + str(broader_term_df.TermMasterID.values[0]))
    output_graph.add((URI, SKOS.broader, broader_URI))
    
    output_graph.add((broader_URI, RDF.type, SKOS.Concept))
    output_graph.add((broader_URI, SKOS.inScheme, URIRef(BASE_URL + PID_THESAURUS)))
    output_graph.add((broader_URI, SKOS.narrower, URI))

    # creating a new df out of the KHM df where the term master ids match so that in the next step
    # the different names for the materials can be accessed
    names_df = KHM_Thesaurus_df.loc[KHM_Thesaurus_df["TermMasterID"] == broader_term_df.TermMasterID.values[0]]
    german_term =  names_df[(names_df["LanguageID"] == 5) & (names_df["TermType"] == "Descriptor")]["Term"].values[0]
    output_graph.add((broader_URI, SKOS.prefLabel, Literal(german_term, lang="de")))
    
    if pd.notnull(names_df[names_df["LanguageID"] == 10019]["Term"].values):
        getty_URI = URIRef("http://vocab.getty.edu/aat/" + str(names_df[names_df["LanguageID"] == 10019]["Term"].values[0]))
        output_graph.add((broader_URI, SKOS.exactMatch, getty_URI))
    
    if pd.notnull(names_df[names_df["LanguageID"] == 9].drop_duplicates(subset="LanguageID")["Term"].values):
        english_term = names_df[names_df["LanguageID"] == 9]["Term"].values[0]
        output_graph.add((broader_URI, SKOS.prefLabel, Literal(english_term, lang="en")))

    # adding the top concept
    if len(broader_term_ID.split(".")) == 4:
        output_graph.add((SKOS_Dataset, SKOS.hasTopConcept, broader_URI)) 

    # shortening of the term ID which is used in the next function call for getting the broader materials
    broader_term_ID = broader_term_ID.rsplit(".", 1)[0]

    return broader_URI, broader_term_ID
########################################################################################
### MAIN
########################################################################################

# Objektinformationen

KHM_Thesaurus_df = pd.read_excel(KHM_Thesaurus, engine="openpyxl")
CROWN_Thesaurus_df = pd.read_excel(CROWN_Thesaurus, engine="openpyxl")

########################################################################################
# make a output graph
output_graph = Graph()
GAMS = Namespace("https://gams.uni-graz.at/o:gams-ontology#")
VOID = Namespace("http://rdfs.org/ns/void#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
DC = Namespace("http://purl.org/dc/elements/1.1/")
CROWN = Namespace("https://gams.uni-graz.at/o:crown.ontology#")
SCHEMA = Namespace("https://schema.org/")
TEST = Namespace("http://www.w3.org/2004/02/skos/core#")

# define namespace in output file
output_graph.bind("gams", GAMS)
output_graph.bind("void", VOID)
output_graph.bind("dcterms", DCTERMS)
output_graph.bind("dc", DC)
output_graph.bind("crown", CROWN)
output_graph.bind("schema", SCHEMA)
output_graph.bind("skos", SKOS)

# void:Dataset
VOID_Dataset = URIRef("https://gams.uni-graz.at/o:crown.object.thesaurus")
output_graph.add((VOID_Dataset, RDF.type, VOID.Dataset))
# void 
output_graph.add((VOID_Dataset, VOID.feature, URIRef("http://www.w3.org/ns/formats/RDF_XML")))
output_graph.add((VOID_Dataset, VOID.dataDump, URIRef("https://gams.uni-graz.at/o:crown.object.1480898/ONTOLOGY")))
output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:crown.ontology#")))
output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:gams-ontology#")))
output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("http://purl.org/dc/terms/")))
output_graph.add((VOID_Dataset, DC.title, Literal("Thesaurus")))
output_graph.add((VOID_Dataset, DC.language, Literal('ger') ))
output_graph.add((VOID_Dataset, DC.source, Literal('Kunsthistorisches Museum, Wien') ))
# static metadata
output_graph.add((VOID_Dataset, DC.relation, Literal( "CROWN. Untersuchungen zu Materialität, Technologie und Erhaltungszustand der Wiener Reichskrone." ) ))
output_graph.add((VOID_Dataset, DC.relation, Literal( "http://gams.uni-graz.at/crown" ) ))
output_graph.add((VOID_Dataset, DC.publisher, Literal( "Institute Centre for Information Modelling, University of Graz" ) ))
output_graph.add((VOID_Dataset, DC.rights, Literal( "Creative Commons BY-NC 4.0" ) ))
output_graph.add((VOID_Dataset, DC.rights, Literal( "https://creativecommons.org/licenses/by-nc/4.0/" ) ))
output_graph.add((VOID_Dataset, DC.creator, Literal("Digital Humanities Craft OG")))
output_graph.add((VOID_Dataset, DC.creator, Literal("Reiter, Georg")))
output_graph.add((VOID_Dataset, DC.creator, Literal("Steiner, Christian")))
output_graph.add((VOID_Dataset, DC.creator, Literal("Pollin, Christopher")))
output_graph.add((VOID_Dataset, DC.language, Literal("ger")))
output_graph.add((VOID_Dataset, RDFS.seeAlso, Literal("https://www.projekt-reichskrone.at/")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Geschichte", lang="de")))
output_graph.add((VOID_Dataset, DC.subject, Literal("History", lang="en")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Kunstgeschichte", lang="de")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Art History", lang="en")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Linked Open Data", lang="de")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Linked Open Data", lang="en")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Collection", lang="en")))
output_graph.add((VOID_Dataset, DC.subject, Literal("Sammlung", lang="de")))
output_graph.add((VOID_Dataset, DC.publisher, Literal("Kunsthistorisches Museum, Wien")))
output_graph.add((VOID_Dataset, DC.date, Literal(date.today().year)))
output_graph.add((VOID_Dataset, DCTERMS.modified, Literal(date.today())))

# SKOS

SKOS_Dataset = URIRef(BASE_URL + PID_THESAURUS)
output_graph.add((SKOS_Dataset, RDF.type, SKOS.ConceptScheme))
output_graph.add((SKOS_Dataset, DC.title, Literal("Thesaurus")))
output_graph.add((SKOS_Dataset, DC.language, Literal("ger", lang="de")))
output_graph.add((SKOS_Dataset, DC.language, Literal("eng", lang="en")))
output_graph.add((SKOS_Dataset, DC.identifier, URIRef(BASE_URL + PID_THESAURUS)))
output_graph.add((SKOS_Dataset, DC.publisher, URIRef("http://d-nb.info/gnd/1137284463")))
output_graph.add((SKOS_Dataset, DC.publisher, Literal( "Zentrum für Informationsmodellierung, Universität Graz" )))
output_graph.add((SKOS_Dataset, DC.publisher, Literal("Institute Centre for Information Modelling, University of Graz")))
output_graph.add((SKOS_Dataset, DC.date, Literal(date.today().year)))
output_graph.add((SKOS_Dataset, DC.decription, Literal("To Do", lang="deu")))
output_graph.add((SKOS_Dataset, DC.decription, Literal("To Do", lang="eng")))

# getting unique MasterIDs from the crown thesaurus so that we have
# all the different unique materials of the crown
unique_master_IDs = CROWN_Thesaurus_df["TermMasterID"].unique()

# creating a new df out of the KHM thesaurus where the rows match the unique IDs from the crown thesaurus
# so that only the rows of the KHM thesaurus are selected which contain crown materials
working_df = KHM_Thesaurus_df.loc[KHM_Thesaurus_df["TermMasterID"].isin(unique_master_IDs)]

for row in working_df.itertuples():
    URI = URIRef(BASE_URL + PID_THESAURUS + str(row.TermMasterID))
    output_graph.add((URI, RDF.type, SKOS.Concept))
    output_graph.add((URI, SKOS.inScheme, URIRef(BASE_URL + PID_THESAURUS)))
    if row.LanguageID == 5 and row.TermType == "Descriptor":
        output_graph.add((URI, SKOS.prefLabel, Literal(row.Term, lang="de")))
    elif (row.LanguageID == 9 or row.LanguageID == 1) and row.TermType == "Alternate Term" :
        output_graph.add((URI, SKOS.prefLabel, Literal(row.Term, lang="en")))
    elif row.LanguageID == 10019:
        output_graph.add((URI, SKOS.exactMatch, URIRef("http://vocab.getty.edu/aat/" + str(row.Term))))
   
    # getting the ID of the broader term by removing the last 3 letters, f. i. 
    # "AUT.AAA.AAN.AAA.AAH.AAB.AAC" --> "AUT.AAA.AAN.AAA.AAH.AAB"
    broader_term_ID = str(row.CN).rsplit(".", 1)[0]
    
    broader_URI, broader_term_ID = get_SKOS(URI, broader_term_ID)
    broader_URI, broader_term_ID = get_SKOS(broader_URI, broader_term_ID)
    # this condition ist needed because otherwise it will throw an index error because the 
    # broadest term in the excel sheet consists of 4 elements
    if len(broader_term_ID.split(".")) > 3:
        broader_URI, broader_term_ID = get_SKOS(broader_URI, broader_term_ID)
    if len(broader_term_ID.split(".")) > 3:
        broader_URI, broader_term_ID = get_SKOS(broader_URI, broader_term_ID)
              
########################################################################################
    

########################################################################################

output_graph.serialize(destination = 'rdf_output_indices/index_thesaurus.xml', format="pretty-xml", max_depth=1)