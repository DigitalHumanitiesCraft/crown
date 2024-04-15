import logging
import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD, SKOS
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logging.basicConfig(filename='crown_ontology_errors.log', level=logging.INFO, format='%(asctime)s %(message)s')


def create_data_property_static(g, namespace, property_name, domain, label_de, label_en, comment_de, comment_en):
    
    property_uri = namespace[property_name]
    domain_uri = namespace[domain]
    g.add((property_uri, RDF.type, RDF.Property))
    g.add((property_uri, RDFS.domain, domain_uri))
    g.add((property_uri, RDFS.range, XSD.string))
    g.add((property_uri, RDFS.label, Literal(label_de, lang="de")))
    g.add((property_uri, RDFS.label, Literal(label_en, lang="en")))
    g.add((property_uri, RDFS.comment, Literal(comment_de, lang="de")))
    g.add((property_uri, RDFS.comment, Literal(comment_en, lang="en")))



def create_skos_concept(g, concept_name, label_de=None, label_en=None, comment_de=None, comment_en=None):
    if 'crownvoc:' in property_path[-1]:
        concept_name = normalize_name(property_path[-1].split('crownvoc:')[1])
        concept_uri = CROWN_VOC[concept_name]
        g.add((concept_uri, RDF.type, SKOS.Concept))
        if label_de:
            g.add((concept_uri, SKOS.prefLabel, Literal(label_de, lang="de")))
        if label_en:
            g.add((concept_uri, SKOS.prefLabel, Literal(label_en, lang="en")))
        if comment_de:
            g.add((concept_uri, RDFS.comment, Literal(comment_de, lang="de")))
        if comment_en:
            g.add((concept_uri, RDFS.comment, Literal(comment_en, lang="en")))
    else:
        logging.info(f'Error in line: {property_path} - "crownvoc:" not found')

def get_datatype(datatype):
    if datatype == "integer":
        return XSD.integer
    if datatype == "float":
        return XSD.float
    elif datatype == "text":
        return XSD.string
    elif datatype == "uri":
        return XSD.anyURI
    else:
        return XSD.string

def create_data_property(g, namespace, property_name, datatype, label_de=None, label_en=None, comment_de=None, comment_en=None):
    property_uri = namespace[property_name]
    g.add((property_uri, RDF.type, RDF.Property))
    g.add((property_uri, RDFS.range, datatype))
    if label_de:
        g.add((property_uri, RDFS.label, Literal(label_de, lang="de")))
    if label_en:
        g.add((property_uri, RDFS.label, Literal(label_en, lang="en")))
    if comment_de:
        g.add((property_uri, RDFS.comment, Literal(comment_de, lang="de")))
    if comment_en:
        g.add((property_uri, RDFS.comment, Literal(comment_en, lang="en")))

def create_object_property(g, namespace, property_name, domain, range_, label_de, label_en, comment_de, comment_en):
    property_uri = namespace[property_name]
    g.add((property_uri, RDF.type, RDF.Property))
    g.add((property_uri, RDFS.domain, namespace[domain]))
    g.add((property_uri, RDFS.range, namespace[range_]))
    g.add((property_uri, RDFS.label, Literal(label_de, lang="de")))
    g.add((property_uri, RDFS.label, Literal(label_en, lang="en")))
    g.add((property_uri, RDFS.comment, Literal(comment_de, lang="de")))
    g.add((property_uri, RDFS.comment, Literal(comment_en, lang="en")))

def normalize_name(name):
    return name.replace(" ", "")

SERVICE_ACCOUNT_FILE = '/home/chrisi/Documents/GitHub/CROWN/data/credentials.json'
SPREADSHEET_ID = '1Z-vb1JVzQ3dndH8Cxt_Bs5XQnKIDrKj_PR1A4xDnEYE'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = None
creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)
# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='flexfields').execute()
values = result.get('values', [])

if not values:
    print('No data found.')
else:
    header = values[0]
    data = values[1:]

    df = pd.DataFrame(data, columns=header)
    df = df[["UserfieldName: german", "UserfieldName: english", "definition: german", "definition: english", "Property Path", "Datatype"]]

    g = Graph()
    CROWN = Namespace("https://gams.uni-graz.at/o:ontology.crown#")
    CROWN_VOC = Namespace("https://gams.uni-graz.at/o:crown.vocabulary#")


    # Initialize a set to store unique class names
    class_names = set()

    # Adding the specified object properties
    object_properties = {
    "analysisPerformed": {
        "domain": "Object",
        "range": "Analysis",
        "label_de": "Analyse durchgeführt",
        "label_en": "Analysis Performed",
        "comment_de": "Verknüpft ein Objekt mit der durchgeführten Analyse.",
        "comment_en": "Links an object to the performed analysis."
    },
    "descriptionOf": {
        "domain": "Object",
        "range": "Component",
        "label_de": "Beschreibung von",
        "label_en": "Description of",
        "comment_de": "Verknüpft ein Objekt mit seiner Beschreibung über eine Komponente.",
        "comment_en": "Links an object to a components description."
    },
    "conditionReported": {
        "domain": "Object",
        "range": "Condition",
        "label_de": "Zustand berichtet",
        "label_en": "Condition Reported",
        "comment_de": "Verknüpft ein Objekt mit einem Bericht über seinen Zustand.",
        "comment_en": "Links an object to a report of its condition."
    },
    "component": {
        "domain": "Object",
        "range": "Component",
        "label_de": "Komponente",
        "label_en": "Component",
        "comment_de": "Verknüpft ein Objekt mit seinen Komponenten.",
        "comment_en": "Links an object to its components."
    },
    "materialUsed": {
        "domain": "Object",
        "range": "Material",
        "label_de": "Verwendetes Material",
        "label_en": "Material Used",
        "comment_de": "Verknüpft ein Objekt mit dem verwendeten Material.",
        "comment_en": "Links an object to the material used."
    },
    "documentation": {
        "domain": "Object",
        "range": "Documentation",
        "label_de": "Dokumentation",
        "label_en": "Documentation",
        "comment_de": "Verknüpft ein Objekt mit seiner Dokumentation.",
        "comment_en": "Links an object to its documentation."
    }
}

    for prop, details in object_properties.items():
        create_object_property(g, CROWN, prop, details['domain'], details['range'], details['label_de'], details['label_en'], details['comment_de'], details['comment_en'])

    # Top-level classes with labels and comments
    top_level_classes = {
        "Object": {
            "label_de": "Objekt",
            "label_en": "Object",
            "comment_de": "Ein Objekt im CROWN Projekt: ein Komponent der Reichskrone.",
            "comment_en": "A Object in the CROWN Project: a component of the Crown."
        },
        "Analysis": {
            "label_de": "Analyse",
            "label_en": "Analysis",
            "comment_de": "Klasse für verschiedene Arten von Analysen.",
            "comment_en": "Class for various types of analyses."
        },
        "Condition": {
            "label_de": "Zustand",
            "label_en": "Condition",
            "comment_de": "Klasse zur Beschreibung des Zustands von Objekten.",
            "comment_en": "Class for describing the condition of objects."
        },
        "Component": {
            "label_de": "Komponente",
            "label_en": "Component",
            "comment_de": "Klasse für verschiedene Komponenten oder Teile von Objekten.",
            "comment_en": "Class for different components or parts of objects."
        }
    }

    # Adding top-level classes to the RDF graph
    for class_name, details in top_level_classes.items():
        class_uri = CROWN[class_name]
        g.add((class_uri, RDF.type, RDFS.Class))
        g.add((class_uri, RDFS.label, Literal(details["label_de"], lang="de")))
        g.add((class_uri, RDFS.label, Literal(details["label_en"], lang="en")))
        g.add((class_uri, RDFS.comment, Literal(details["comment_de"], lang="de")))
        g.add((class_uri, RDFS.comment, Literal(details["comment_en"], lang="en")))


    analysis_classes = {
    "XRFAnalysis": (
        "XRF-Analyse", 
        "XRF Analysis", 
        "Klasse für XRF-Analysen.", 
        "Class for XRF analyses."
    ),
    "FORSAnalysis": (
        "FORS-Analyse", 
        "FORS Analysis", 
        "FORS (Fiber Optics Reflectance Spectroscopy) ist eine Technik zur Untersuchung der optischen Eigenschaften von Materialien.", 
        "FORS (Fiber Optics Reflectance Spectroscopy) is a technique used to study the optical properties of materials."
    ),
    "RamanAnalysis": (
        "Raman-Analyse", 
        "Raman Analysis", 
        "Raman-Spektroskopie ist eine analytische Technik zur Beobachtung von Schwingungs-, Rotations- und anderen niederfrequenten Modi in einem System.", 
        "Raman spectroscopy is an analytical technique used to observe vibrational, rotational, and other low-frequency modes in a system."
    ),
    "InterventionXRFAnalysis": (
        "Interventions-XRF-Analyse", 
        "Intervention XRF Analysis", 
        "Interventions-XRF-Analyse bezieht sich auf die Anwendung der XRF-Technik zur Untersuchung von Objekten nach einer Restaurierung oder Konservierung.", 
        "Intervention XRF Analysis refers to the application of XRF technique to study objects following restoration or conservation interventions."
    ),
    "EnamelMuRamanAnalysis": (
        "Email µ-Raman-Analyse", 
        "Enamel µ-Raman Analysis", 
        "Email µ-Raman-Analyse ist eine spezialisierte Form der Raman-Spektroskopie, die sich auf die Untersuchung von Emailmaterialien konzentriert.", 
        "Enamel µ-Raman Analysis is a specialized form of Raman spectroscopy focused on the study of enamel materials."
    ),
    "EnamelXRFAnalysis": (
        "Email XRF-Analyse", 
        "Enamel XRF Analysis", 
        "Email XRF-Analyse verwendet die XRF-Technik, um die Elementzusammensetzung von Emailoberflächen zu bestimmen.", 
        "Enamel XRF Analysis uses XRF technique to determine the elemental composition of enamel surfaces."
    ),
    "PearlRamanAnalysis": (
        "Perlen-Raman-Analyse", 
        "Pearl Raman Analysis", 
        "Perlen-Raman-Analyse ist eine Anwendung der Raman-Spektroskopie zur Untersuchung der molekularen Struktur von Perlen.", 
        "Pearl Raman Analysis is an application of Raman spectroscopy for investigating the molecular structure of pearls."
    ),
    "PearlXRFAnalysis": (
        "Perlen-XRF-Analyse", 
        "Pearl XRF Analysis", 
        "Perlen-XRF-Analyse wird verwendet, um die chemische Zusammensetzung von Perlenoberflächen mittels XRF-Technik zu analysieren.", 
        "Pearl XRF Analysis is used to analyze the chemical composition of pearl surfaces using XRF technique."
    ),
    "GemstoneXRFAnalysis": (
        "Edelstein-XRF-Analyse", 
        "Gemstone XRF Analysis", 
        "Edelstein-XRF-Analyse nutzt die XRF-Spektroskopie, um die Elementzusammensetzung von Edelsteinen zu bestimmen.", 
        "Gemstone XRF Analysis utilizes XRF spectroscopy to determine the elemental composition of gemstones."
    )
}
    for class_name, labels_comments in analysis_classes.items():
        class_uri = CROWN[class_name]
        g.add((class_uri, RDF.type, RDFS.Class))
        g.add((class_uri, RDFS.subClassOf, CROWN.Analysis))
        g.add((class_uri, RDFS.label, Literal(labels_comments[0], lang="de")))
        g.add((class_uri, RDFS.label, Literal(labels_comments[1], lang="en")))
        g.add((class_uri, RDFS.comment, Literal(labels_comments[2], lang="de")))
        g.add((class_uri, RDFS.comment, Literal(labels_comments[3], lang="en")))

    component_classes = {
    "Grooves": (
        "Rillen", 
        "Grooves", 
        "Rillen sind Kerben oder Einkerbungen an Objekten, häufig zur Verzierung oder Funktionalität, wie sie in historischen Kronen zu finden sind.", 
        "Grooves are notches or indentations on objects, often for decoration or functionality, as found in historical crowns."
    ),
    "Ribs": (
        "Rippen", 
        "Ribs", 
        "Rippen sind erhabene Streifen oder Leisten, die zur Verstärkung oder Dekoration an Objekten, insbesondere in metallischen Komponenten historischer Kronen, angebracht sind.", 
        "Ribs are raised strips or ridges applied to objects for reinforcement or decoration, especially in metallic components of historical crowns."
    ),
    "Wire": (
        "Draht", 
        "Wire", 
        "Draht in historischen Kronen bezieht sich auf Metallfäden, die für Struktur, Verbindung oder Verzierung verwendet werden, oft mit spezifischen Durchmessern und Windungsrichtungen.", 
        "Wire in historical crowns refers to metal threads used for structure, connection, or decoration, often with specific diameters and winding directions."
    ),
    "WireBinding": (
        "Drahtbindung", 
        "Wire Binding", 
        "Drahtbindung ist eine Technik zur Befestigung oder Verbindung von Komponenten in historischen Kronen, wobei Draht verwendet wird, um Teile zusammenzuhalten.", 
        "Wire binding is a technique for fastening or connecting components in historical crowns, using wire to hold parts together."
    ),
    "Granule": (
        "Granalie", 
        "Granule", 
        "Granalien sind kleine, kugelförmige Partikel, oft aus Metall, die in der Verzierung historischer Kronen und Schmuckstücke verwendet werden, um Detailreichtum und Textur zu erzeugen.", 
        "Granules are small, spherical particles, often made of metal, used in the decoration of historical crowns and jewelry to create detail and texture."
    ),
     "Rivets": (
        "Niete",
        "Rivets",
        "Nieten sind metallische Befestigungselemente, die zur Verbindung von Teilen in historischen Kronen verwendet werden, oft erkennbar an charakteristischen Werkzeugspuren.",
        "Rivets are metallic fasteners used to join parts in historical crowns, often identifiable by characteristic tool traces."
    ),
    "Enamel": (
        "Email",
        "Enamel",
        "Email, eine glasartige Beschichtung, wird in historischen Kronen verwendet, um Oberflächen zu verzieren und zu schützen, häufig in leuchtenden Farben und komplexen Mustern.",
        "Enamel, a glass-like coating, is used in historical crowns to decorate and protect surfaces, often in vibrant colors and intricate patterns."
    ),
    "PearlWireRing": (
        "Perldrahtring",
        "Pearl Wire Ring",
        "Perldrahtringe sind feine, kreisförmige Metalldrähte, die in der Herstellung historischer Kronen verwendet werden, oft zur Halterung von Perlen oder als dekoratives Element.",
        "Pearl wire rings are fine, circular metal wires used in the making of historical crowns, often for holding pearls or as a decorative element."
    ),
    "GranulesWithPearlWireRings": (
        "Granalien mit Perldrahtringen",
        "Granules with Pearl Wire Rings",
        "Diese Kombination aus kleinen Granalien und Perldrahtringen wird in der Verzierung historischer Kronen eingesetzt, um eine zusätzliche Dimension der Feinheit und Detailtreue zu erreichen.",
        "This combination of small granules and pearl wire rings is used in the decoration of historical crowns to achieve an added dimension of finesse and detail."
    ),
    "Claws": (
        "Krallen",
        "Claws",
        "Krallen sind kleine, hakenförmige Metallelemente, die in historischen Kronen zur Befestigung von Edelsteinen und anderen Dekorationselementen dienen.",
        "Claws are small, hook-shaped metal elements used in historical crowns to secure gemstones and other decorative pieces."
    ),
    "Loops": (
        "Schlaufen",
        "Loops",
        "Schlaufen sind ring- oder schleifenförmige Elemente in historischen Kronen, die sowohl dekorative als auch funktionale Zwecke erfüllen, wie das Verbinden von Komponenten.",
        "Loops are ring- or loop-shaped elements in historical crowns serving both decorative and functional purposes, such as connecting components."
    ),
    "PearlWire": (
        "Perldraht",
        "Pearl Wire",
        "Perldraht bezeichnet dünne, flexible Metalldrähte in historischen Kronen, oft verwendet, um Perlen zu halten oder feine Details zu erstellen.",
        "Pearl wire refers to thin, flexible metal wires in historical crowns, often used to hold pearls or create fine details."
    ),
    "Tubes": (
        "Röhrchen",
        "Tubes",
        "Röhrchen in historischen Kronen sind kleine, zylindrische Komponenten, verwendet für strukturelle Zwecke oder als Halterungen für kleinere Schmuckelemente.",
        "Tubes in historical crowns are small, cylindrical components used for structural purposes or as mounts for smaller jewelry elements."
    ),
    "Bezel": (
        "Zarge",
        "Bezel",
        "Die Zarge ist ein ringförmiger Metallrahmen in historischen Kronen, der dazu dient, Edelsteine sicher zu fassen und hervorzuheben.",
        "The bezel is a ring-shaped metal frame in historical crowns, serving to securely set and highlight gemstones."
    ),
    "UShapedClamps": (
        "bügelförmige Klammern",
        "U-shaped Clamps",
        "Bügelförmige Klammern sind U-förmige Befestigungselemente in historischen Kronen, die für das Zusammenhalten von Teilen oder als strukturelle Verstärkungen eingesetzt werden.",
        "U-shaped clamps are U-shaped fasteners in historical crowns used for holding parts together or as structural reinforcements."
    ),
     "AssemblyTubes": (
        "Montageröhrchen",
        "Assembly Tubes",
        "Montageröhrchen sind kleine zylindrische Elemente in historischen Kronen, die zur Montage und Befestigung kleinerer Dekorationselemente oder als strukturelle Verbindungspunkte verwendet werden.",
        "Assembly tubes are small cylindrical elements in historical crowns used for assembling and securing smaller decorative elements or as structural connection points."
    ),
    "Pins": (
        "Splinte",
        "Pins",
        "Splinte sind schmale, stabförmige Befestigungselemente in historischen Kronen, charakterisiert durch ihren Durchmesser und Querschnitt, verwendet für Verbindungen und Fixierungen.",
        "Pins are slender, rod-like fasteners in historical crowns, characterized by their diameter and cross-section, used for connections and fixations."
    ),
    "Pinhead": (
        "Splintkopf",
        "Pinhead",
        "Der Splintkopf, oft in der Form einer Kugelpyramide, ist das Kopfteil eines Splints in historischen Kronen, welches zur Befestigung und dekorativen Akzentuierung dient.",
        "The pinhead, often in the form of a ball pyramid, is the head part of a pin in historical crowns, serving for fastening and decorative accentuation."
    ),
    "ArcadeFiligree": (
        "Arkadenfiligran",
        "Arcade Filigree",
        "Arkadenfiligran in historischen Kronen bezieht sich auf filigrane Metallarbeiten, die oft Arkaden und Säulen nachbilden, ein Element des Details und der Feinheit.",
        "Arcade filigree in historical crowns refers to delicate metalwork often emulating arcades and columns, an element of detail and finesse."
    ),
    "InsertionPins": (
        "Einsteckstifte",
        "Insertion Pins",
        "Einsteckstifte sind in historischen Kronen verwendete kleine Befestigungselemente, die für die präzise Positionierung und Fixierung von Schmuckstücken und Komponenten dienen.",
        "Insertion pins are small fastening elements used in historical crowns for the precise positioning and securing of jewelry pieces and components."
    ),
    "SettingFlange": (
        "Fassungszarge",
        "Setting Flange",
        "Die Fassungszarge ist ein Metallrahmen in historischen Kronen, der zur festen Umrandung und Hervorhebung von Edelsteinen und anderen Dekorationsstücken dient.",
        "The setting flange is a metal frame in historical crowns used to firmly encircle and highlight gemstones and other decorative pieces."
    ),
    "Nozzles": (
        "Tüllen",
        "Nozzles",
        "Tüllen in historischen Kronen sind Düsen- oder röhrenförmige Elemente, die für die präzise Führung von Flüssigkeiten oder als feine dekorative Details eingesetzt werden.",
        "Nozzles in historical crowns are spout- or tube-like elements used for precise guiding of liquids or as fine decorative details."
    ),
    "ShapeForSetting": (
        "Form für Fassung",
        "Shape for Setting",
        "Die Form für Fassung bezeichnet die spezifische Gestaltung und Konstruktion der Edelsteinfassungen in historischen Kronen, die das Design und die Funktionalität der Fassung beeinflusst.",
        "The shape for setting refers to the specific design and construction of gemstone settings in historical crowns, influencing the design and functionality of the setting."
    ),
    "ClampWithCVolutes": (
        "Klammer mit C-Voluten verlötet",
        "Clamp with C Volutes",
        "Eine mit C-Voluten verlötete Klammer ist ein in historischen Kronen verwendetes Element, das dekorative Spiralformen aufweist und zur strukturellen Stärkung oder als Teil des Designs dient.",
        "A clamp soldered with C volutes is an element used in historical crowns featuring decorative spiral shapes, serving for structural strengthening or as part of the design."
    ),
    "BallPyramid": (
        "Kugelpyramide",
        "Ball Pyramid",
        "Die Kugelpyramide in historischen Kronen ist eine kugelförmige, pyramidenartige Struktur, die oft als dekoratives oder symbolisches Element eingesetzt wird.",
        "The ball pyramid in historical crowns is a spherical, pyramid-like structure often used as a decorative or symbolic element."
    ),
    "BeehiveWithSingleGranule": (
        "Bienenkorb mit Einzelgranulat",
        "Beehive with Single Granule",
        "Ein Bienenkorb mit Einzelgranulat ist eine spezielle Form einer dekorativen Komponente in historischen Kronen, gekennzeichnet durch seine einzigartige Struktur.",
        "A beehive with single granule is a specific form of a decorative component in historical crowns, characterized by its unique structure."
    ),
     "EnamelPlate": (
        "Emailplatte",
        "Enamel Plate",
        "Eine Emailplatte in historischen Kronen ist eine Komponente aus emailliertem Material, oft verwendet für dekorative und schützende Zwecke.",
        "An enamel plate in historical crowns is a component made of enameled material, often used for decorative and protective purposes."
    ),
    "BasePlate": (
        "Grundplatte",
        "Base Plate",
        "Die Grundplatte ist in historischen Kronen ein grundlegendes Element, das als Basis oder Unterstützung für andere Komponenten dient.",
        "The base plate in historical crowns is a fundamental element serving as a base or support for other components."
    ), "Gemstone": (
        "Edelstein",
        "Gemstone",
        "Ein Edelstein in historischen Kronen ist ein nach dem Schleifen und Polieren verwendeter Schmuckstein, oft als zentrales dekoratives Element.",
        "A gemstone in historical crowns is a decorative stone used after being cut and polished, often as a central decorative element."
    ),
     "EnamelPlateColourPalette": (
        "Emailplatten-Farbpalette",
        "Enamel Plate Colour Palette",
        "Die Farbpalette einer Emailplatte in historischen Kronen beschreibt die vielfältigen Farben und deren Zusammensetzung, die zur Schaffung visueller Effekte verwendet werden.",
        "The colour palette of an enamel plate in historical crowns describes the diverse colors and their composition used to create visual effects."
    ),
    "EnamelPlateDefect": (
        "Emailplatten-Defekt",
        "Enamel Plate Defect",
        "Ein Emailplatten-Defekt in historischen Kronen bezieht sich auf Beschädigungen oder Unvollkommenheiten, die die Ästhetik und Integrität der Emailarbeit beeinträchtigen.",
        "An enamel plate defect in historical crowns refers to damage or imperfections that affect the aesthetics and integrity of the enamel work."
    ),
    "EnamelMetalWires": (
        "Email-Metall Drähte",
        "Enamel Metal Wires",
        "Email-Metall Drähte in historischen Kronen sind feine Drähte, die in die Emailarbeit eingebettet sind und strukturelle oder dekorative Funktionen erfüllen.",
        "Enamel metal wires in historical crowns are fine wires embedded in the enamel work, serving structural or decorative functions."
    ),
    "ClawSetting": (
        "Krallenfassung",
        "Claw Setting",
        "Eine Krallenfassung in historischen Kronen ist eine Methode, bei der Metallklauen zum Halten und Hervorheben von Edelsteinen verwendet werden.",
        "A claw setting in historical crowns is a method where metal claws are used to hold and highlight gemstones."
    ),
    "SettingWithThreePearls": (
        "Fassung mit drei Perlen",
        "Setting with Three Pearls",
        "Eine Fassung mit drei Perlen in historischen Kronen ist ein Schmuckelement, das drei Perlen auf besondere Weise präsentiert und betont.",
        "A setting with three pearls in historical crowns is a jewelry element that distinctively presents and accentuates three pearls."
    ),
      "BezelSetting": (
        "Zargenfassung",
        "Bezel Setting",
        "Die Zargenfassung in historischen Kronen ist eine Technik, bei der Edelsteine durch eine Metallumrandung sicher gehalten werden, was sowohl Schutz als auch eine hervorgehobene Präsentation bietet.",
        "The bezel setting in historical crowns is a technique where gemstones are securely held by a metal rim, offering both protection and an enhanced presentation."
    ),
    "ProngSetting": (
        "Krappenfassung",
        "Prong Setting",
        "Eine Krappenfassung in historischen Kronen verwendet kleine Metallprongs, um Edelsteine fest zu halten, wodurch eine minimale Metallabdeckung und maximale Sichtbarkeit des Steins ermöglicht wird.",
        "A prong setting in historical crowns uses small metal prongs to securely hold gemstones, allowing for minimal metal coverage and maximum visibility of the stone."
    ),
    "SettingOnTheCentralCross": (
        "Fassung am Zentralkreuz",
        "Setting on the Central Cross",
        "Die Fassung am Zentralkreuz in historischen Kronen bezieht sich auf die Anbringung von Edelsteinen oder Dekorationen an einem zentralen Kreuz, oft als symbolisches oder auffälliges Element.",
        "The setting on the central cross in historical crowns refers to the placement of gemstones or decorations on a central cross, often as a symbolic or striking element."
    ),
    "PearlSetting": (
        "Perlenfassung",
        "Pearl Setting",
        "Die Perlenfassung in historischen Kronen beschreibt die Art und Weise, wie Perlen eingebettet oder befestigt werden, oft mit einem Fokus auf Ästhetik und Handwerkskunst.",
        "The pearl setting in historical crowns describes how pearls are embedded or affixed, often with a focus on aesthetics and craftsmanship."
    ),
    "BasePlateEdging": (
        "Grundplattenrand",
        "Base Plate Edging",
        "Der Rand der Grundplatte in historischen Kronen ist ein gestalterisches Element, das den äußeren Rand der Grundplatte verziert und oft Detailreichtum und Raffinesse hinzufügt.",
        "The edging of the base plate in historical crowns is a design element that adorns the outer edge of the base plate, often adding detail and sophistication."
    ),
    "PendiliaTubeAndHingeTube": (
        "Pendilia-Rohr und Scharnierrohr",
        "Pendilia Tube and Hinge Tube",
        "Pendilia- und Scharnierrohre sind Komponenten, die in byzantinischen Kronen verwendet werden, oft zur Anbringung von hängenden Ornamenten oder als bewegliche Verbindungselemente.",
        "Pendilia and hinge tubes are components used in Byzantine crowns, often for attaching hanging ornaments or as movable connecting elements."
    ),
    "PearlWireRingWithSingleGranule": (
        "Perldrahtring mit Einzelgranulat",
        "Pearl Wire Ring with Single Granule",
        "Ein Perldrahting mit Einzelgranulat in historischen Kronen ist charakterisiert durch einen dünnen Draht mit einem einzelnen Granulat, oft als feines dekoratives Detail verwendet.",
        "A pearl wire ring with single granule in historical crowns is characterized by a thin wire with a single granule, often used as a fine decorative detail."
    ),
    "HingePin": (
        "Scharnierstift",
        "Hinge Pin",
        "Ein Scharnierstift in historischen Kronen ist eine mechanische Komponente, die zur drehbaren Verbindung von Teilen verwendet wird, was Flexibilität und Bewegung ermöglicht.",
        "A hinge pin in historical crowns is a mechanical component used to pivotally connect parts, allowing for flexibility and movement."
    ),
    "Nozzle": (
        "Düse",
        "Nozzle",
        "Düsen in historischen Kronen sind Vorrichtungen zur Steuerung der Richtung oder Eigenschaften eines Flüssigkeitsstroms, oft im Rahmen von dekorativen Wasserspielen.",
        "Nozzles in historical crowns are devices to control the direction or characteristics of a fluid flow, often in the context of decorative water features."
    ),
    "BundlesOfVolute": (
        "Bündel von Voluten",
        "Bundles of Volute",
        "Bündel von Voluten sind in historischen Kronen dekorative Elemente mit spiralförmigen Mustern oder Designs, die für ihre kunstvolle Gestaltung und symbolische Bedeutung bekannt sind.",
        "Bundles of volute in historical crowns are decorative elements with spiral patterns or designs, known for their artistic design and symbolic significance."
    )
}
    for class_name, labels_comments in component_classes.items():
        class_uri = CROWN[class_name]
        g.add((class_uri, RDF.type, RDFS.Class))
        g.add((class_uri, RDFS.subClassOf, CROWN.Component))
        g.add((class_uri, RDFS.label, Literal(labels_comments[0], lang="de")))
        g.add((class_uri, RDFS.label, Literal(labels_comments[1], lang="en")))
        g.add((class_uri, RDFS.comment, Literal(labels_comments[2], lang="de")))
        g.add((class_uri, RDFS.comment, Literal(labels_comments[3], lang="en")))

    condition_classes = {
    "SurfaceDegradation": (
        "Degradation der Oberfläche",
        "Surface Degradation",
        "Bezieht sich auf die visuelle Verschlechterung der Oberfläche, einschließlich Verfärbungen, Abblättern oder anderen Formen des Verfalls.",
        "Refers to the visual degradation of the surface, which can include discoloration, peeling, or other forms of deterioration."
    ),
    "Blistering": (
        "Blasen",
        "Blistering",
        "Das Vorhandensein von Blasen oder Bläschen, was auf zugrundeliegende Probleme oder Schäden hinweisen kann.",
        "The presence of blisters or bubbles, which can indicate underlying issues or damage."
    ),
    "Wear": (
        "Abnutzung",
        "Wear",
        "Allgemeine Abnutzung, die im Laufe der Zeit auftritt, was auf das Alter und die Nutzung des Objekts hinweist.",
        "General wear and tear that occurs over time, indicating the object's age and usage."
    ),
    "AttachmentLoss": (
        "Haftungsverlust",
        "Attachment Loss",
        "Zeigt einen Verlust der Anhaftung oder Adhäsion von Teilen des Objekts an.",
        "Indicates a loss of attachment or adhesion in parts of the object."
    ),
    "Scratches": (
        "Kratzer",
        "Scratches",
        "Markierungen oder Linien, die auf physische Abrieb oder Verschleiß hinweisen.",
        "Marks or lines indicating physical abrasion or wear."
    ),
    "CrystalBloom": (
        "kristalline Ausblühungen",
        "Crystal Bloom",
        "Bezieht sich auf kristalline Formationen, die oft aufgrund chemischer Reaktionen oder Umweltbedingungen auf der Oberfläche erscheinen.",
        "Refers to crystalline formations that may appear on the surface, often due to chemical reactions or environmental conditions."
    ),
    "OtherConditions": (
        "Zustand: Sonstiges",
        "Other Conditions",
        "Eine allgemeine Kategorie für andere Zustände, die nicht spezifisch anderweitig kategorisiert sind.",
        "A general category for other conditions not specifically categorized elsewhere."
    ),
    "SolderedConnections": (
        "verlötet mit...",
        "Soldered Connections",
        "Zeigt an, dass Komponenten mit Löten verbunden oder repariert wurden, eine gängige Methode zur Restaurierung oder Montage in der Metallverarbeitung.",
        "Indicates components that have been joined or repaired using soldering, a common restoration or assembly method in metalworking."
    ),
    "GoldAddition": (
        "Ergänzung: Gold",
        "Gold Addition",
        "Bezieht sich darauf, dass Gold zu einer Komponente hinzugefügt wurde, möglicherweise zur Reparatur oder Verbesserung.",
        "Refers to gold being added to a component, possibly for repair or enhancement."
    ),
    "EnamelDamage": (
        "Email: Beschädigt",
        "Enamel Damage",
        "Zeigt Schäden an der Email-Arbeit an, wie Risse, Chips oder Verblassen.",
        "Indicates damage to the enamel work, such as cracks, chips, or fading."
    ),
    "RupturedSolderConnection": (
        "Ursache: aufgerissene Lötverbindung",
        "Ruptured Solder Connection",
        "Spezifiziert einen Zustand, bei dem die Lötverbindung versagt hat oder beschädigt ist.",
        "Specifies a condition where the solder connection has failed or is damaged."
    ),
    "Breakage": (
        "Ursache: Bruch",
        "Breakage",
        "Zeigt an, dass eine Komponente gebrochen ist, was für das Verständnis der Geschichte und der Konservierungsbedürfnisse des Objekts entscheidend ist.",
        "Indicates that a component has broken, which is crucial for understanding the object's history and conservation needs."
    ),
    "Deformation": (
        "Ursache: Deformierung",
        "Deformation",
        "Bezieht sich auf jegliche Biegung, Verformung oder Umgestaltung der ursprünglichen Form einer Komponente.",
        "Refers to any bending, warping, or reshaping of the original form of a component."
    ),
    "MissingParts": (
        "Ursache: fehlende Teile",
        "Missing Parts",
        "Hebt Komponenten oder Teile hervor, die vom Objekt fehlen.",
        "Highlights components or parts that are missing from the object."
    ),
    "Cracks": (
        "Ursache: Riss",
        "Cracks",
        "Spezifiziert Risse im Objekt, was für die Beurteilung seines Zustands und seiner strukturellen Integrität entscheidend sein kann.",
        "Specifies cracks in the object, which can be critical for assessing its condition and structural integrity."
    ),
    "DamageFromIntervention": (
        "durch Eingriff verursachte Schäden",
        "Damage from Intervention",
        "Zeigt Schäden an, die durch frühere Restaurierung, Reparatur oder andere Eingriffe verursacht wurden.",
        "Indicates damage caused by previous restoration, repair, or other interventions."
    )
}
    for class_name, labels_comments in condition_classes.items():
        class_uri = CROWN[class_name]
        g.add((class_uri, RDF.type, RDFS.Class))
        g.add((class_uri, RDFS.subClassOf, CROWN.Condition))
        g.add((class_uri, RDFS.label, Literal(labels_comments[0], lang="de")))
        g.add((class_uri, RDFS.label, Literal(labels_comments[1], lang="en")))
        g.add((class_uri, RDFS.comment, Literal(labels_comments[2], lang="de")))
        g.add((class_uri, RDFS.comment, Literal(labels_comments[3], lang="en")))


    # First iteration: Handle properties and SKOS concepts
    for _, row in df.iterrows():
        property_path = row.get('Property Path', '').split('/')
        datatype = get_datatype(row.get('Datatype', 'text'))

        if property_path:
            property_name = normalize_name(property_path[-1])
            label_de = row.get('UserfieldName: german', '')
            label_en = row.get('UserfieldName: english', '')
            comment_de = row.get('definition: german', '')
            comment_en = row.get('definition: english', '')

            # Check if it's a crown:has property with SKOS Concept as range
            if datatype == XSD.anyURI:
                # Create crown:has property if not already created
                if not (CROWN['has'], RDF.type, RDF.Property) in g:
                    create_data_property(g, CROWN, 'has', SKOS.Concept)
                # Extract SKOS concept name from the path and create SKOS concept
                skos_concept_name = normalize_name(property_path[-1])  # Use the last element as the concept name
                create_skos_concept(g, skos_concept_name, label_de, label_en, comment_de, comment_en)
            elif row.get('Datatype', '') == "class":
                # Add class names to the set
                for part in property_path:
                    if part and part[0].isupper():  # Check if part is not empty and starts with an uppercase letter
                        class_names.add(part)
            else:
                create_data_property(g, CROWN, property_name, datatype, label_de, label_en, comment_de, comment_en)



    # Define your data properties here
    data_properties = {
        "media": {
            "domain": "Analysis",
            "label_de": "Medien",
            "label_en": "Media",
            "comment_de": "Die Dateien der Untersuchungsergebnisse.",
            "comment_en": "The files of the analysis results."
        },
        "dateOfAnalysis": {
            "domain": "Analysis",
            "label_de": "Inspektionsdatum",
            "label_en": "Date of Analysis",
            "comment_de": "Das Datum an dem die Untersuchung durchgeführt wurde.",
            "comment_en": "The date on which the analysis was conducted."
        },
        "method": {
            "domain": "Analysis",
            "label_de": "Maßnahme/Bildmaterial",
            "label_en": "Method",
            "comment_de": "Die verwendete Untersuchungsmethode.",
            "comment_en": "The method used for the analysis."
        },
        "instrumentals": {
            "domain": "Object",
            "label_de": "Behandlung/Maßnahme",
            "label_en": "Instrumentals",
            "comment_de": "Zusätzliche Informationen über die Untersuchungen, die verwendeten Geräte und Einstellungen.",
            "comment_en": "Additional information about the analyses, the instruments used, and their settings."
        }
    }

    # Create data properties in the graph
    for prop, details in data_properties.items():
        create_data_property_static(g, CROWN, prop, details['domain'], details['label_de'], details['label_en'], details['comment_de'], details['comment_en'])


    # Serialize the graph to Turtle format and write to a file
    ttl_data = g.serialize(format="turtle")
    with open("crown-ontology.ttl", "w") as file:
        file.write(g.serialize(format="turtle"))

    print("RDF data written to crown-ontology.ttl")