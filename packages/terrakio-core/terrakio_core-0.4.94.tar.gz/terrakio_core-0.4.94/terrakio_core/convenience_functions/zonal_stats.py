# Standard library imports
import asyncio
import psutil
import random
import uuid
from io import BytesIO
from typing import Optional

# Third-party library imports
import aiohttp
import geopandas as gpd
import nest_asyncio
import pandas as pd
import pyproj
import xarray as xr
from geopandas import GeoDataFrame
from shapely.geometry import box, mapping, shape
from shapely.ops import transform

# Local imports
from .geoquries import request_geoquery_list

nest_asyncio.apply()
class cloud_object(gpd.GeoDataFrame):
    """
    This class is a class used for cloud
    """
    def __init__(self, job_id: str, job_name: str, client=None):

        super().__init__({
            'geometry': [], 
            'dataset': []
        })

        self.job_id = job_id
        self.client = client
        self.job_name = job_name

    def head(self, n = 5):
        """
        Returns the first n files stored in the cloud bucket.
        """
        return asyncio.run(self._head_async(n))

    async def _head_async(self, n = 5):
        """
        Returns the first n files stored in the cloud bucket.

        Args:
            n (int): Number of files to return. Default is 5.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the first n files.
        """

        track_info = await self.client.mass_stats.track_job([self.job_id])
        job_info = track_info[self.job_id]
        status = job_info['status']
        
        if status == "Completed":
            payload = {
                "job_name": job_info["name"],
                "file_type": "raw",
                "bucket": job_info["bucket"],
            }
            result = await self.client._terrakio_request("POST", "mass_stats/download_files", json=payload)
            download_urls = result["download_urls"][:n]
            datasets = []

            async with aiohttp.ClientSession() as session:
                for i, url in enumerate(download_urls):
                    try:
                        self.client.logger.info(f"Downloading dataset {i+1}/{len(download_urls)}...")
                        async with session.get(url) as response:
                            if response.status == 200:
                                content = await response.read()
                                dataset = xr.open_dataset(BytesIO(content))
                                datasets.append(dataset)
                                self.client.logger.info(f"Successfully processed dataset {i+1}")
                            else:
                                self.client.logger.warning(f"Failed to download dataset {i+1}: HTTP {response.status}")
                    except Exception as e:
                        self.client.logger.error(f"Error downloading dataset {i+1}: {e}")
                        continue
                if not datasets:
                    self.client.logger.warning("No datasets were successfully downloaded")
                    return gpd.GeoDataFrame({'geometry': [], 'dataset': []})
                try:
                    json_response = await self.client._terrakio_request(
                        "POST", "mass_stats/download_json", 
                        params={"job_name": job_info['name']}
                    )
                    json_url = json_response["download_url"]
                    
                    async with session.get(json_url) as response:
                        if response.status == 200:
                            json_data = await response.json()
                            self.client.logger.info("Successfully downloaded geometry data")
                            
                            geometries = []
                            max_geometries = min(n, len(json_data), len(datasets))
                            
                            for i in range(max_geometries):
                                try:
                                    geom_dict = json_data[i]["request"]["feature"]["geometry"]
                                    shapely_geom = shape(geom_dict)
                                    geometries.append(shapely_geom)
                                except (KeyError, ValueError) as e:
                                    self.client.logger.warning(f"Error parsing geometry {i}: {e}")
                                    continue
                            
                            min_length = min(len(datasets), len(geometries))
                            if min_length == 0:
                                self.client.logger.warning("No matching datasets and geometries found")
                                return gpd.GeoDataFrame({'geometry': [], 'dataset': []})
                            
                            gdf = gpd.GeoDataFrame({
                                'geometry': geometries[:min_length],
                                'dataset': datasets[:min_length]
                            })
                            
                            self.client.logger.info(f"Created GeoDataFrame with {len(gdf)} rows")
                            try:
                                expanded_gdf = expand_on_variables_and_time(gdf)
                                return expanded_gdf
                            except NameError:
                                self.client.logger.warning("expand_on_variables_and_time function not found, returning raw GeoDataFrame")
                                return gdf
                                
                        else:
                            self.client.logger.warning(f"Failed to download geometry data: HTTP {response.status}")
                            return gpd.GeoDataFrame({'geometry': [], 'dataset': []})
                                    
                except Exception as e:
                        self.client.logger.error(f"Error downloading geometry data: {e}")
                        return gpd.GeoDataFrame({'geometry': [], 'dataset': []})
        
        elif status in ["Failed", "Cancelled", "Error"]:
            raise RuntimeError(f"The zonal stats job (job_id: {self.job_id}) has failed, cancelled, or errored. Please check the job status!")
        
        else:
            raise RuntimeError(f"The zonal stats job (job_id: {self.job_id}) is still running. Please come back at a later time!")

def expand_on_time(gdf):
    """
    Expand datasets on time dimension - each time becomes a new row.
    
    Input: GeoDataFrame with 'geometry' and 'dataset' columns (or variable columns)
    Output: GeoDataFrame with time in multi-index and datasets without time coordinate
    """
    rows = []
    
    for idx, row in gdf.iterrows():
        if 'geometry' in gdf.columns:
            geometry = row['geometry']
        elif gdf.index.name == 'geometry':
            geometry = idx
        else:
            raise ValueError(f"Cannot find geometry in columns: {list(gdf.columns)} or index: {gdf.index.name}")
        
        if 'dataset' in gdf.columns:
            dataset = row['dataset']
            
            if 'time' in dataset.dims:
                for time_val in dataset.time.values:
                    time_slice = dataset.sel(time=time_val).drop_vars('time')
                    rows.append({
                        'geometry': geometry,
                        'time': time_val,
                        'dataset': time_slice
                    })
            else:
                rows.append({
                    'geometry': geometry,
                    'dataset': dataset
                })
        else:
            variable_columns = list(gdf.columns)
            
            first_dataset = row[variable_columns[0]]
            if 'time' in first_dataset.dims:
                time_values = first_dataset.time.values
                
                for time_val in time_values:
                    row_data = {'geometry': geometry, 'time': time_val}
                    
                    for var_col in variable_columns:
                        dataset = row[var_col]
                        time_slice = dataset.sel(time=time_val).drop_vars('time')
                        row_data[var_col] = time_slice
                    
                    rows.append(row_data)
            else:
                row_data = {'geometry': geometry}
                for var_col in variable_columns:
                    row_data[var_col] = row[var_col]
                rows.append(row_data)
    
    result_df = pd.DataFrame(rows)
    
    if 'time' in result_df.columns:
        result_gdf = gpd.GeoDataFrame(result_df, geometry='geometry')
        result_gdf = result_gdf.set_index(['geometry', 'time'])
    else:
        result_gdf = gpd.GeoDataFrame(result_df, geometry='geometry')
        result_gdf = result_gdf.set_index(['geometry'])
    
    result_gdf.attrs = gdf.attrs.copy()
    
    return result_gdf

def expand_on_variables(gdf):
    """
    Expand datasets on variables dimension - each variable becomes a new column.
    
    Input: GeoDataFrame with 'geometry' and 'dataset' columns (or already time-expanded)
    Output: GeoDataFrame with separate column for each variable
    """
    rows = []
    
    for idx, row in gdf.iterrows():
        if 'geometry' in gdf.columns:
            geometry = row['geometry']
        elif hasattr(gdf.index, 'names') and 'geometry' in gdf.index.names:
            if isinstance(idx, tuple):
                geometry_idx = gdf.index.names.index('geometry')
                geometry = idx[geometry_idx]
                time_idx = gdf.index.names.index('time')
                time_val = idx[time_idx]
            else:
                geometry = idx
                time_val = None
        else:
            raise ValueError(f"Cannot find geometry in columns: {list(gdf.columns)} or index: {gdf.index.names}")
        
        if 'dataset' in gdf.columns:
            dataset = row['dataset']
            
            var_names = list(dataset.data_vars.keys())
            
            if len(var_names) <= 1:
                if len(var_names) == 0:
                    continue
            
            if hasattr(gdf.index, 'names') and 'time' in gdf.index.names:
                row_data = {'geometry': geometry, 'time': time_val}
            else:
                row_data = {'geometry': geometry}
            
            for var_name in var_names:
                var_dataset = dataset[[var_name]]
                
                if len(var_dataset.dims) == 0:
                    row_data[var_name] = float(var_dataset[var_name].values)
                else:
                    row_data[var_name] = var_dataset
            
            rows.append(row_data)
        else:
            raise ValueError("Expected 'dataset' column for variable expansion")
    
    result_df = pd.DataFrame(rows)

    if 'time' in result_df.columns:
        result_gdf = gpd.GeoDataFrame(result_df, geometry='geometry')
        result_gdf = result_gdf.set_index(['geometry', 'time'])
    else:
        result_gdf = gpd.GeoDataFrame(result_df, geometry='geometry')
        result_gdf = result_gdf.set_index(['geometry'])
    
    result_gdf.attrs = gdf.attrs.copy()
    
    return result_gdf

def expand_on_variables_and_time(gdf):
    """
    Convenience function to expand on both variables and time.
    Automatically detects which expansions are possible.
    """
    try:
        expanded_on_time = expand_on_time(gdf)
    except Exception as e:
        expanded_on_time = gdf
    
    try:
        expanded_on_variables_and_time = expand_on_variables(expanded_on_time)
        return expanded_on_variables_and_time
    except Exception as e:
        return expanded_on_time
    
def estimate_geometry_size_ratio(queries: list):
    """Calculate size ratios for all geometries relative to the first geometry using bounding box area."""
    
    areas = []
    
    for query in queries:
        geom = shape(query["feature"]["geometry"])
        in_crs = query["in_crs"]
        
        if in_crs and in_crs != 'EPSG:3857':
            transformer = pyproj.Transformer.from_crs(in_crs, 'EPSG:3857', always_xy=True)
            transformed_geom = transform(transformer.transform, geom)
            bbox = box(*transformed_geom.bounds)
            area = bbox.area
        else:
            bbox = box(*geom.bounds)
            area = bbox.area
        
        areas.append(area)    
    base_area = areas[0]
    
    if base_area == 0:
        non_zero_areas = [area for area in areas if area > 0]
        base_area = non_zero_areas[0] if non_zero_areas else 1.0
    
    ratios = []
    for area in areas:
        if area == 0:
            ratios.append(0.1)
        else:
            ratios.append(area / base_area)
    
    return ratios

async def estimate_query_size(
    client,
    quries: list[dict],
):
    first_query = quries[0]

    first_query_dataset = await client.geoquery(**first_query)
    ratios = estimate_geometry_size_ratio(quries)
    total_size_mb = 0
    for i in range(len(ratios)):
        total_size_mb += first_query_dataset.nbytes * ratios[i] / (1024**2)
    return total_size_mb

async def estimate_timestamp_number(
        client,
        quries: list[dict],
):
    if len(quries) <= 3:
        return quries
    sampled_queries = [query.copy() for query in random.sample(quries, 3)]
    for query in sampled_queries:
        query['debug'] = 'grpc'
    result = await request_geoquery_list(client = client, quries = sampled_queries, conc = 5)
    total_estimated_number_of_timestamps = result * len(quries)
    return total_estimated_number_of_timestamps


def get_available_memory_mb():
    """
    Get available system memory in MB
    
    Returns:
        float: Available memory in MB
    """
    memory = psutil.virtual_memory()
    available_mb = memory.available / (1024 * 1024)
    return round(available_mb, 2)

async def local_or_remote(
        client,
        quries: list[dict],
):
    if len(quries) > 1000:
        return {
            "local_or_remote": "remote",
            "reason": "The number of the requests is too large(>1000), please set the mass_stats parameter to True",
        }
    elif await estimate_timestamp_number(client = client, quries = quries) > 25000:
        return {
            "local_or_remote": "remote",
            "reason": "The time taking for making these requests is too long, please set the mass_stats parameter to True",
        }
    elif await estimate_query_size(client = client, quries = quries) > get_available_memory_mb():
        return {
            "local_or_remote": "remote",
            "reason": "The size of the dataset is too large, please set the mass_stats parameter to True",
        }
    else:
        return {
            "local_or_remote": "local",
            "reason": "The number of the requests is not too large, and the time taking for making these requests is not too long, and the size of the dataset is not too large",
        }
    
def gdf_to_json(
    gdf: GeoDataFrame,
    expr: str,
    in_crs: str = "epsg:4326",
    out_crs: str = "epsg:4326",
    resolution: int = -1,
    geom_fix: bool = False,
    id_column: Optional[str] = None,
):
    """
    Convert a GeoDataFrame to a list of JSON requests for mass_stats processing.
    
    Args:
        gdf: GeoDataFrame containing geometries and optional metadata
        expr: Expression to evaluate
        in_crs: Input coordinate reference system
        out_crs: Output coordinate reference system
        resolution: Resolution parameter
        geom_fix: Whether to fix geometry issues
        id_column: Optional column name to use for group and file names
        
    Returns:
        list: List of dictionaries formatted for mass_stats requests
    """
    mass_stats_requests = []
    
    for idx, row in gdf.iterrows():
        request_feature = {
            "expr": expr,
            "feature": {
                "type": "Feature",
                "geometry": mapping(gdf.geometry.iloc[idx]),
                "properties": {}
            },
            "in_crs": in_crs,
            "out_crs": out_crs,
            "resolution": resolution,
            "geom_fix": geom_fix,
        }
        
        if id_column is not None and id_column in gdf.columns:
            identifier = str(row[id_column])
            group_name = f"group_{identifier}"
            file_name = f"file_{identifier}"
        else:
            group_name = f"group_{idx}"
            file_name = f"file_{idx}"
            
        request_entry = {
            "group": group_name,
            "file": file_name,
            "request": request_feature,
        }
        
        mass_stats_requests.append(request_entry)
        
    return mass_stats_requests

async def handle_mass_stats(
    client,
    gdf: GeoDataFrame,
    expr: str,
    in_crs: str = "epsg:4326",
    out_crs: str = "epsg:4326",
    resolution: int = -1,
    geom_fix: bool = False,
    id_column: Optional[str] = None,
):
    request_json = gdf_to_json(gdf=gdf, expr=expr, in_crs=in_crs, out_crs=out_crs, 
                              resolution=resolution, geom_fix=geom_fix, id_column=id_column)
    
    job_response = await client.mass_stats.execute_job(
        name=f"zonal-stats-{str(uuid.uuid4())[:6]}",
        output="netcdf",
        config={},
        request_json=request_json,
        overwrite=True,
    )
    
    # Extract the actual task ID from the response
    if isinstance(job_response, dict) and 'task_id' in job_response:
        return job_response['task_id']  # Return just the string ID
    else:
        return job_response  # In case it's already just the ID


async def zonal_stats(
    client,
    gdf: GeoDataFrame,
    expr: str,
    conc: int = 20,
    in_crs: str = "epsg:4326",
    out_crs: str = "epsg:4326",
    resolution: int = -1,
    geom_fix: bool = False,
    mass_stats: bool = False,
    id_column: Optional[str] = None,
):
    """Compute zonal statistics for all geometries in a GeoDataFrame."""
    if mass_stats:
        mass_stats_id = await handle_mass_stats(
            client = client,
            gdf = gdf,
            expr = expr,
            in_crs = in_crs,
            out_crs = out_crs,
            resolution = resolution,
            geom_fix = geom_fix,
            id_column = id_column,
        )
        job_name = await client.mass_stats.track_job([mass_stats_id])
        job_name = job_name[mass_stats_id]["name"]
        cloud_files_object = cloud_object(job_id = mass_stats_id, job_name = job_name, client = client)
        return cloud_files_object
    
    quries = []
    for i in range(len(gdf)):
        quries.append({
            "expr": expr,
            "feature": {
                "type": "Feature",
                "geometry": mapping(gdf.geometry.iloc[i]),
                "properties": {}
            },
            "in_crs": in_crs,
            "out_crs": out_crs,
            "resolution": resolution,
            "geom_fix": geom_fix,
        })

    local_or_remote_result = await local_or_remote(client= client, quries = quries)
    if local_or_remote_result["local_or_remote"] == "remote":
        raise ValueError(local_or_remote_result["reason"])
    else:
        gdf_with_datasets = await request_geoquery_list(client = client, quries = quries, conc = conc)
        gdf_with_datasets.attrs["cloud_metadata"] = {
            "is_cloud_backed": False,
        } 
        gdf_with_datasets = expand_on_variables_and_time(gdf_with_datasets)
    return gdf_with_datasets

