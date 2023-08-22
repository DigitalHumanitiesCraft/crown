#import csv
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, XSD
import pandas as pd
import re
from datetime import date
import xml.etree.ElementTree as ET
from collections import Counter

### global variables
########################################################################################
BASE_URL = "https://gams.uni-graz.at/"
PID = 'o:crown.object'

CROWN_Objects_2 = 'data/CROWN_Objects_2.xlsx'
CROWN_Objects_3_TextEntries = 'data/CROWN_Objects_3_TextEntries.xlsx'
CROWN_Objects_4_Constituents = 'data/CROWN_Objects_4_Constituents.xlsx'
CROWN_Objects_5_AltNumbers = 'data/CROWN_Objects_5_AltNumbers.xlsx'
CROWN_Objects_6_Medien = 'data/CROWN_Objects_6_Medien.xlsx'
CROWN_Restaurierung_1 = 'data/CROWN_Restaurierung_1.xlsx'
CROWN_Restaurierung_2 = 'data/CROWN_Restaurierung_2.xlsx'
CROWN_Restaurierung_3_Medien = 'data/CROWN_Restaurierung_3_Medien.xlsx'
Crown_Userfields = 'data/Crown_Userfields.xlsx'

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
def convert_carriage_return(string):
    '''This functions replaces ASCII code that stands for the carriage returns in the 
        excel sheets. It gets created when the files are read. The space after the 
        character is needed, otherwise there are two or more spaces in the string after
        the character is removed'''
    converted_string = string.replace("_x000D_ ", "").replace("_x000d_", "")
    return converted_string
########################################################################################
def getFileExtensions(column, URI):
    ''' This function checks the file extensions of the entries in a certain column and then
        adds the corresponding mime type to the graph. 
    '''
    # file extension is after the dot in the path; setting maxsplit to 1 to split only once beginning 
    # from the right side because sometimes there is a dot in the filenmame. Substring [1] then selects the file extension
    # Format starts with a capital "F" because ".format" is a Python method (can it be escaped?)
    extension = column.rsplit('.', 1)[1].lower()
    if extension == 'jpg':
        output_graph.add((URI, DCTERMS["format"], Literal('image/jpeg')))
    elif extension == 'png':
        output_graph.add((URI, DCTERMS["format"], Literal('image/png')))
    elif extension == 'txt':
        output_graph.add((URI, DCTERMS["format"], Literal('text/plain')))
    # Catching yet unconsidered/future formats
    else:
        output_graph.add((URI, DCTERMS["format"], Literal('Please consider this format!')))
########################################################################################
def convert_umlauts(string):
    characters = {'ä': 'ae', 'ü': 'ue', 'ö':'oe', 'Ä': 'Ae', 'Ü': 'Ue', 'Ö':'Oe'}
    table = string.maketrans(characters)
    translated_string = string.translate(table)
    return translated_string
########################################################################################
# Convert floats with just 0 after the dots to ints ("12.000" --> "12") and strips trailing zeroes ("6.3000" --> "6.3")
def convert_floats(string):
    string = str(string)
    string_without_0 = f'{string.rstrip("0").rstrip(".") if "." in string else string}'
    return string_without_0

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
# 
Crown_Userfields_df = pd.read_excel(Crown_Userfields, engine='openpyxl')
# reading mapping_userfields
userfields_xml = ET.parse("mapping_userfields.xml")
root = userfields_xml.getroot()

# for every row; every row is an object
for row in CROWN_Objects_2_df.itertuples(index=True, name='Crown'):

    # variables
    object_id = getattr(row, "ObjectID")
    objectNumber = normalizeStringforJSON(getattr(row, "ObjectNumber"))
    objectName = normalizeStringforJSON(str(getattr(row, "ObjectName")))
    
    
    
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
        VOID_Dataset = URIRef(BASE_URL + PID + "." + str(object_id))
        output_graph.add((VOID_Dataset, RDF.type, VOID.Dataset))
        # void 
        output_graph.add((VOID_Dataset, VOID.feature, URIRef("http://www.w3.org/ns/formats/RDF_XML")))
        output_graph.add((VOID_Dataset, VOID.dataDump, URIRef(BASE_URL + PID + '.' + str(object_id) + "/ONTOLOGY")))
        output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:crown.ontology#")))
        output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://gams.uni-graz.at/o:gams-ontology#")))
        output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("http://purl.org/dc/terms/")))
        output_graph.add((VOID_Dataset, VOID.vocabulary, URIRef("https://schema.org/")))
        output_graph.add((VOID_Dataset, DC.title, Literal((objectName + ', ' if objectName else '') + objectNumber)))
        output_graph.add((VOID_Dataset, DC.title, Literal((objectName + ', ' if objectName else '') + objectNumber)))
        objectDescription = convert_carriage_return(normalizeStringforJSON(str(getattr(row, "Description"))))
        output_graph.add((VOID_Dataset, DC.description, Literal((objectName + ', ' if objectName else '') + objectNumber +  (", " + objectDescription if objectDescription else ''))))
        # include dates
        output_graph.add((VOID_Dataset, DC.date, Literal(date.today().year)))
        output_graph.add((VOID_Dataset, DCTERMS.modified, Literal(date.today())))
        
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
        output_graph.add((VOID_Dataset, DC.subject, Literal("Sammlung", lang="en")))
        output_graph.add((VOID_Dataset, DC.publisher, Literal("Kunsthistorisches Museum, Wien")))

        # crown:Object
        crown_object = URIRef(BASE_URL + PID + '.' + str(object_id) + '.o')
        
        # Creating <crown:AdditionalMaterial> or <crown:Object>
        auth_value = getattr(row, "AuthValue") 
        if auth_value == "Kronreif" or auth_value == "Bügel" or auth_value == "Stirnkreuz" or (auth_value == "(nicht vergeben)" and objectName == "Reichskrone"):
            output_graph.add((crown_object, RDF.type, CROWN.Object))
        else:
            output_graph.add((crown_object, RDF.type, CROWN.AdditionalMaterial))
    

        # rdfs:label   
        if(pd.notnull(objectNumber)):
            # "Hochfassung für Perle mit Einsteckstiften, Test_AA_Fa_1" | "Test_AA_Fa_1"
            output_graph.add((crown_object, RDFS.label, Literal((objectName + ', ' if objectName else '') + objectNumber) ))
        # rdfs:comment
        if(pd.notnull( getattr(row, "Description") )):
            output_graph.add((crown_object, RDFS.comment, Literal(convert_carriage_return(normalizeStringforJSON(getattr(row, "Description"))))))
        # dct:medium
        if(pd.notnull(getattr(row, "Medium") )):
                # Works on 95 % of the cases, otherwise the data is to messy
                medium = getattr(row, "Medium")
                # if there isn't a separator followed by a capital letter, its 1 medium, f. e. "Gold" or "Spinell; rosa"
                if len(re.findall("(,|;) [A-Z]", medium)) == 0:
                    output_graph.add((crown_object, DCTERMS.medium, Literal(normalizeStringforJSON(medium.lstrip()))))
                # This condition is a bit hacky. If there is a separator followed by a lowercase letter
                # and the split string is rather short, its one medium. 
                if len(re.split(",|;", medium)) <= 3 and re.search("(,|;) [a-z]", medium):
                    output_graph.add((crown_object, DCTERMS.medium, Literal(normalizeStringforJSON(medium.lstrip()))))
                # Each other substring after a separator is most of the time a different medium
                else: 
                    split_medium = re.split(",|;", str(medium))
                    for single_medium in split_medium:
                            output_graph.add((crown_object, DCTERMS.medium, Literal(normalizeStringforJSON(single_medium.lstrip()))))
                    
        # dct:extent
        if(pd.notnull( getattr(row, "Dimensions") )):
            output_graph.add((crown_object, DCTERMS.extent, Literal( convert_carriage_return(normalizeStringforJSON( getattr(row, "Dimensions"))) ) ))

        # crown:analysesPerformed
        if(pd.notnull( getattr(row, "ShortText8") )):
            # Seperates the different analysis performed, seperator always seems to be ";"
            analysis = getattr(row, "ShortText8").split(sep=';')    
            for index, single_analysis in enumerate (analysis, 1): 
                crown_analysis = URIRef(BASE_URL + PID + '.' + str(object_id) + '.analysis.' + str(index))
                output_graph.add((crown_analysis, RDF.type, CROWN.Analysis))
                output_graph.add((crown_object, CROWN.analysisPerformed, crown_analysis))
                output_graph.add((crown_analysis, RDFS.label, Literal(normalizeStringforJSON(single_analysis.lstrip()))))

        # <gams:textualContent>     
        output_graph.add((crown_object, GAMS.textualContent, Literal(str((str(object_id) + ' ' + str(objectNumber) + ' ' + str(auth_value) + ' ' + str(objectName) 
        + ' ' + str(row.Dated if pd.isna(row.Dated) == False else "") + ' ' + convert_carriage_return(str(row.Medium if pd.isna(row.Medium) == False else ""))) + ' ' 
        + convert_carriage_return(str(row.Dimensions if pd.isna(row.ShortText8) == False else ""))  + ' ' + convert_carriage_return(str(row.Description) if pd.isna(row.Description) == False  else "") 
        + ' ' + convert_carriage_return(str(row.ShortText8 if pd.isna(row.ShortText8) == False else ""))).replace("    ", " ").replace("   ", " ").replace("  ", " ").rstrip())))
        
        # crown:dateBegin
        #if(pd.notnull( getattr(row, "DateBegin") )):
        #    output_graph.add((crown_object, CROWN.dateBegin, Literal(getattr(row, "DateBegin")) )) 
        # crown:dateEnd
        #if(pd.notnull( getattr(row, "DateEnd") )):
        #    output_graph.add((crown_object, CROWN.dateEnd, Literal(getattr(row, "DateEnd")) )) 

        # select via object_id all entries in sheet "Tech_Untersuchungen" representing an analysis
        # cp: check column name "Object ID" in new tms export
        object_analyses = CROWN_Restaurierung_1_df.loc[CROWN_Restaurierung_1_df['ID'] == object_id]
        for row in object_analyses.itertuples(index=True):
            
            # variable
            surveyType = normalizeStringforJSON(getattr(row, "SurveyType"))
            
            
            # GR: It works, but I have no idea why. Probably because "Raman" is always the last analysis (see code above) and the stuff here gets added to the last?
            output_graph.add((crown_analysis, RDF.type, CROWN.Analysis))
            output_graph.add((crown_object, CROWN.analysisPerformed, crown_analysis))
            output_graph.add((crown_analysis, RDFS.label, Literal( surveyType + ' des Objekts ' + objectNumber ) ))
            # crown:surveyType
            if(pd.notnull( getattr(row, "SurveyType") )):
                output_graph.add((crown_analysis, CROWN.surveyType, Literal(surveyType) )) 
            # crown:personInvolved
            # cp: check column name in new tms export
            # get examiner 1
            if(pd.notnull( getattr(row, "ExaminerID") )):
                personInvolved_URI = BASE_URL + 'o:crown.index.person#' + str(getattr(row, "ExaminerID"))
                personInvolved = URIRef(personInvolved_URI)
                output_graph.add((crown_analysis, CROWN.personInvolved, personInvolved))  
            # get examiner 2
            if(pd.notnull( getattr(row, "Examiner2ID") )):
                personInvolved_URI = BASE_URL + 'o:crown.index.person#' + str(getattr(row, "Examiner2ID"))
                personInvolved = URIRef(personInvolved_URI)
                output_graph.add((crown_analysis, CROWN.personInvolved, personInvolved))
            # crown:date
            if(pd.notnull( getattr(row, "SurveyISODate") )):
                output_graph.add((crown_analysis, CROWN.date, Literal(getattr(row, "SurveyISODate")) ))
            
            #####
            #CROWN_Restaurierung_2
            # select via ConditionID
            condition_id = getattr(row, "ConditionID")
            CROWN_Restaurierung_2_data = CROWN_Restaurierung_2_df.loc[CROWN_Restaurierung_2_df['ConditionID'] == condition_id]
            for index, row in enumerate(CROWN_Restaurierung_2_data.itertuples(index=True)):
                # crown:attributeType
                if(pd.notnull( getattr(row, "AttributeType") )):
                    output_graph.add((crown_analysis, CROWN.attributeType, Literal(convert_carriage_return(normalizeStringforJSON(getattr(row, "AttributeType")))) )) 
                # crown:briefDescription
                if(pd.notnull( getattr(row, "BriefDescription") )):
                    output_graph.add((crown_analysis, CROWN.briefDescription, Literal(convert_carriage_return(normalizeStringforJSON( getattr(row, "BriefDescription")) )))) 
                # crown:statment
                if(pd.notnull( getattr(row, "Statement") )):
                    output_graph.add((crown_analysis, CROWN.statement, Literal(convert_carriage_return(normalizeStringforJSON( getattr(row, "Statement"))) ) )) 
                # crown:proposal
                if(pd.notnull( getattr(row, "Proposal") )):
                    output_graph.add((crown_analysis, CROWN.proposal, Literal(convert_carriage_return(normalizeStringforJSON( getattr(row, "Proposal")) )) )) 
                # crown:treatment
                if(pd.notnull( getattr(row, "Treatment") )):
                    output_graph.add((crown_analysis, CROWN.treatment, Literal(convert_carriage_return(normalizeStringforJSON( getattr(row, "Treatment"))) ) )) 
                    
                #####
                #CROWN_Restaurierung_3_Medien
                # connection to files and media via ConditionID
                # select via CondLineItemID
                condLineItem_id = getattr(row, "CondLineItemID")
                CROWN_Restaurierung_3_Medien_data = CROWN_Restaurierung_3_Medien_df.loc[CROWN_Restaurierung_3_Medien_df['CondLineItemID'] == condLineItem_id]
                for row in CROWN_Restaurierung_3_Medien_data.itertuples(index=True): 
                    crown_analysis_media = URIRef(BASE_URL + PID + '.' + str(object_id) + '.media.' + str(getattr(row, "MediaMasterID" )))
                    output_graph.add((crown_analysis_media, RDF.type, CROWN.Media))
                    output_graph.add((crown_analysis, CROWN.media, crown_analysis_media))
                    # getting the file endings 
                    output_graph.add((crown_analysis_media, RDFS.label, Literal(getattr(row, "RenditionNumber" ))))
                    getFileExtensions(getattr(row, "FileName"), crown_analysis_media)
                   
                   # crown:path
        ####
        # CROWN_Objects_6_Medien
        CROWN_Objects_6_Medien_data = CROWN_Objects_6_Medien_df.loc[CROWN_Objects_6_Medien_df['ObjectID'] == object_id]
        for count, row in enumerate(CROWN_Objects_6_Medien_data.itertuples(index=True), 1):
            object_media = URIRef(BASE_URL + PID + '.' + str(getattr(row, "ObjectID")) + '.media.' + str(getattr(row, "MediaMasterID" )))
            output_graph.add((object_media, RDF.type, SCHEMA.MediaObject))
            output_graph.add((object_media, RDFS.label, Literal(getattr(row, "RenditionNumber" ))))
            output_graph.add((crown_object, CROWN.media, object_media))
            ImageObject = URIRef(BASE_URL + PID + '.' + str(object_id) + "/IMAGE." + str(count))
            output_graph.add((object_media, SCHEMA.image, ImageObject))
            output_graph.add((ImageObject, RDF.type, SCHEMA.ImageObject))
            # Changing the file endings to lower case; ".JPG" --> ".jpg"
            filename = getattr(row, "FileName").rsplit('.', 1)
            filename_lowercase_endings = filename[0] + '.' + filename[1].lower()
            output_graph.add((ImageObject, SCHEMA.contentURL, Literal(normalizeStringforJSON(filename_lowercase_endings))))
            # getting the file endings
            getFileExtensions(getattr(row, "FileName"), object_media)
            
        
        #####
        # CROWN_Objects_3_TextEntries
        text_entries = CROWN_Objects_3_TextEntries_df.loc[CROWN_Objects_3_TextEntries_df["Object_ID"] == object_id]
        for entry in text_entries.itertuples(index=True):
            if getattr(entry, "TextType") == "Transkription":
                output_graph.add((crown_object, CROWN.transcription, Literal(convert_carriage_return(normalizeStringforJSON((str(getattr(entry, "TextEntry"))))))))
            elif (getattr(entry, "TextType") == "Beschreibung" or getattr(entry, "TextType") == "Bildbeschreibung" or 
                 getattr(entry, "TextType") == "Beschreibung online @") :
                output_graph.add((crown_object, RDFS.comment, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "Inschrift":
                output_graph.add((crown_object, CROWN.inscription, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "Beschriftung":
                output_graph.add((crown_object, CROWN.label, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "Literaturzitat":
                output_graph.add((crown_object, SCHEMA.citation, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "FileMaker Daten":
                output_graph.add((crown_object, CROWN.filemakerdaten, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "FotoNr.":
                output_graph.add((crown_object, CROWN.fotonummer, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "Bemerkung":
                output_graph.add((crown_object, CROWN.bemerkung, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "Recherchenotiz":
                output_graph.add((crown_object, CROWN.recherchenotiz, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            elif getattr(entry, "TextType") == "Notiz":
                output_graph.add((crown_object, CROWN.note, Literal(convert_carriage_return(normalizeStringforJSON(str(getattr(entry, "TextEntry")))))))
            else:
                 output_graph.add((crown_object, CROWN.TextType, Literal("Please consider this text type")))
        
        # ####
        # CROWN_Objects_5_AltNumbers
        # For the time being everything is a "schema.identifier" because there are 41 values in "AltNumDescription"
        alt_numbers = CROWN_Objects_5_AltNumbers_df.loc[CROWN_Objects_5_AltNumbers_df["ID"]== object_id]
        for entry in alt_numbers.itertuples(index=True):
           output_graph.add((crown_object, SCHEMA.identifier, Literal(normalizeStringforJSON(str(getattr(entry, "AltNum")))))) 


        #####
        # CROWN_Userfields
        subdataframe = Crown_Userfields_df[Crown_Userfields_df.ID == object_id]

        # Initialize an empty counter (subclass of a dict) so that "wire" and "insertionpin" can be counted
        # f. e. "https://gams.uni-graz.at/o:crown.object.1467468.components.wire.1"
        path_counter = Counter()

        for string in subdataframe["UserFieldName"].astype('string'):
            # getting the entry that corresponds to the userfield string
            entry = root.find(".//entry[userfieldName ='%s']" % string)
            # check if entry exists for the string, if not it returns none and that produces an error when 
            # trying to get the property path in the next step
            if entry != None:
                # getting property path from this entry as a string, f. i. crown:components/crown:Granules/crown:number
                property_path = entry.find('propertyPath').text
                # processes only elements that have a property path in the xml file
                if property_path != " ":
                    # splits f. i. crown:components/crown:Granules/crown:number
                    split_path = property_path.split(sep="/")
                    if len(split_path) == 3 and split_path[2] != '':
                        # creating f. i. https://gams.uni-graz.at/o:crown.object.1480898.granules
                        first_URI = URIRef(BASE_URL + PID + '.' + str(object_id) + '.' + str(split_path[1].split(sep=":")[1].lower()))
                        # creating f. i. <crown:Granules rdf:about="https://gams.uni-graz.at/o:crown.object.1480898.granules">
                        # creating f. i. <crown:components>, its the first element of "split_path"
                        output_graph.add((crown_object, CROWN[f'{split_path[0].split(sep=":")[1]}'], first_URI))
                        output_graph.add((first_URI, RDF.type, URIRef(CROWN[split_path[1].split(sep=":")[1]])))
                        
                        # if there is a <range> element in the xml, create an object property   
                        if entry.find('range') != None:
                            range = entry.find('range').text
                            # if the the FieldValue corresponding to the UserfieldName is 1, take the whole range from the xml, f. e.: https://gams.uni-graz.at/o:crown.vocabulary#fromtubes
                            if subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values == "1":
                                output_graph.add((first_URI, CROWN[split_path[2].split(sep=":")[1]], URIRef(range)))
                            # else take only https://gams.uni-graz.at/o:crown.vocabulary# from the xml and combine it with the German string from the FieldValue, f. i. "verlötet"
                            else:
                                output_graph.add((first_URI, CROWN[split_path[2].split(sep=":")[1]], URIRef(range + normalizeStringforURI(convert_umlauts(subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values[0])))))                   
                        # else create a data property, f. e. <crown:comment>Perle an Fassung angebunden - Perle erstezt (?)</crown:comment>
                        else:
                            field_value = subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values[0]
                            output_graph.add((first_URI, CROWN[split_path[2].split(sep=":")[1]], Literal(convert_floats(field_value))))
                    
                    # f.i. crown:components/crown:PearlWireRings/crown:wire/crown:Wires/crown:onBaseplate
                    if len(split_path) == 5 and split_path[4] != '':

                        # See above for how this works
                        first_URI = URIRef(BASE_URL + PID + '.' + str(object_id) + '.' + split_path[1].split(sep=":")[1].lower())
                        output_graph.add((crown_object, CROWN[split_path[0].split(sep=":")[1]], first_URI))
                        output_graph.add((first_URI, RDF.type, URIRef(CROWN[split_path[1].split(sep=":")[1]])))
                        
                        # creates f. e. https://gams.uni-graz.at/o:crown.object.1467468.components.wire
                        second_URI_string = BASE_URL + PID + '.' + str(object_id) + '.' + split_path[0].split(sep=":")[1] + '.' + split_path[2].split(sep=":")[1].lower()

                        # if if there is a <countable> element in the xml, the URIs need to be enumerated (f. e. [...]wire.1)
                        if entry.find('countable') != None:
                            
                            # Adds the string the to the counter outside the for loop. The strings are the keys and how often they appear are the values. So if 
                            # there f. i are multiple "[...]wire" in an object, the first "wire" ends with ".1" since there is at first is only one 
                            # in the Counter. The second then ends with ".2" since there then are two of the same strings in the Counter which means
                            # that the value that corresponds to the key (=string) is then 2.

                            path_counter.update({second_URI_string})

                            # creates f. e. https://gams.uni-graz.at/o:crown.object.1467468.components.wire.1
                            second_URI = URIRef(second_URI_string + '.' + str(path_counter[f'{second_URI_string}']))

                            # creates for example 
                            # <crown:wire rdf:resource="https://gams.uni-graz.at/o:crown.object.1467468.components.wire.1"/>
                            # <crown:Wires rdf:about="https://gams.uni-graz.at/o:crown.object.1467468.components.wire.1"/> 
                            output_graph.add((first_URI, CROWN[f'{split_path[2].split(sep=":")[1]}'], second_URI))
                            # creates the singular of a class, f. i. "Wires" --> "Wire"
                            singular_subclass = split_path[3].split(sep=":")[1][:-1] if split_path[3].split(sep=":")[1][-1] == "s" else split_path[3].split(sep=":")[1]
                            output_graph.add((second_URI, RDF.type, URIRef(CROWN[singular_subclass])))
                        
                        # if there is no need for counting, just add the string as URI
                        else:
                            second_URI = URIRef(second_URI_string)
                            output_graph.add((first_URI, CROWN[split_path[2].split(sep=":")[1]], second_URI))
                            # creates the singular of a class, f. i. "Wires" --> "Wire"
                            singular_subclass = split_path[3].split(sep=":")[1][:-1] if split_path[3].split(sep=":")[1][-1] == "s" else split_path[3].split(sep=":")[1]
                            output_graph.add((second_URI, RDF.type, URIRef(CROWN[singular_subclass])))

                        # if there is a <range> element in the xml, create an object property   
                        if entry.find('range') != None:
                            range = entry.find('range').text
                            if subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values == "1":
                                output_graph.add((second_URI, CROWN[split_path[4].split(sep=":")[1]], URIRef(range)))
                            else:
                                output_graph.add((first_URI, CROWN[split_path[4].split(sep=":")[1]], URIRef(range + normalizeStringforURI(convert_umlauts(subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values[0])))))   
                        # else create a data property
                        else:
                            field_value = subdataframe.loc[subdataframe.UserFieldName == str(string), 'FieldValue'].values[0]
                            output_graph.add((second_URI, CROWN[split_path[4].split(sep=":")[1]], Literal(convert_floats(field_value))))

        ########################################################################################
        ### OUTPUT file .xml
        output_graph.serialize(destination = 'rdf_output/crown_object_' + str(object_id) + '.xml', format="pretty-xml")