from typing import Dict, Any, Optional
import json
import gzip        
import os
import weakref
import weakref
from pathlib import Path
from urllib.parse import urlparse
from ..helper.decorators import require_token, require_api_key, require_auth
import aiohttp
from typing import Dict, Any, Optional, List, Union
import asyncio
import xarray as xr
from io import BytesIO
import geopandas as gpd
from shapely.geometry import shape

class MassStats:
    def __init__(self, client):
        self._client = client

    @require_api_key
    async def _upload_request(
        self,
        name: str,
        size: int,
        sample: str,
        output: str,
        config: Dict[str, Any],
        region: str = None,
        overwrite: bool = False,
        skip_existing: bool = False,
        location: Optional[str] = None,
        force_loc: Optional[bool] = None,
        server: Optional[str] = "dev-au.terrak.io",
    ) -> Dict[str, Any]:
        """
        Upload a request to the mass stats server.

        Args:
            name: The name of the job
            size: The size of the job
            sample: The sample expression for deciding which server to make the request to
            output: The output of the job
            config: The config of the job
            overwrite: Whether to overwrite the job
            skip_existing: Whether to skip existing jobs
            location: The location of the job
            force_loc: Whether to force the location
            server: The server to use

        Returns:
            API response as a dictionary

        Raises:
            APIError: If the API request fails
        """
        # we don't actually need the region function inside the request, the endpoint will fix that for us
        payload = {
            "name": name,
            "size": size,
            "sample": sample,
            "output": output,
            "config": config,
            "overwrite": overwrite,
            "skip_existing": skip_existing,
            "server": server,
            "region": region
        }
        payload_mapping = {
            "location": location,
            "force_loc": force_loc
        }
        for key, value in payload_mapping.items():
            if value is not None:
                payload[key] = str(value).lower()
        return await self._client._terrakio_request("POST", "mass_stats/upload", json=payload)

    @require_api_key
    async def start_job(self, id: str) -> Dict[str, Any]:
        """
        Start a mass stats job by task ID.

        Args:
            task_id: The ID of the task to start

        Returns:
            API response as a dictionary

        """
        return await self._client._terrakio_request("POST", f"mass_stats/start/{id}")
    
    @require_api_key
    def get_task_id(self, name: str, stage: str, uid: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the task ID for a mass stats job by name and stage (and optionally user ID).

        Args:
            name: The name of the job
            stage: The stage of the job
            uid: The user ID of the job

        Returns:
            API response as a dictionary

        Raises:
            APIError: If the API request fails
        """
        url = f"mass_stats/job_id?name={name}&stage={stage}"
        if uid is not None:
            url += f"&uid={uid}"
        return self._client._terrakio_request("GET", url)
    
    @require_api_key
    async def track_job(self, ids: Optional[list] = None) -> Dict[str, Any]:
        """
        Track the status of one or more mass stats jobs.

        Args:
            ids: The IDs of the jobs to track

        Returns:
            API response as a dictionary

        Raises:
            APIError: If the API request fails
        """
        data = {"ids": ids} if ids is not None else {}
        return await self._client._terrakio_request("POST", "mass_stats/track", json=data)
    
    @require_api_key
    def get_history(self, limit: Optional[int] = 100) -> Dict[str, Any]:
        """
        Get the history of mass stats jobs.

        Args:
            limit: The number of jobs to return

        Returns:
            API response as a dictionary

        Raises:
            APIError: If the API request fails
        """
        params = {"limit": limit}
        return self._client._terrakio_request("GET", "mass_stats/history", params=params)
    

    @require_api_key     
    async def start_post_processing(
        self,
        process_name: str,
        data_name: str,
        output: str,
        consumer: str,
        overwrite: bool = False
    ) -> Dict[str, Any]:
                
        with open(consumer, 'rb') as f:
            script_bytes = f.read()
        
        data = aiohttp.FormData()
        data.add_field('process_name', process_name)
        data.add_field('data_name', data_name) 
        data.add_field('output', output)
        data.add_field('overwrite', str(overwrite).lower())
        data.add_field('consumer', script_bytes, filename=os.path.basename(consumer), content_type='text/x-python')
        
        return await self._client._terrakio_request(
            "POST", 
            "mass_stats/post_process", 
            data=data,
        )

    @require_api_key     
    async def zonal_stats_transform(
        self,
        data_name: str,
        output: str,
        consumer: bytes,
        overwrite: bool = False
    ) -> Dict[str, Any]:
                
        data = aiohttp.FormData()
        data.add_field('data_name', data_name) 
        data.add_field('output', output)
        data.add_field('overwrite', str(overwrite).lower())
        data.add_field('consumer', consumer, filename="consumer.py", content_type='text/x-python')

        return await self._client._terrakio_request(
            "POST", 
            "mass_stats/transform", 
            data=data,
        )
    
    @require_api_key
    def download_results(
        self,
        file_name: str,
        id: Optional[str] = None,
        force_loc: Optional[bool] = None,
        bucket: Optional[str] = None,
        location: Optional[str] = None,
        output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download results from a mass stats job or arbitrary results if force_loc is True.

        Args:
            file_name: File name of resulting zip file (required)
            id: Post processing id. Can't be used with 'force_loc'
            force_loc: Download arbitrary results not connected to a mass-stats job id. Can't be used with 'id'
            bucket: Bucket name (required if force_loc is True)
            location: Path to folder in bucket (required if force_loc is True)
            output: Output type (required if force_loc is True)

        Returns:
            API response as a dictionary

        Raises:
            APIError: If the API request fails
            ValueError: If validation fails for parameter combinations
        """
        if id is not None and force_loc is True:
            raise ValueError("Cannot use both 'id' and 'force_loc' parameters simultaneously")
        
        if id is None and force_loc is not True:
            raise ValueError("Either 'id' or 'force_loc=True' must be provided")
        
        if force_loc is True:
            if bucket is None or location is None or output is None:
                raise ValueError("When force_loc is True, 'bucket', 'location', and 'output' must be provided")
        
        params = {"file_name": file_name}
        
        if id is not None:
            params["id"] = id
        if force_loc is True:
            params["force_loc"] = force_loc
            params["bucket"] = bucket
            params["location"] = location
            params["output"] = output
            
        return self._client._terrakio_request("GET", "mass_stats/download", params=params)

    @require_api_key
    async def _upload_file(self, file_path: str, url: str, use_gzip: bool = False):
        """
        Helper method to upload a JSON file to a signed URL.
        
        Args:
            file_path: Path to the JSON file
            url: Signed URL to upload to
            use_gzip: Whether to compress the file with gzip
        """
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {file_path}: {e}")
        
        return await self._upload_json_data(json_data, url, use_gzip)

    @require_api_key
    async def _upload_json_data(self, json_data: Union[Dict, List], url: str, use_gzip: bool = False):
        """
        Helper method to upload JSON data directly to a signed URL.
        
        Args:
            json_data: JSON data (dict or list) to upload
            url: Signed URL to upload to
            use_gzip: Whether to compress the data with gzip
        """
        if hasattr(json, 'dumps') and 'ignore_nan' in json.dumps.__code__.co_varnames:
            dumps_kwargs = {'ignore_nan': True}
        else:
            dumps_kwargs = {}
        
        if use_gzip:
            body = gzip.compress(json.dumps(json_data, **dumps_kwargs).encode('utf-8'))
            headers = {
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip'
            }
        else:
            body = json.dumps(json_data, **dumps_kwargs).encode('utf-8')
            headers = {
                'Content-Type': 'application/json'
            }
        
        response = await self._client._regular_request("PUT", url, data=body, headers=headers)
        return response
    
    @require_api_key
    async def download_file(self, 
                        job_name: str,
                        bucket: str,
                        file_type: str,
                        output_path: str,
                        folder: str = None,
                        page_size: int = None,
                      ) -> list:
        """
        Download a file from mass_stats using job name and file name.
        
        Args:
            job_name: Name of the job
            download_all: Whether to download all raw files from the job
            file_type: either 'raw' or 'processed'
            current_page: Current page number for pagination
            page_size: Number of file per page for download
            output_path: Path where the file should be saved
            
        Returns:
            str: Path to the downloaded file
        """


        if file_type not in ("raw", "processed"):
            raise ValueError("file_type must be 'raw' or 'processed'.")

        if file_type == "raw" and page_size is None:
            raise ValueError("page_size is required to define pagination size when downloading raw files.")

        request_body = {
            "job_name": job_name,
            "bucket": bucket,
            "file_type": file_type,
            "folder": folder
        }

        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_files = []

        async def download_urls_batch(download_urls, session):
            for i, url in enumerate(download_urls):
                parsed = urlparse(url)
                path_parts = Path(parsed.path).parts
                try:
                    data_idx = path_parts.index("data") if file_type == "raw" else path_parts.index("outputs")
                    subpath = Path(*path_parts[data_idx + 1:])
                except ValueError:
                    subpath = Path(path_parts[-1])
                file_save_path = output_dir / subpath
                file_save_path.parent.mkdir(parents=True, exist_ok=True)
                self._client.logger.info(f"Downloading file to {file_save_path} ({i+1}/{len(download_urls)})")

                async with session.get(url) as resp:
                    resp.raise_for_status()
                    import aiofiles
                    async with aiofiles.open(file_save_path, 'wb') as file:
                        async for chunk in resp.content.iter_chunked(1048576):  # 1 MB
                            if chunk:
                                await file.write(chunk)

                if not os.path.exists(file_save_path):
                    raise Exception(f"File was not written to {file_save_path}")

                file_size = os.path.getsize(file_save_path)
                self._client.logger.info(f"File downloaded successfully to {file_save_path} (size: {file_size / (1024 * 1024):.4f} mb)")
                output_files.append(str(file_save_path))

        try:
            page = 1
            total_files = None
            downloaded_files = 0
            async with aiohttp.ClientSession() as session:
                while True:
                    params = {
                        "page": page,
                        "page_size": page_size
                    }
                    response = await self._client._terrakio_request("POST", "mass_stats/download_files", json=request_body, params=params)
                    data = response

                    download_urls = data.get('download_urls')
                    if not download_urls:
                        break
                    await download_urls_batch(download_urls, session)
                    if total_files is None:
                        total_files = data.get('subdir_total_files')
                    downloaded_files += len(download_urls)
                    if total_files is not None and downloaded_files >= total_files:
                        break
                    if len(download_urls) < page_size:
                        break  # Last page
                    page += 1
            return output_files
        except Exception as e:
            raise Exception(f"Error in download process: {e}")

    def validate_request(self, request_json: Union[str, List[Dict]]):
        # Handle both file path and direct JSON data
        if isinstance(request_json, str):
            # It's a file path
            with open(request_json, 'r') as file:
                request_data = json.load(file)
        elif isinstance(request_json, list):
            # It's already JSON data
            request_data = request_json
        else:
            raise ValueError("request_json must be either a file path (str) or JSON data (list)")
        
        # Rest of validation logic stays exactly the same
        if not isinstance(request_data, list):
            raise ValueError("Request JSON should contain a list of dictionaries")
        
        for i, request in enumerate(request_data):
            if not isinstance(request, dict):
                raise ValueError(f"Request {i} should be a dictionary")
            required_keys = ["request", "group", "file"]
            for key in required_keys:
                if key not in request:
                    raise ValueError(f"Request {i} should contain {key}")
            try:
                str(request["group"])
            except ValueError:
                ValueError("Group must be string or convertible to string")
            if not isinstance(request["request"], dict):
                raise ValueError("Request must be a dictionary")
            if not isinstance(request["file"], (str, int, list)):
                raise ValueError("'file' must be a string or a list of strings")
            if i == 3:
                break

    async def execute_job(
        self, 
        name: str, 
        output: str, 
        config: Dict[str, Any],
        request_json: Union[str, List[Dict]],  # ← Accept both file path OR data
        region: str = None, 
        overwrite: bool = False, 
        skip_existing: bool = False,  
        location: str = None, 
        force_loc: bool = None, 
        server: str = None
    ) -> Dict[str, Any]:
        """
        Execute a mass stats job.
        
        Args:
            name: The name of the job
            output: The output of the job
            config: The config of the job
            request_json: Path to the request JSON file
            overwrite: Whether to overwrite the job
            skip_existing: Whether to skip existing jobs
            location: The location of the job
            force_loc: Whether to force the location
            server: The server to use
        
        Returns:
            API response as a dictionary
        
        Raises:
            APIError: If the API request fails
        """
        
        def extract_manifest_from_request(request_data: List[Dict[str, Any]]) -> List[str]:
            """Extract unique group names from request data to create manifest list."""
            groups = []
            seen_groups = set()
            
            for item in request_data:
                if not isinstance(item, dict):
                    raise ValueError("Each item in request JSON should be a dictionary")
                    
                if 'group' not in item:
                    raise ValueError("Each item should have a 'group' field")
                    
                group = item['group']
                if group not in seen_groups:
                    groups.append(group)
                    seen_groups.add(group)
                    
            return groups
        
        # # Load and validate request JSON
        # try:
        #     with open(request_json, 'r') as file:
        #         request_data = json.load(file)
        #         if isinstance(request_data, list):
        #             size = len(request_data)
        #         else:
        #             raise ValueError(f"Request JSON file {request_json} should contain a list of dictionaries")
        # except FileNotFoundError as e:
        #     return e
        # except json.JSONDecodeError as e:
        #     return e
        try:
            if isinstance(request_json, str):
                # It's a file path
                with open(request_json, 'r') as file:
                    request_data = json.load(file)
            elif isinstance(request_json, list):
                # It's already JSON data
                request_data = request_json
            else:
                raise ValueError("request_json must be either a file path (str) or JSON data (list)")
                
            if isinstance(request_data, list):
                size = len(request_data)
            else:
                raise ValueError("Request JSON should contain a list of dictionaries")
        except FileNotFoundError as e:
            return e
        except json.JSONDecodeError as e:
            return e

        # Generate manifest from request data (kept in memory)
        try:
            manifest_groups = extract_manifest_from_request(request_data)
        except Exception as e:
            raise ValueError(f"Error extracting manifest from request JSON: {e}")
        
        # Extract the first expression
        first_request = request_data[0]  # Changed from data[0] to request_data[0]
        first_expression = first_request["request"]["expr"]
        
        # Get upload URLs
        upload_result = await self._upload_request(
            name=name, 
            size=size, 
            region=region, 
            sample = first_expression,
            output=output, 
            config=config, 
            location=location, 
            force_loc=force_loc, 
            overwrite=overwrite, 
            server=server, 
            skip_existing=skip_existing
        )
        
        requests_url = upload_result.get('requests_url')
        manifest_url = upload_result.get('manifest_url')
        
        if not requests_url:
            raise ValueError("No requests_url returned from server for request JSON upload")
        
        # Upload request JSON file
        try:
            self.validate_request(request_json)
            
            if isinstance(request_json, str):
                # File path - use existing _upload_file method
                requests_response = await self._upload_file(request_json, requests_url, use_gzip=True)
            else:
                # JSON data - use _upload_json_data method
                requests_response = await self._upload_json_data(request_json, requests_url, use_gzip=True)
                
            if requests_response.status not in [200, 201, 204]:
                # ... rest stays the same
                self._client.logger.error(f"Requests upload error: {requests_response.text()}")
                raise Exception(f"Failed to upload request JSON: {requests_response.text()}")
        except Exception as e:
            raise Exception(f"Error uploading request JSON file {request_json}: {e}")
        
        if not manifest_url:
            raise ValueError("No manifest_url returned from server for manifest JSON upload")
        
        # Upload manifest JSON data directly (no temporary file needed)
        try:
            manifest_response = await self._upload_json_data(manifest_groups, manifest_url, use_gzip=False)
            if manifest_response.status not in [200, 201, 204]:
                self._client.logger.error(f"Manifest upload error: {manifest_response.text()}")
                raise Exception(f"Failed to upload manifest JSON: {manifest_response.text()}")
        except Exception as e:
            raise Exception(f"Error uploading manifest JSON: {e}")
        
        # Start the job
        start_job_task_id = await self.start_job(upload_result.get("id"))
        return start_job_task_id

    @require_api_key
    def cancel_job(self, id: str) -> Dict[str, Any]:
        """
        Cancel a mass stats job by ID.
        
        Args:
            id: The ID of the mass stats job to cancel
            
        Returns:
            API response as a dictionary
            
        Raises:
            APIError: If the API request fails
        """
        return self._client._terrakio_request("POST", f"mass_stats/cancel/{id}")
    
    @require_api_key
    def cancel_all_jobs(self) -> Dict[str, Any]:
        """
        Cancel all mass stats jobs.
        
        Returns:
            API response as a dictionary
            
        Raises:
            APIError: If the API request fails
        """
        return self._client._terrakio_request("POST", "mass_stats/cancel")
    
    @require_api_key
    async def random_sample(
        self,
        name: str,
        config: dict,
        aoi: dict,
        samples: int,
        crs: str,
        tile_size: int,
        res: float,
        output: str,
        year_range: list[int] = None,
        overwrite: bool = False,
        server: str = None,
        bucket: str = None
    ) -> Dict[str, Any]:
        """
        Submit a random sample job.

        Args:
            name: The name of the job
            config: The config of the job
            aoi: The AOI of the job
            samples: The number of samples to take
            crs: The CRS of the job
            tile_size: The tile size of the job
            res: The resolution of the job
            output: The output of the job
            year_range: The year range of the job
            overwrite: Whether to overwrite the job
            server: The server to use
            bucket: The bucket to use

        Returns:
            API response as a dictionary
            
        Raises: 
            APIError: If the API request fails
        """
        payload ={
            "name": name,
            "config": config,
            "aoi": aoi,
            "samples": samples,
            "crs": crs,
            "tile_size": tile_size,
            "res": res,
            "output": output,
            "overwrite": str(overwrite).lower(),
        }
        payload_mapping = {
            "year_range": year_range,
            "server": server,
            "bucket": bucket,
        }
        for key, value in payload_mapping.items():
            if value is not None:
                payload[key] = value
        return await self._client._terrakio_request("POST", "random_sample", json=payload)


    @require_api_key
    def create_pyramids(self, name: str, levels: int, config: dict) -> Dict[str, Any]:
        """
        Create pyramids for a dataset.

        Args:
            name: The name of the job
            levels: The levels of the pyramids
            config: The config of the job

        Returns:
            API response as a dictionary
        """
        payload = {
            "name": name,
            "levels": levels,
            "config": config
        }
        return self._client._terrakio_request("POST", "pyramids/create", json=payload)
    
    @require_api_key
    async def combine_tiles(self, data_name: str, overwrite: bool = True, output: str = "netcdf", max_file_size_mb = 5120) -> Dict[str, Any]:
        """
        Combine tiles for a dataset.

        Args:
            data_name: The name of the dataset
            overwrite: Whether to overwrite the dataset
            output: The output of the dataset

        Returns:
            API response as a dictionary

        Raises:
            APIError: If the API request fails
        """
        payload = {
            'data_name': data_name,
            'folder': "file-gen",
            'output': output,
            'overwrite': str(overwrite).lower(),
            'max_file_size_mb': max_file_size_mb
        }
        return await self._client._terrakio_request("POST", "mass_stats/combine_tiles", json=payload)