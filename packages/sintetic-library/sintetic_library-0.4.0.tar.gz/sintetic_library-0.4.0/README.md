# Contents of `README.md`

# Sintetic Library

## Description
Python client for Sintetic Project. This library provides a simple interface to interact with the Sintetic API, allowing users to manage and retrieve data related to synthetic datasets.
For more information, visit https://sinteticproject.eu/

## Intallation

To install the library, you can use pip:

```bash
pip install sintetic-library
```

## Use case


```python
from sintetic_library import SinteticClient

# Create istance of SinteticClient using your Sintetic account
client = SinteticClient(
        email="XXXXXX",
        password="YYYYYYY"
    )

#######
# Sample #1
# Implementation sample for tree processor, forest operation and stan4d files
#######

# Call method for retrieving list of tree processors
result = client.get_list_tree_processors ()

# Retrieve list of forest properties
result = client.get_list_forest_properties () 

# Retrieve list of forest properties
result = client.get_list_forest_properties ()

# Create tree processor id for given data
data = { "name" : "Test Tree Processor",
         "type" : "harvester"    
       }        

id_tree_processor = client.create_tree_processor(data)

# Create new forest operation from given data
# 
data = { "name" : "Test Forest Operation",
                 "status" : "planned",
                 "location": {
                    "type": "Point",
                    "coordinates": [10.2, 45.2]
                    },  
                 "start_date" : "2025-06-19",
                 "end_date" : "2025-06-19", 
                 "area": 100,
                 "forest_property_id": "XXXXXXXX-YYYY-ZZZZ-XXXX-ZZZZZZZZZZZZ"
                }
        
id_forest_operation = client.create_forest_operation(data)       

# Retrieve list of Stan4D files
response = client.get_stan4d_list() 

# Save new Stan4D file
with open("./stan4d_file.hpr", "rb") as f:
    xml_content = f.read()
    
response = client.save_stan4d_object(
    filename=os.path.basename(f.name),
    xml_content=xml_content,
    tree_processor_id=id_tree_processor,
    forest_operation_id=id_forest_operation
)
    
# Extract Stan4D file ID    
stand4d_id = response.json()["id"]

# Get Stan4D file using the associated ID
response = client.get_stan4d_file(fileid=stand4d_id)

# Delete Stan4D file using the associated ID
response = client.delete_stan4d_file(fileid=stand4d_id)

# Delete Forest Operation using the associated ID
response = client.delete_forest_operation(forest_operation_id=id_forest_operation)
        
# Delete Tree Processor using the associated ID
response = client.delete_tree_processor(tree_processor_id=id_tree_processor)
##### End of Sample #1

#####
# Sample #2
# Implementation sample for climate data attachment management
#####

#Open CSV file with climate data
with open("testcsv.csv", "rb") as f:
    csv_content = f.read()

# Create new climate object
response = client.save_climate_object(
    filename="testcsv.csv",
    climate_file=csv_content,
    anomalistic=True,
    forest_operation_id="24a912c4-6a0a-4860-a163-f62e96f43d6b",
    temporal_resolution=TemporalResolution.DAILY.value,
    coverage_start_year=2025,
    coverage_end_year=2025,
    description="Test Climate Attachment"
)


climate_object_id = response   
print("Climate object saved successfully:", climate_object_id)    

# Retrieve Climate Attachment data
print("Retrieved Climate Attachment data:", client.get_climate_data(climate_object_id))   

# Retrieve Climate Attachment file
print("Retrieved Climate file contents:", client.get_climate_file(climate_object_id))

# Delete climate file and data
print("Delete climate file:", client.delete_climate_file(climate_object_id))

#### End of Sample #2

####
# Sample #3
# Implementation sample for subcompartments and vegetation file management
####

#create a new forest operation for subcompartment
data = { "name" : "Test Leandro for Subcompartment",
                "status" : "planned",
                "location": {
                "type": "Point",
                "coordinates": [10.2, 45.2]
                },  
                "start_date" : "2025-06-19",
                "end_date" : "2025-06-19", 
                "area": 100,
                "forest_property_id": "8a0febff-e133-44fd-8e15-bfa11b40f620"
            }
    
forest_id = client.create_forest_operation(data)
print("Risposta creazione forest operation: ", forest_id)

# Create a new subcompartment
response = client.create_subcompartment("Test subcompartment Leandro", SubcompartmentType.FOREST_OPERATION.value, 
                            forest_id, 10.0, 10.0, 20.0, 20.0)

print(f"Subcompartment created successfully with UUID: {response}")
subcomp_id = response
# Retrieve the list of subcompartments
response = client.get_subcompartments_list()
print(f"List of subcompartments: {response}")

# Retrieve the subcompartment by UUID   
response = client.get_subcompartment(subcomp_id)
print(f"Retrieved subcompartment info: {response}")

# Create new vegetation object
# open ndvi file in binary mode
with open("ndvi_july.csv", "rb") as f:
    csv_content = f.read()

response = client.save_vegetation_object(
    filename="ndvi_july.csv",
    vegetation_file=csv_content,
    subcompartment_id=subcomp_id,
)

print(f"Vegetation object saved successfully with ID: {response}")

# Retrieve the vegetation data
response = client.get_vegetation_data(subcomp_id)
print(f"Retrieved vegetation file contents: {response}")
    
# Retrieve vegetation attachments list
response = client.get_vegetation_list()
print(f"Retrieved vegetation attachments list: {response}")

# Retrieve the vegetation object
response = client.get_vegetation_file(subcomp_id)
print(f"Retrieved vegetation file contents: {response}")
    
#Append new vegetation file
#open ndvi file in binary mode
with open("ndvi_august.csv", "rb") as f:
    csv_content = f.read()

response = client.save_vegetation_object(
    filename="ndvi_august.csv",
    vegetation_file=csv_content,
    subcompartment_id=subcomp_id,
)

print(f"Vegetation object saved successfully with ID: {response}")

# Retrieve the updated vegetation object 
response = client.get_vegetation_file(subcomp_id)
print(f"Retrieved updated file contents: {response}")

# Delete vegetation file
response = client.delete_vegetation_file(subcomp_id)
print(f"Vegetation file deleted successfully: {response}")

# Delete subcompartment
response = client.delete_subcompartment(subcomp_id)
print(f"Subcompartment deleted successfully: {response}")

# Delete forest operation
response = client.delete_forest_operation(forest_id)
print(f"Subcompartment deleted successfully: {response}")

```

## License
This library is freely provided for use within the Sintetic project