#import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD
import pandas as pd
import re
import xml.etree.ElementTree as ET
from datetime import date
from reconciler import reconcile
from collections import Counter

### global variables
########################################################################################
BASE_URL = "https://gams.uni-graz.at/"
PID = 'o:crown.object'

# excel files
CROWN_Objects_2 = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Objects_2.xlsx'
CROWN_Objects_3_TextEntries = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Objects_3_TextEntries.xlsx'
CROWN_Objects_4_Constituents = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Objects_4_Constituents.xlsx'
CROWN_Objects_5_AltNumbers = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Objects_5_AltNumbers.xlsx'
CROWN_Objects_6_Medien = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Objects_6_Medien.xlsx'
CROWN_Restaurierung_1 = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Restaurierung_1.xlsx'
CROWN_Restaurierung_2 = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Restaurierung_2.xlsx'
CROWN_Restaurierung_3_Medien = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/CROWN_Restaurierung_3_Medien.xlsx'
Crown_Userfields = '//pers.ad.uni-graz.at/fs/ou/562/data/projekte/crown/data/Crown_Export_2023_03_07/Crown_Userfields_2023_03_07.xlsx'




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

def convert_umlauts(string):
    """
    Converts german umlauts
    """
    characters = {'ä': 'ae', 'ü': 'ue', 'ö':'oe', 'Ä': 'Ae', 'Ü': 'Ue', 'Ö':'Oe'}
    table = string.maketrans(characters)
    translated_string = string.translate(table)
    return translated_string

########################################################################################

def convert_floats(string):
    """
    Convert floats with just 0 after the dots to ints ("12.000" --> "12") and strips trailing 
    zeroes ("6.3000" --> "6.3")
    """
    string_without_0 = f'{string.rstrip("0").rstrip(".") if "." in string else string}'
    return string_without_0

########################################################################################

def create_first_URI(crown_object: URIRef, split_property_path: list):
    """
    Creates the first URI from the property path (f. i. crown:components/crown:Granules/crown:number),
    assigns a class to it and adds it to the crown_object URI.
    
    params
    ------
    URI : URIRef
        The crown_object URI

    split_property_path : list
        The split property path 
     ------
    Return : first_URI       
    """

    # creating f. i. https://gams.uni-graz.at/o:crown.object.1480898.granules
    first_URI = URIRef(BASE_URL + PID + '.' + str(object_id) + '.' + str(split_property_path[1].split(sep=":")[1].lower()))
    # creating f. i. <crown:Granules rdf:about="https://gams.uni-graz.at/o:crown.object.1480898.granules">
    # creating f. i. <crown:descriptionOfComponents>, its the first element of "split_property_path"
    output_graph.add((crown_object, CROWN[f'{split_property_path[0].split(sep=":")[1]}'], first_URI))
    output_graph.add((first_URI, RDF.type, URIRef(CROWN[split_property_path[1].split(sep=":")[1]])))

    return first_URI

########################################################################################

def add_second_URI(first_URI: URIRef, split_property_path: list, second_URI: URIRef):
    """
    Adds the second_URI to the first URI and assigns a class to the former. 
    
     params
    ------
    first_URI : URIRef
        The first URI

    split_property_path : list
        The split property path 

    second_URI    
     ------
        The second URI
    """
    # creates f. i. <crown:wire rdf:resource="https://gams.uni-graz.at/o:crown.object.1467468.wire.1"/>
    # <crown:Wire rdf:about="https://gams.uni-graz.at/o:crown.object.1467468.wire.1"/> 
    output_graph.add((first_URI, CROWN[split_property_path[2].split(sep=":")[1]], second_URI))
    output_graph.add((second_URI, RDF.type, URIRef(CROWN[split_property_path[3].split(sep=":")[1]])))

########################################################################################

def create_range_property(URI: URIRef, len_split_property_path: int, split_property_path: list, field_value: str):
    """
    Creates a range property. If the FieldValue is "1", the whole range is taken from 
    the mapping_userfields xml (f. i. https://gams.uni-graz.at/o:crown.vocabulary#fromtubes).
    If the FieldValue is anything else (besides "1" or "0"), just the part before the "#" is 
    taken from the mapping xml and it is combined with the german FieldValue (f. i.
    https://gams.uni-graz.at/o:crown.vocabulary#verloetet)
    
    params
    ------
    URI : URIRef
        The URI to which the range property gets added

    len_split_property_path : int
        The length of the split property path, 3 or 5    
    
    field_value : str
        The FieldValue from the excel sheet f. i. "verlötet"
    """
    
    range = mappingfile_entry.find('range').text

    # This is needed to accomodate the different path lengths in the range creation
    # f. i. crown:components/crown:DrillHole/crown:alignment (take "alignment" = third element = [2]) or
    # or crown:components/crown:InsertionPins/crown:insertionPin/crown:InsertionPins/crown:has (take "has" = 
    # fifth element = [4])
    split_position = 2 if len_split_property_path == 3 else 4

    if field_value == "0":
        return
    elif field_value == "1":
        output_graph.add((URI, CROWN[split_property_path[split_position].split(sep=":")[1]], URIRef(range)))
    else:
        output_graph.add((URI, CROWN[split_property_path[split_position].split(sep=":")[1]], URIRef(range + 
        normalizeStringforURI(convert_umlauts(field_value)))))

########################################################################################

def create_data_property(URI: URIRef, len_split_property_path: int, split_property_path: list, field_value: str): 
    """
    Creates a data property.
    
    params
    ------
    URI : URIRef
        The URI to which the data property gets added

    len_split_property_path : int
        The length of the split property path, 3 or 5  

    split_property_path: list
        The split property path

    field_value : str
        The FieldValue from the excel sheet f. i. "verlötet"
    """ 

    #   This is needed to accomodate the different path lengths f. i. crown:components/crown:DrillHole/crown:alignment 
    # (take "alignment" = third element = [2]) or crown:components/crown:InsertionPins/crown:insertionPin/crown:InsertionPins/crown:has 
    # (take "has" = fifth element = [4])
    split_position = 2 if len_split_property_path == 3 else 4

    output_graph.add((URI, CROWN[split_property_path[split_position].split(sep=":")[1]], Literal(convert_floats(field_value))))

########################################################################################

def reconcile_userfields(userfield_name: str, field_value: str, instance_of: str, added_string: str):
    """
    Reconciles the FieldValue of the Crown_Userfields excel sheet against Wikidata. First
    a Pandas dataframe is created from a dict, because that is the needed input for the 
    reconciler, f. i. {"Farbe": "rosa"}. The reconciler returns a pandas dataframe with 
    multiple columns, the most important one is "match" (values: "True" or "False"). If "match" 
    is true the (wikidata) "id" column from the dataframe is accessed and an object property 
    with a Wikidata url corresponding to the FieldValue is created, f. i. "https://www.wikidata.org/entity/Q1088" 
    for "blue". If the reconciliation is not successful, a data property is created.

    params
    ------
    userfield_name : str
        The UserfieldName from the excel sheet, f. i. "Farbe"
    
    field_value : str
        The FieldValue from the excel sheet, f. i. "rosa"

    instance_of : str
        The Wikidata "instance of" property to reconcile against, f. i. "Q1075" for color

    added_string : str
        The string that gets added to the field value to finetune the search, f. i. "Farbe"
    """

    userfield_df = pd.DataFrame({userfield_name: [field_value]})
    reconciled_df = reconcile(userfield_df[f"{userfield_name}"], type_id = instance_of)
    # if the field_value is not found at all at wikidata, the cell value of id is NaN. If this is not the case
    # a match is found and it can be checked if its a true match
    if reconciled_df["id"].isnull().values[0] == False:
        # check f. i. if the field_value produces a true match                      
        if check_for_match(reconciled_df):
            return
        # else add f. i. "Farbe" to "rosa" and try again
        else:
            userfield_df.at[0, userfield_name] = field_value + added_string
            reconciled_df = reconcile(userfield_df[f"{userfield_name}"], type_id = instance_of)
            if check_for_match(reconciled_df):
                return
            else:
                output_graph.add((first_URI, CROWN[split_property_path[2].split(sep=":")[1]], Literal(field_value)))
    else:
        output_graph.add((first_URI, CROWN[split_property_path[2].split(sep=":")[1]], Literal(field_value)))

########################################################################################

def check_for_match(reconciled_df: pd.DataFrame):
    """
    Checks if the column value for "match" in the reconciled pandas dataframe is "True". 
    If this is the case, an object property with the wikidata url is created, f. i.
    https://www.wikidata.org/entity/Q1088. Returns "True" if its a match.
    
    params
    ------
    userfield_name : pd.Dataframe
        A reconciled pandas dataframe returned by the reconciler library
    ------
    Return : True 
    """

    if (reconciled_df["match"].values[0] == True):                          
            id = reconciled_df["id"].values[0]
            output_graph.add((first_URI, CROWN[split_property_path[2].split(sep=":")[1]], URIRef(f"https://www.wikidata.org/entity/{id}")))
            return True

########################################################################################
### MAIN
########################################################################################
# Objektinformationen
CROWN_Objects_2_df = pd.read_excel(CROWN_Objects_2, engine='openpyxl')
# 
CROWN_Objects_3_TextEntries_df = pd.read_excel(CROWN_Objects_3_TextEntries, engine='openpyxl')
# 
CROWN_Objects_4_Constituents_df = pd.read_excel(CROWN_Objects_4_Constituents, engine='openpyxl')
# 
CROWN_Objects_5_AltNumbers_df = pd.read_excel(CROWN_Objects_5_AltNumbers, engine='openpyxl')
# 
CROWN_Objects_6_Medien_df = pd.read_excel(CROWN_Objects_6_Medien, engine='openpyxl')
# Object_ID | ObjectNumber | ExaminerID | dbo_Constituents_DisplayName | Examiner2ID | dbo_Constituents_1_DisplayName | SurveyISODate | SurveyType | Project | ConditionID
CROWN_Restaurierung_1_df = pd.read_excel(CROWN_Restaurierung_1, engine='openpyxl')
# 
CROWN_Restaurierung_2_df = pd.read_excel(CROWN_Restaurierung_2, engine='openpyxl')
# 
CROWN_Restaurierung_3_Medien_df = pd.read_excel(CROWN_Restaurierung_3_Medien, engine='openpyxl')
# das geht irgednwie nicht zum laden ... 
Crown_Userfields_df = pd.read_excel(Crown_Userfields, engine='openpyxl')

# reading mapping_userfields
userfields_xml = ET.parse("mapping_userfields.xml")
root = userfields_xml.getroot()

# Creating graph, Void-Dataset and Object

 # variables
object_id = 1467471

if(pd.notnull(object_id)):
    # make a graph
    output_graph = Graph()
    GAMS = Namespace("https://gams.uni-graz.at/o:gams-ontology#")
    VOID = Namespace("http://rdfs.org/ns/void#")
    DCTERMS = Namespace("http://purl.org/dc/terms/")
    DC = Namespace("http://purl.org/dc/elements/1.1/")
    CROWN = Namespace("https://gams.uni-graz.at/o:crown.ontology#")
    SCHEMA = Namespace("https://schema.org/")

    # define namespace in output file
    output_graph.bind("gams", GAMS)
    output_graph.bind("void", VOID)
    output_graph.bind("dcterms", DCTERMS)
    output_graph.bind("dc", DC)
    output_graph.bind("crown", CROWN)
    output_graph.bind("schema", SCHEMA)

    # void:Dataset
    VOID_Dataset = URIRef(BASE_URL + PID + str(object_id))
    output_graph.add((VOID_Dataset, RDF.type, VOID.Dataset))
    # void 
    output_graph.add((VOID_Dataset, VOID.feature, URIRef("http://www.w3.org/ns/formats/RDF_XML")))
    output_graph.add((VOID_Dataset, VOID.dataDump, URIRef(BASE_URL + PID + '.' + str(object_id) + "/ONTOLOGY")))
    output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:crown.ontology#")))
    output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:gams-ontology#")))
    output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("http://purl.org/dc/terms/")))
    #if(pd.notnull(getattr(row, "DateBegin")) and pd.notnull(getattr(row, "DateEnd"))):
    #    output_graph.add((VOID_Dataset, DC.date, Literal( str(getattr(row, "DateBegin")) + '-' + str(getattr(row, "DateEnd"))  ) ))
    #else:
    #    output_graph.add((VOID_Dataset, DC.date, Literal( str(getattr(row, "DateBegin")) ) ))
    output_graph.add((VOID_Dataset, DC.language, Literal('ger') ))
    output_graph.add((VOID_Dataset, DC.source, Literal('KHM') ))
    # static metadata
    output_graph.add((VOID_Dataset, DC.relation, Literal( "CROWN. Untersuchungen zu Materialität, Technologie und Erhaltungszustand der Wiener Reichskrone." ) ))
    output_graph.add((VOID_Dataset, DC.relation, Literal( "http://gams.uni-graz.at/crown" ) ))
    output_graph.add((VOID_Dataset, DC.publisher, Literal( "Institute Centre for Information Modelling, University of Graz" ) ))
    output_graph.add((VOID_Dataset, DC.rights, Literal( "Creative Commons BY 4.0" ) ))
    output_graph.add((VOID_Dataset, DC.rights, Literal( "https://creativecommons.org/licenses/by/4.0" ) ))
    # include date of the file transformation as dcterms:modified 
    output_graph.add((VOID_Dataset, DCTERMS.modified, Literal(date.today())))


    # crown:Object
    crown_object = URIRef(BASE_URL + PID + str(object_id) + '.o')
    output_graph.add((crown_object, RDF.type, CROWN.Object))

# Developing and testing the object and userfields mapping
# rosa: 1480887 blau; milchig: 1480888 milchig weißlich hellblau mit dunklen schlieren: 1480559
# dunkelblau: 1481019 1.Perldrahtring auf Grundplatte: 1481728 

subdataframe = Crown_Userfields_df[Crown_Userfields_df.ID == 1481728]

for string in subdataframe["UserFieldName"].astype('string'):
    # getting the entry that corresponds to the userfield string from the mapping xml
    mappingfile_entry = root.find(".//entry[userfieldName ='%s']" % string)
    # get the fieldValue corresponding to the UserFieldName
    field_value = subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values[0]
    # check if entry exists for the string, if not it returns none and that produces an error when 
    # trying to get the property path in the next step
    if mappingfile_entry != None:
        # getting property path from this entry as a string, f. i. crown:components/crown:Granules/crown:number
        property_path = mappingfile_entry.find('propertyPath').text
        # processes only elements that have a property path in the xml file
        if property_path != " ":
            # splits f. i. crown:components/crown:Granules/crown:number
            split_property_path = property_path.split(sep="/")
            len_split_property_path = len(split_property_path)
            if (len_split_property_path == 3 and split_property_path[2] != '') and (convert_floats(field_value) != "0" and (field_value != "(not assigned)")):
                
                first_URI = create_first_URI(crown_object, split_property_path)
                
                # creating rdfs:label
                rdfs_label_string = string.split(sep=":")[0]
                output_graph.add((first_URI, RDFS.label, Literal(rdfs_label_string)))
                
                # if there is a <range> element in the xml, create an object property   
                if mappingfile_entry.find('range') != None:
                    create_range_property(first_URI, len_split_property_path, split_property_path, field_value)
                
                # if there is a <reconciliation> element in the mapping xml, try to reconcile the FieldValue (f. i. "blau")
                elif mappingfile_entry.find('reconciliation') != None:
                    userfield_name = mappingfile_entry.find('userfieldName').text
                    # try to get first substring of userfieldName, f. i. "grün" from "grün; opak"
                    field_value = field_value.split(sep=";")[0] if ";" in field_value else field_value
                                        
                    if userfield_name == "Farbe":
                        reconcile_userfields(userfield_name, field_value, instance_of="Q1075", added_string=" Farbe")
                    
                # else create a data property, f. e. <crown:comment>Perle an Fassung angebunden - Perle erstezt (?)</crown:comment>
                else:
                    create_data_property(first_URI, len_split_property_path, split_property_path, field_value)
                
            # f.i. crown:descriptionOfComponents/crown:PearlWireRing/crown:wire/crown:Wires/crown:onBaseplate
            if (len_split_property_path == 5 and split_property_path[4] != '') and ((convert_floats(field_value) != "0") and (field_value != "(not assigned)")):

                first_URI = create_first_URI(crown_object, split_property_path)

                # creates f. e. https://gams.uni-graz.at/o:crown.object.1467468.wire
                second_URI_string = BASE_URL + PID + '.' + str(object_id) + '.' + split_property_path[2].split(sep=":")[1].lower()
                second_URI = URIRef(second_URI_string)

                # if if there is a <count> element in the xml, the URIs need to be enumerated (f. i. [...] wire.1)
                mappingfile_count_entry = mappingfile_entry.find('count')
                if mappingfile_count_entry != None:
                    second_URI = URIRef(second_URI_string + '.' + str(mappingfile_count_entry.text))
                    add_second_URI(first_URI, split_property_path, second_URI)
                
                # if there is no <count> element, just add the string as URI
                else:
                    add_second_URI(first_URI, split_property_path, second_URI)

                # if there is a <range> element in the mapping xml, create an object property   
                if mappingfile_entry.find('range') != None:
                    create_range_property(second_URI, len_split_property_path, split_property_path, field_value)
                
                # else create a data property, f. e. <crown:comment>Perle an Fassung angebunden - Perle erstezt (?)</crown:comment>
                else:
                    create_data_property(second_URI, len_split_property_path, split_property_path, field_value)

########################################################################################
### OUTPUT file .xml
output_graph.serialize(destination = 'crown_object_' + str(object_id) + '.xml', format="pretty-xml", max_depth=5)