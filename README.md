# Sharing the CROWN – Establishing a Workflow from Collection Data to Linked Research Data

[CLARIAH-AT - Funding Call 2022: Interoperability and Reusability of DH Data and Tools](https://clariah.at/project-funding)

* Project Investigator (KHM): Dr Martina Griesser, KHM-Museumsverband, Vienna
* Project Investigator (ZIM): Christopher Pollin, ZIM, University of Graz

* **Objectives of the Document**
  * To provide a guide to establishing a workflow that transforms collection data from The Museum System (TMS) into structured, linked research data in accordance with FAIR principles.
  * To outline the steps involved in the data transformation process, including data export, processing and conversion to RDF format.
  * Introduce the tools and scripts used in the workflow and explain their role in data extraction, ontology mapping and RDF creation.
  * To detail the development and structure of the application ontology, focusing on how it facilitates the integration of museum data with domain ontologies.
* **Prerequisites**
  * Basic understanding of museum data management
  * Knowledge of RDF, RDFs and basic data modelling
  * Python basics

## Introduction

### About the CROWN Project

The CROWN project is an interdisciplinary research project focusing on the Imperial Crown of the Holy Roman Empire. It combines fields such as art history, history, conservation science and technological analysis. The aim is to understand the material composition of the crown, its historical significance and its state of conservation.

At the heart of the project is a detailed examination of the physical characteristics of the crown, including all its different parts and components, such as its gemstone settings, wires and plates. We will call these components `crown:Object`. Advanced methods such as Raman spectroscopy, µ-XRF analysis, 3D digital microscopy and others are key to these studies. They provide insights into the physical composition of the different materials in each component, and thus into the working techniques and the condition of the crown.

The project also examines the history of the crown. This includes studying the inscriptions, analysing stylistic features within their historical periods, and considering how the crown has been depicted in historical records. The study also looks at the design and decoration of the crown from a symbolic point of view, in order to understand its significance as an emblem of divine authority. For this reason, additional sources on the crown and its history are also included in the project. All these sources, from charters to images and physical objects, are summarised as `crown:AdditionalMaterial`.

### CLARIAH-AT: “Sharing the CROWN – Establishing a Workflow from Collection Data to Linked Research Data”

The project, supported by CLARIAH-AT, aims to improve the accessibility and reusability of museum research data through improved data creatin workflows. Due to the complexity and historical value of the Crown, the project addresses the difficulties of handling, analysing and disseminating specialised research data resulting from cross-disciplinary studies of the Crown.

Its primary objective is to establish best practice for transforming data from The Museum System (TMS) into data that is Findable, Accessible, Interoperable and Reusable (FAIR). This process goes beyond traditional data management to address the complex needs of museum research, which often lacks standard data capture and standardisation methods. A critical part of this effort is the creation of a structured RDF data and lightweight application ontology, based on the principles of the [CIDOC Conceptual Reference Model (CIDOC-CRM)](https://www.cidoc-crm.org). This ontology acts as a structure for linking data points to controlled vocabularies and Wikidata, adding a semantic layer.

The project consists of several key tasks and packages, such as developing a domain-specific application ontology, converting the TMS data into a Linked Open Data (LOD) and FAIR RDF dataset, semantically enriching the data by aligning it with resources such as Wikidata, and creating a prototype in [GAMS](https://gams.uni-graz.at/) for accessing the data. These steps are designed to address the unique challenges of managing complex research data in the museum environment, from initial data modelling to the final analysis and presentation of linked research data.

### Overview of the Workflow

![CROWN Workflow](img/crown-workflow.png)

The process begins with the collection of data through **The Museum System (TMS)**, which allows data to be exported in Excel format. This format contains various data fields designed to meet the operational needs of the museum and the research-related details of each object (´crown:Object´ or ´crown:AdditionalMaterial´).

Two Python scripts are used to convert the data from Excel to RDF format: excel-to-rdf.py and index-to-rdf.py. The **excel-to-rdf.py script** does most of the conversion, using the *Datafields Spreadsheet* to map Excel fields to the ontology and creates the **RDF data** itself. This stage also includes data normalisation to meet the specific needs of the project. The **index-to-rdf.py script** creates the necessary index files, like those for materials and persons. Both use the [rdflib](https://rdflib.readthedocs.io/en/stable/) Python library.

The most important aspect of the workflow is the mapping of the data fields in TMS, in particular the user fields, which are customisable, project-specific data fields that can be defined in the TMS. These fields need to be mapped to RDF classes and properties defined in the application ontology, and it is important that domain experts are able to customise field names, definitions and translations. This is achieved by **Datafields Spreadsheet**. One recommendation is to use Google spreadsheets for this, but any spreadsheet or CSV will do for this type of work.

Another script, **datafields-to-ontology.py**, extracts mappings from the datafields spreadsheet. This process likely involves insights from domain experts to develop the complete RDF data model. This specific, lightweight **application ontology** is crucial for organizing the RDF data for the CROWN project. Furthermore, it defines how to link to additional ontologies like CIDOC-CRM, helping to ensure the project aligns with broader cultural heritage documentation standards.

The RDF data and the application ontology together describe all the information about the CROWN project, or any other project represented in TMS. This data can be used directly in a triple store, or archived and published in a research data **repository**.

## TMS and Export

### The Museum System (TMS)

The Museum System (TMS), developed by Gallery Systems and built on an open architecture database using Microsoft SQL Server, is a web-based collections management system designed for museums, galleries and cultural institutions. It supports the effective management of collections. TMS Collections provides a wide range of collection management tools, including

- **Objects Management:** Enables the cataloguing and management of detailed records of objects, such as descriptions, provenance, condition and location.
- Exhibitions and Loans:** Helps organise and track objects that are exhibited or loaned to other organisations.
- Digital Asset Management:** Integrates with systems to associate multimedia files with object records, enhancing documentation.
- Conservation Documentation:** Provides modules for recording treatments, condition reports and conservation activities.
- Reporting and Analysis:** Includes reporting capabilities for customised reports and collection insights.
- Standards Compliance:** Complies with international standards such as CDWA, CIDOC CRM, LIDO and Dublin Core for collection data management and exchange.
- Web Publishing:** Can be integrated with eMuseum to publish collections online, widening access to collections.

### TMS Excel Export.

The following table summarises the content and purpose of each Excel file associated with the CROWN project and as a data export from TMS, outlining the structured approach to managing and documenting various aspects of the objects under study.

| File Name                                  | Primary Focus                    | Key Fields                                                                                               | Description                                                                                                                                                       |
|------------------------------------------------|--------------------------------------|--------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CROWN_Objects_1_2024_02_02.xlsx            | Details of various objects       | ObjectID, ObjectNumber, SortNumber, ObjectName, Dated, Medium, Dimensions, Description, Notes, ShortText8, Authority50ID, Bestandteil | Records details on objects, including material, dimensions, and condition. Authority50ID and Bestandteil indicate relationships to other parts.                   |
| CROWN_Objects_3_TextEntries_2024_02_02.xlsx| Text entries related to the objects  | ID, TextType, TextEntry                                                                                  | Stores additional descriptive or historical text information on objects for various purposes including display and documentation.                                  |
| CROWN_Objects_4_AltNumbers_2024_02_02.xlsx | Alternate numbering for objects  | ID, AltNumDescription, AltNum                                                                            | Provides alternate identifiers or links to resources, allowing for cross-references to external databases or digital collections.                                  |
| CROWN_Objects_5_Constituents_2024_02_02.xlsx   | Constituent information on objects   | ObjectID, DisplayOrder, Role, DisplayName, ConstituentID                                                 | Details on individuals or institutions associated with the objects, such as analysis participants.                                                                 |
| CROWN_Objects_6_Medien_2024_02_02.xlsx     | Media related to the objects     | ObjectID, TableID, DisplayOrder, MediaMasterID, RenditionNumber, MediaType, Path, FileName                | Manages digital media for objects, including images and documents. Path and filename indicate storage location within TMS.                                        |
| CROWN_Restaurierung_1_2024_02_02.xlsx      | Information for analysis events  | ID, ObjectNumber, ExaminerID, dbo_Constituents_DisplayName, Examiner2ID, SurveyISODate, SurveyType, Project, ConditionID | Records details on analysis assessments, including examiner details and survey types, for tracking analysis events.                                                |
| CROWN_Restaurierung_2_2024_02_02.xlsx      | Detailed restoration actions     | ConditionID, CondLineItemID, AttributeType, BriefDescription, Statement, Proposal, ActionTaken, DateCompleted, Treatment  | Dives into specific restoration and analysis treatments, documenting actions taken and future conservation proposals.                                              |
| CROWN_Restaurierung_3_Medien_2024_02_02.xlsx   | Media related to restoration and analysis | CondLineItemID, TableID, DisplayOrder, MediaMasterID, RenditionNumber, MediaType, Path, FileName            | Focuses on documenting restoration and analysis through media, including before/after images, reports, or scans.                                                   |
| Crown_Userfields_2024_02_02.xlsx           | Custom user-defined fields for objects| ObjectNumber, ID, UserFieldName, FieldValue, GroupName, UserFieldGroupID, NumericFieldValue, DisplayOrder, UserFieldID | Defines project-specific TMS data fields for the CROWN project. "UserFieldName" is mapped to "Property Path" in the Data Fields spreadsheet.                      |


### 1.2 Datafields Spreadsheet

The Datafields spreadsheet implemented in Google Spreadsheets offers several benefits.  Real-time collaboration between multiple users is streamlined, allowing for simultaneous editing. This enables a more efficient workflow, especially when drawing on the expertise of different individuals or teams. Google Spreadsheets' built-in version control system automatically logs all changes. Another advantage of Google Spreadsheets is that the Google Spreadsheets API allows programmatic interaction with the Datafields spreadsheet. Using a non-commercial production and working with CSV, howser is also possible. 

In the context of museum databases, the ability to define custom data fields is essential. Museums house diverse collections ranging from archaeological artifacts to modern art, each with unique characteristics and historical contexts. Custom data fields allow museums to tailor their data management practices to the specific needs of their collections, enabling precise documentation, analysis, and sharing of information about each object. This workflow, even though it requires modelling and programming expertise, allowsa this complexity to be managed.

#### Spreadsheet Structure and Headers
- **GroupName: german/english**: Organizes fields into logical groups or categories, making the spreadsheet easier to navigate and aligning with the museum's internal taxonomy.
- **Property Path**: Specifies the exact path used in RDF modeling to ensure mapping to RDF classes and properties.
- **Datatype**: Defines the type of data (e.g., integer, text, date).
- **UserfieldName: german/english**: The field name as used in the database, provided in both English and German to support bilingual documentation and international collaboration. The German user field is the string used for matching in the TMS export.
- **Definition: german/english**: A description of the field, its contents, and how it should be interpreted. Used for rdfs:label in the application ontology.

## Section 2: Data Transformation Scripts

### 2.1 The excel-to-rdf.py Script

This section provides an overview of the `excel-to-rdf.py` script, designed to convert data from Excel spreadsheets into RDF (Resource Description Framework) format.

#### Detailed Script Functionality

The script reads data from multiple Excel files related to the CROWN project, processes this data, and outputs RDF/XML files. Key functionalities include:

- **Reading Excel Files**: Utilizes pandas to load data from specified Excel files into dataframes for processing.
- **RDF Graph Construction**: Employs the rdflib library to build an RDF graph for each object described in the Excel data, adding various types of metadata and relationships.
- **Data Reconciliation**: Incorporates reconciliation of specific data fields against external sources like Wikidata to enhance data quality and interoperability.
- **Normalization and Formatting**: Applies several normalization and formatting routines to ensure data consistency and compatibility with RDF standards.

#### Input and Output Format

**Input Format**: The script expects data from The Museum System (TMS) exported into Excel files.

**Output Format**: The script generates RDF/XML files. Each file represents an RDF graph for a single object from the input data, including all relevant metadata, relationships, and linked external resources.

#### Mapping Process and Data Normalization

**Mapping Process**: The script maps fields from Excel files to RDF properties based on predefined mappings. These mappings are critical for converting spreadsheet data into a structured format that aligns with the project's ontology.

**Data Normalization**:
- **String Normalization**: Includes removing unnecessary spaces, converting umlauts, and formatting strings for URIs and JSON.
- **Data Type Conversions**: Converts numeric data and formats dates appropriately for RDF.
- **File Extension Handling**: Translates file extensions into MIME types for media files.

#### Code Walkthrough and Execution

1. **Preparation**:
   - Ensure all dependencies are installed, including pandas, rdflib, and any other required libraries.
   - Verify that Excel files are accessible and in the correct format.

2. **Execution**:
   - Run the script with Python. Adjust paths to Excel files and output directories as needed in the script's global variables section.
   - The script processes each object in turn, building an RDF graph and saving it as an XML file.

### 2.2 The index-to-rdf.py Script

#### Purpose of Indexing in RDF Creation
The rationale behind using indexing when creating RDF files, focusing on materials and persons.

#### Handling Material and Person Indexes
A guide to managing material and person indexes within the RDF creation process.

#### Step-by-Step Guide to Script Usage
Instructions for using the `index-to-rdf.py` script, including setup, execution, and troubleshooting.

### 2.3 The datafields-to-ontology.py Script

#### Role in Ontology Creation
An overview of how the `datafields-to-ontology.py` script contributes to the creation of the Application Ontology.

#### Extracting and Combining Mappings
Details on how the script extracts mappings from the Datafields Spreadsheet and combines them with additional domain knowledge.

#### CIDOC-CRM Integration
Guidance on integrating the CIDOC-CRM model into the Application Ontology.

#### Script Explanation and Implementation
An explanation of the script's functionality and instructions for its implementation.

## Section 3: Developing the Application Ontology

### 3.1 Introduction to the "CROWN" Ontology

#### Overview of the CROWN Ontology Structure
A description of the structure and components of the CROWN Ontology, which outlines the data model for the RDF data.

#### Mapping to CIDOC-CRM
Details on the process and benefits of mapping the CROWN Ontology to the CIDOC-CRM standards.

### 3.2 Building the Ontology

#### Defining Classes and Properties
A guide to defining classes and properties within the ontology to ensure accurate representation of data.

#### Creating RDF Data Models
Step-by-step instructions for creating RDF data models that adhere to the ontology's structure.

#### Best Practices for Ontology Development
A compilation of best practices to follow when developing and refining the ontology to enhance data interoperability and accuracy.
