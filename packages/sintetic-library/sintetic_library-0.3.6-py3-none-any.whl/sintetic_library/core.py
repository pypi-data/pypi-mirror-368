# Sintetic Management Client
# This module provides a client for interacting with the Sintetic GeoDB API
# with handling authentication and requests.

import requests
import json
from datetime import datetime
import pytz
from typing import Optional, Dict, Any
import uuid
from enum import Enum

# Sintetic API Endpoints
# These endpoints are used to interact with the Sintetic GeoDB API.
SINTETIC_ENDPOINTS = {
    "AUTH_LOGIN": "/auth/login",
    "STAN_FOR_D": "/stanford_attachments",
    "TREE_PROCESSORS": "/tree_processors",
    "FOREST_OPERATIONS": "/forest_operations",
    "FOREST_PROPERTIES": "/forest_properties",
    "CLIMATE_ATTACHMENTS": "/climate_data_attachments",
    "VEGETATION_ATTACHMENTS": "/vegetation_data_attachments",
    "SUBCOMPARTMENTS": "/subcompartments"
   
}

class TemporalResolution(Enum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    DAILY = "daily"

class SubcompartmentType(Enum):
    FOREST_OPERATION = "forest_operation"
    FOREST_PROPERTY = "forest_property"

class SinteticClient:
    # SinteticClient Class constructor
    def __init__(self, email: str, password: str, base_url: str = "https://api.geodb-staging.sintetic.iit.cnr.it"):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
    # Check if the token is valid    
    def _check_token_validity(self) -> bool:
        
        if not self.token or not self.token_expiry:
            return False
        
        now = datetime.now(pytz.UTC)
        return now < self.token_expiry

    # Login method to authenticate and obtain a new token
    def _login(self) -> None:
       
        login_url = f"{self.base_url}{SINTETIC_ENDPOINTS['AUTH_LOGIN']}"
        login_data = {
            "login": {
                "email": self.email,
                "password": self.password
            }
        }
        
        try:
            # Perform login request
            response = requests.post(login_url, json=login_data)
            response.raise_for_status()
            
            data = response.json()
            self.token = data["login"]["token"]
            self.token_expiry = datetime.strptime(
                data["login"]["expiry"], 
                "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=pytz.UTC)
            
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    # Get headers with authentication token
    def _get_headers(self) -> Dict[str, str]:
       
        if not self._check_token_validity():
            self._login()
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # Make a generic request to the Sintetic API
    def make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Perform a generic https request to the Sintetic API
        
        Args:
            method: Metodo HTTP (get, post, put, delete, etc.)
            endpoint: Endpoint of API
            **kwargs: Optional parameters for the request, such as data or params
        
        Returns:
            JSON response from the API
        """
        
        url = f"{self.base_url}{endpoint}"
        
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    # Get Stand4D Attachments list
    # Returns:
    #     List of attachments with created_at, name and url
    def get_stan4d_list(self, **kwargs) -> Any:
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            response_data = response.json()
            #extract a subset of data composed by created_at, name and url
            filtered_data = [
                {
                    "id": item.get("id", ""),
                    "created_at": item.get("created_at", ""),
                    "name": item.get("name", ""),
                    "url": item.get("url", "")
                }
                for item in response_data
            ]
            return filtered_data
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Get Stand4D Attachment object from given ID
    # Returns:
    #     XML object of the attachment with given ID
    def get_stan4d_file(self, fileid: str, **kwargs) -> Any:
        """
            Get Stand4D Attachment XML file from given ID
    
            Args:
                fileid: ID of the attachment to retrieve
                **kwargs: Optional parameters for the request
        
            Returns:
                str: XML content of the attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}/files/{fileid}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    # Get Stand4D Attachment object from given ID
    # Returns:
    #     XML object of the attachment with given ID
    def save_stan4d_object(self, filename: str, xml_content: bytes, tree_processor_id: str,
            forest_operation_id: str, **kwargs) -> Any:
        """
            Get Stand4D Attachment XML file from given ID
    
            Args:
                fileid: ID of the attachment to retrieve
                **kwargs: Optional parameters for the request
        
            Returns:
                str: XML content of the attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}"
        
        data = {
            "attachment:tree_processor_id": tree_processor_id,
            "attachment:forest_operation_id": forest_operation_id,
            "attachment:id": str(uuid.uuid4())
                }
        files = {
            "attachment:file": (filename, xml_content, "application/xml")
        }

        
        headers = self._get_headers()
        headers.pop("Content-Type", None)  # requests set Content-Type for MultiPart
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        # --- STAMPA DETTAGLI DELLA CHIAMATA ---
        if kwargs:
            print("Altri kwargs:", kwargs)
        try:
            response = requests.post(
                url,
                data=data,
                files=files,
                **kwargs
            )
            response.raise_for_status()      
            return response
 
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Get list forest operations
    # Returns:
    #       json array of forest operations with created_at, name and url
    def get_forest_operations_list(self, **kwargs) -> Any:
        """
            Get list of forest operations
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of forest operations with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['FOREST_OPERATIONS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
    
    # Get list forest properties
    def get_forest_properties_list(self, **kwargs) -> Any:
        """
            Get list of forest properties
            Args:
                **kwargs: Optional parameters for the request
            Returns:
                List of forest properties with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['FOREST_PROPERTIES']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
    
    
    # Get list tree processors
    # Returns:
    #     json array of tree processors with created_at, name and url
    def get_tree_processors_list(self, **kwargs) -> Any:
        """
            Get list of tree processors
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of tree processors with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['TREE_PROCESSORS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.text
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Create a new tree processor
    def create_tree_processor(self, data: dict, **kwargs) -> Any:
        """
        Create a new tree processor
        Args:
            data: Dictionary containing the tree processor data
            **kwargs: Optional parameters for the request
        Returns:
            JSON response from the API
        """
        
        # Generate a unique ID for the tree processor
        data["id"] = str(uuid.uuid4())
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['TREE_PROCESSORS']}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=data  # requests gestirà automaticamente la serializzazione in JSON
            )
            
            response.raise_for_status()
            return data["id"]
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
    
    
    # Create a new forest operation
    def create_forest_operation(self, data: dict, **kwargs) -> Any:
        """
        Create a new forest operation
        Args:
            data: Dictionary containing the forest operation data
            **kwargs: Optional parameters for the request
        Returns:
            JSON response from the API
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['FOREST_OPERATIONS']}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        data["id"] = str(uuid.uuid4())
        
        print("Data to create forest operation:", data)
        try:
            response = requests.post(
                url=url,
                headers=headers,
                json=data  # requests gestirà automaticamente la serializzazione in JSON
            )
            
            response.raise_for_status()
            return data["id"]
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")  
        
        
    # Delete stan4d4d file
    def delete_stan4d_file(self, fileid: str, **kwargs) -> Any:
       
        """        Delete a Stand4D file by its ID
        Args:
            fileid: ID of the Stand4D file to delete
            **kwargs: Optional parameters for the request
        Returns:
            int: HTTP status code of the response
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['STAN_FOR_D']}/{fileid}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.delete(
                url=url,
                headers=headers,
                
            )
            
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    
    # Delete a forest operation
    # Args:
    #       forest_operation_id: ID of the forest operation to delete
    # Returns:
    #       int: HTTP status code of the response
    def delete_forest_operation(self, forest_operation_id: str, **kwargs) -> Any:
        
        url = f"{SINTETIC_ENDPOINTS['FOREST_OPERATIONS']}/{forest_operation_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            
            response = self.make_request("DELETE", url, **kwargs)
            
            return response.status_code
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
    
    # Delete a tree processor
    # Args:
    #       forest_operation_id: ID of the forest operation to delete
    # Returns:
    #       int: HTTP status code of the response
    def delete_tree_processor(self, tree_processor_id: str, **kwargs) -> Any:
        """
            Get list of forest operations
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of forest operations with created_at, name and url
        """
        url = f"{SINTETIC_ENDPOINTS['TREE_PROCESSORS']}/{tree_processor_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            response = self.make_request("DELETE", url, **kwargs)
            
            return response.status_code
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
    
    
    # Get Climate Attachments list
    # Returns:
    #     List of climate attachments with created_at, name and url
    def get_climate_list(self, **kwargs) -> Any:
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['CLIMATE_ATTACHMENTS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            response_data = response.json()
            #extract a subset of data composed by created_at, name and url
            filtered_data = [
                {
                    "id": item.get("id", ""),
                    "created_at": item.get("created_at", ""),
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "description": item.get("description", ""),
                    "type": item.get("type", ""),
                    "forest_operation_id": item.get("related_overview", "").get("id","")
                }
                for item in response_data
            ]
            return filtered_data
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    # Get Climate Attachment object from given ID
    # Returns:
    #     ID of the created attachment
    def save_climate_object(self, filename: str, climate_file: bytes, anomalistic: bool,
            forest_operation_id: str, temporal_resolution: TemporalResolution, coverage_start_year: int, coverage_end_year: int,
            description: str = "", **kwargs) -> Any:
        """
            Get Climate Attachment CSV/JPEG file from given ID
    
            Args:
                filename: Name of the file to save
                climate_file: Content of the climate file (CSV/JPEG/XML)
                anomalistic: Boolean indicating if the attachment is anomalistic
                forest_operation_id: ID of the related forest operation
                temporal_resolution: Temporal resolution of the attachment (yearly, monthly, daily) 
                coverage_start_year: Start year of the coverage
                coverage_end_year: End year of the coverage 
                description: Description of the attachment (optional)
                **kwargs: Optional parameters for the request
        
            Returns:
                str: id of the created attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['CLIMATE_ATTACHMENTS']}"
        
        if filename.lower().endswith(".xml"):
            mime_type = "application/xml"
        elif filename.lower().endswith(".jpeg") or filename.lower().endswith(".jpg"):
            mime_type = "image/jpeg"
        elif filename.lower().endswith(".csv"):
            mime_type = "text/csv"
        else:
            mime_type = "application/octet-stream"  # fallback generico

        
        data = {
            "attachment:anomalistic": "true" if anomalistic else "false",
            "attachment:forest_operation_id": forest_operation_id,
            "attachment:temporal_resolution": temporal_resolution,
            "attachment:coverage_start_year": coverage_start_year,
            "attachment:coverage_end_year": coverage_end_year,
            "attachment:description": description,
            "attachment:id": str(uuid.uuid4())
                }
        files = {
            "attachment:file": (filename, climate_file, mime_type)
        }

        
        headers = self._get_headers()
        headers.pop("Content-Type", None)  # requests set Content-Type for MultiPart
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
     
        
        try:
            #print("=== SinteticClient Request ===")
            #print("URL:", url)
            #print("Data:", data)
            #print("Headers:", headers)
            #print("Files:", files)
            #print("Kwargs:", kwargs)
            #print("=============================")
            response = requests.post(
                url,
                data=data,
                files=files,
                **kwargs
            )
            response.raise_for_status()      
            return data["attachment:id"]
 
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        

    # Get Climate Attachments list
    # Returns:
    #     List of climate attachments with created_at, name and url
    def get_climate_data(self,climate_id: str, **kwargs) -> Any:
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['CLIMATE_ATTACHMENTS']}/{climate_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            response_data = response.json()
            # If response_data is a list, filter the data
            # to extract a subset of fields
            if isinstance(response_data, list):
                filtered_data = [
                    {
                        "id": item.get("id", ""),
                        "created_at": item.get("created_at", ""),
                        "name": item.get("name", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", ""),
                        "type": item.get("type", ""),
                        "forest_operation_id": item.get("related_overview", "").get("id","")
                    }
                    for item in response_data
                ]
            # If it's a single object, filter the data
            elif isinstance(response_data, dict):
                filtered_data = [{
                    "id": response_data.get("id", ""),
                    "created_at": response_data.get("created_at", ""),
                    "name": response_data.get("name", ""),
                    "url": response_data.get("url", ""),
                    "description": response_data.get("description", ""),
                    "type": response_data.get("type", ""),
                    "forest_operation_id": response_data.get("related_overview", "").get("id","")
                }]
            else:
                filtered_data = []
            return filtered_data
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Get Climate Attachment object from given ID
    # Returns:
    #     CSV or Jpeg object of the attachment with given ID
    def get_climate_file(self, fileid: str, **kwargs) -> Any:
        """
            Get Climate Attachment file from given ID
    
            Args:
                fileid: ID of the attachment to retrieve
                **kwargs: Optional parameters for the request
        
            Returns:
                CSV or Jpeg content of the attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['CLIMATE_ATTACHMENTS']}/files/{fileid}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            content_type = response.headers.get("Content-Type", "")
            if "text/csv" in content_type:
                # Return the content as a string
                return response.text
            elif "image/jpeg" in content_type or "image/jpg" in content_type:
                # Return the content as bytes
                return response.content
            else:
                # Unknown content type, return as bytes
                return response.content
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Delete climate file
    def delete_climate_file(self, fileid: str, **kwargs) -> Any:
       
        """        Delete a Climate Attachment file by its ID
        Args:
            fileid: ID of the Stand4D file to delete
            **kwargs: Optional parameters for the request
        Returns:
            int: HTTP status code of the response
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['CLIMATE_ATTACHMENTS']}/{fileid}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.delete(
                url=url,
                headers=headers,
                
            )
            
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        

    # Get Vegetation Attachments list
    # Returns:
    #     List of vegetation attachments with created_at, name and url
    def get_vegetation_list(self, **kwargs) -> Any:
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['VEGETATION_ATTACHMENTS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            response_data = response.json()
            #extract a subset of data composed by created_at, name and url
            filtered_data = [
                {
                    "start_date": item.get("start_date", ""),
                    "end_date": item.get("end_date", ""),
                    "created_at": item.get("created_at", ""),
                    "update_at": item.get("update_at", ""),
                    "forest_operation_id": item.get("related_overview", "").get("forest_operation","").get("id", ""),
                    "subcompartment": item.get("related_overview", "").get("subcompartment","").get("id", ""),
                }
                
                for item in response_data
            ]
            return filtered_data
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    # save a vegetation object
    # Returns:
    #     Status code of the response:
    #     201 if the object was created successfully
    #.    204 no content. attachment file appended to existing object
    def save_vegetation_object(self, filename: str, vegetation_file: bytes, subcompartment_id: str, **kwargs) -> Any:
        """
            Get Climate Attachment CSV/JPEG file from given ID
    
            Args:
                filename: Name of the file to save
                vegetation_file: Content of the climate file (CSV)
                subcompartment_id: ID of the related subcompartment
                **kwargs: Optional parameters for the request
        
            Returns:
                str: id of the created attachment
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['VEGETATION_ATTACHMENTS']}"
        
        if filename.lower().endswith(".xml"):
            mime_type = "application/xml"
        elif filename.lower().endswith(".jpeg") or filename.lower().endswith(".jpg"):
            mime_type = "image/jpeg"
        elif filename.lower().endswith(".csv"):
            mime_type = "text/csv"
        else:
            mime_type = "application/octet-stream"  # fallback generico

        
        data = {
            
            "attachment:subcompartment_id": subcompartment_id,
               }
        files = {
            "attachment:file": (filename, vegetation_file, mime_type)
        }

        
        headers = self._get_headers()
        headers.pop("Content-Type", None)  # requests set Content-Type for MultiPart
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
     
        
        try:
            #print("=== SinteticClient Request ===")
            #print("URL:", url)
            #print("Data:", data)
            #print("Headers:", headers)
            #print("Files:", files)
            #print("Kwargs:", kwargs)
            #print("=============================")
            response = requests.post(
                url,
                data=data,
                files=files,
                **kwargs
            )
            response.raise_for_status()      
            return response.status_code
 
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        

    # Get Vegetation Attachment data from given ID
    # Returns:
    #     json object with vegetation attachment data
    def get_vegetation_data(self, subcompartment_id: str, **kwargs) -> Any:
       
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['VEGETATION_ATTACHMENTS']}/{subcompartment_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            content_type = response.headers.get("Content-Type", "")
            if "text/csv" in content_type:
                # Return the content as a string
                return response.text
            elif "image/jpeg" in content_type or "image/jpg" in content_type:
                # Return the content as bytes
                return response.content
            else:
                # Unknown content type, return as bytes
                return response.content
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}") 

    # Delete climate file
    def delete_vegetation_file(self, subcompartment_id: str, **kwargs) -> Any:
       
        """        Delete a Vegetation Attachment file by its ID
        Args:
            subcompartment_id: ID of the file to delete
            **kwargs: Optional parameters for the request
        Returns:
            int: HTTP status code of the response
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['VEGETATION_ATTACHMENTS']}/{subcompartment_id}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.delete(
                url=url,
                headers=headers,
                
            )
            
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        

    # Get list subcompartments
    # Returns:
    #       json array of subcompartment with created_at, name and url
    def get_subcompartments_list(self, **kwargs) -> Any:
        """
            Get list of subcompartments
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of subcompartments with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['SUBCOMPARTMENTS']}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")

    # Get list subcompartments
    # Returns:
    #       json array of subcompartment with created_at, name and url
    def get_subcompartment(self, subcompartment_id: str, **kwargs) -> Any:
        """
            Get list of subcompartments
            
            Args:
                **kwargs: Optional parameters for the request
        
            Returns:
                List of subcompartments with created_at, name and url
        """
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['SUBCOMPARTMENTS']}/{subcompartment_id}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    
    # Create a new subcompartment
    def create_subcompartment(self, name: str, subcompartmentable_type: SubcompartmentType, 
                              subcompartmentable_id: str, minx: float, miny: float, maxx: float, maxy: float,**kwargs) -> Any:
        """
        Create a new subcompartment
        Args:
            name: Name of the subcompartment
            subcompartment_type: Type of the subcompartment (forest_operation, forest_property)
            minx: Minimum x coordinate of the subcompartment boundary
            miny: Minimum y coordinate of the subcompartment boundary
            maxx: Maximum x coordinate of the subcompartment boundary
            maxy: Maximum y coordinate of the subcompartment boundary
            **kwargs: Optional parameters for the request
        Returns:
            JSON response from the API
        """
        
        # Generate a unique ID for the tree processor
        newsubid = str(uuid.uuid4())
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['SUBCOMPARTMENTS']}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            data = {
            
            "id": newsubid,
            "subcompartmentable_id": subcompartmentable_id,
            "subcompartmentable_type": subcompartmentable_type,
            "name": name,
            "boundaries": {     
                "type": "MultiPolygon",
                "coordinates": [[[[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]]]
                }   
            }
            response = requests.post(
                url=url,
                headers=headers,
                json=data  # requests gestirà automaticamente la serializzazione in JSON
            )
            
            response.raise_for_status()
            return newsubid
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
    # Delete subcompartment
    def delete_subcompartment(self, subcompartment_id: str, **kwargs) -> Any:
       
        """        Delete a subcompartment by its ID
        Args:
            subcompartment_id: ID to delete
            **kwargs: Optional parameters for the request
        Returns:
            int: HTTP status code of the response
        """
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['SUBCOMPARTMENTS']}/{subcompartment_id}"
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.delete(
                url=url,
                headers=headers,
                
            )
            
            response.raise_for_status()
            return response.status_code
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")
        
        
    # Get Vegetation Attachment file from given ID
    # Returns:
    #     CSV or Jpeg object of the attachment with given ID
    def get_vegetation_file(self, fileid: str, **kwargs) -> Any:
        
        url = f"{self.base_url}{SINTETIC_ENDPOINTS['VEGETATION_ATTACHMENTS']}/files/{fileid}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        
        try:
            method="GET"
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
        
            
            content_type = response.headers.get("Content-Type", "")
            if "text/csv" in content_type:
                # Return the content as a string
                return response.text
            elif "image/jpeg" in content_type or "image/jpg" in content_type:
                # Return the content as bytes
                return response.content
            else:
                # Unknown content type, return as bytes
                return response.content
        except requests.exceptions.RequestException as e:
            print("Exeption:", str(e))
            if hasattr(e, "response") and e.response is not None:
                print("Error Body: ", e.response.text)
            raise Exception(f"Exception on: {str(e)}")

    