from typing import List, Set, Union

from boto3.dynamodb.conditions import Key
from pydantic import TypeAdapter

from rastless.commands.validate import validate_colormap_exists
from rastless.config import Cfg
from rastless.core.cog import append_to_timestep, create_new_timestep
from rastless.core.s3 import delete_layer_step_files
from rastless.core.validate import validate_filenames_exists, validate_input_with_append, validate_layer_step_override
from rastless.db.models import LayerModel, LayerStepModel, PermissionModel


def create_layer(cfg: Cfg, permissions, **kwargs):
    layer = LayerModel.model_validate(kwargs)

    validate_colormap_exists(cfg, **kwargs)
    cfg.db.add_layer(layer)

    permission_models = [PermissionModel(permission=permission, layer_id=layer.layer_id) for permission in permissions]
    cfg.db.add_permissions(permission_models)

    return layer.layer_id


def create_timestep(
    cfg: "Cfg",
    filenames: Set[str],
    append: bool,
    datetime: str,
    sensor: str,
    layer_id: str,
    temporal_resolution: str,
    profile: str,
    override: bool,
):
    validate_filenames_exists(set(filenames))
    validate_input_with_append(sensor, append)

    layer_step = cfg.db.get_layer_step(datetime, layer_id)
    override = validate_layer_step_override(layer_step, append, override)

    if layer_step and override:
        delete_layer_step_files(layer_step, cfg)
        create_new_timestep(cfg, filenames, layer_id, datetime, profile, temporal_resolution, sensor)
    elif layer_step and append:
        append_to_timestep(cfg, layer_step, filenames, profile)
    else:
        create_new_timestep(cfg, filenames, layer_id, datetime, profile, temporal_resolution, sensor)


def list_layers(cfg: Cfg, client=None, region=None, product=None):
    """List all layers with optional filtering based on client, region, and product using database queries."""
    return cfg.db.list_layers(client, region, product)


def delete_cache(cfg: Cfg, layer_id=None, datetime=None):
    """Deletes cache from the S3 bucket based on the layer ID and/or datetime.

    Parameters:
    - cfg (Cfg): Configuration and state object, containing the cache_s3 instance.
    - layer_id (str): Optional. UUID of the layer for which the cache needs to be deleted.
    - datetime (str): Optional. Specific timestep to delete cache. Must be used with layer_id.

    Returns:
    - str: Status message about the action taken or any error encountered.
    """
    try:
        if layer_id and datetime:
            cfg.db.delete_cached_statistics(layer_id, datetime)
            response = cfg.cache_s3.delete_cache(layer_id=layer_id, datetime=datetime)
            if response:
                return f"Cache for layer {layer_id} at {datetime} deleted."
            else:
                return "No cache objects found or failed to delete cache."

        elif layer_id:
            cfg.db.delete_cached_statistics(layer_id)
            response = cfg.cache_s3.delete_cache(layer_id=layer_id)
            if response:
                return f"Cache for all timesteps of layer {layer_id} deleted."
            else:
                return "No cache objects found or failed to delete cache."

        else:
            cfg.db.delete_cached_statistics()
            response = cfg.cache_s3.delete_cache()
            if response:
                return "Full cache deleted."
            else:
                return "No cache objects found or failed to delete cache."

    except Exception as e:
        return f"Error deleting cache: {str(e)}"


def delete_layer_timesteps(cfg: Cfg, layer_id: str, timesteps: List[str]):
    """Deletes a LayerStep from the Layer and the S3 bucket.

    Parameters:
    - cfg (Cfg): Configuration and state object, containing the cache_s3 instance.
    - layer_id (str): UUID of the layer for which the timestep needs to be deleted.
    - timesteps (List[str]): List of ISO timesteps to delete. Must be used with layer_id.

    Returns:
    - str: Status message about the action taken or any error encountered.
    """
    try:
        layer_steps = [cfg.db.get_layer_step(step, layer_id) for step in timesteps]
        for layer_step in layer_steps:
            delete_layer_step_files(layer_step, cfg)
            cfg.db.delete_layer_step(layer_step.datetime, layer_id)
        return f"Layer timesteps {timesteps} deleted for layer {layer_id}."
    except Exception as e:
        return f"Error deleting timestep: {str(e)}"


def get_layer_steps(cfg: Cfg, layer_id: str) -> Union[LayerStepModel, None]:
    """Get list of LayerSteps for a given layer_id from the database.

    Parameters:
    - cfg (Cfg): Configuration and state object, containing the cache_s3 instance.
    - layer_id (str): Optional. UUID of the layer for which the timestep needs to be deleted.

    Returns:
    - List[LayerStepModel]: List of LayerStepModel objects for the given layer_id,
    or None if no LayerStepModel objects are found.
    """
    try:
        layer_steps = cfg.db.get_layer_steps(layer_id)
        return layer_steps
    except Exception as e:
        print(f"Error getting layer steps: {str(e)}")
        return None


def get_layer_steps_date_range(
    cfg: Cfg, layer_id: str, start_date: str = None, end_date: str = None
) -> List[LayerStepModel]:
    """Get list of timesteps (datetime strings only) for a given layer_id from the database.

    Parameters:
    - cfg (Cfg): Configuration and state object, containing the database instance.
    - layer_id (str): UUID of the layer for which to retrieve timesteps.
    - start_date (str, optional): Filter timesteps starting from this date (inclusive).
    - end_date (str, optional): Filter timesteps up to this date (inclusive).

    Returns:
    - List[LayerStepModel]: List of layersteps for the given layer_id.
    """
    try:
        condition_expression = Key("sk").eq(f"layer#{layer_id}")
        if start_date and end_date:
            condition_expression &= Key("pk").between(f"step#{start_date}", f"step#{end_date}")
        elif end_date:
            condition_expression &= Key("pk").between("step", f"step#{end_date}")
        elif start_date:
            condition_expression &= Key("pk").between(f"step#{start_date}", "step#9")
        else:
            condition_expression &= Key("pk").begins_with("step")

        query_params = {"IndexName": "gsi1", "KeyConditionExpression": condition_expression, "ScanIndexForward": False}

        items = cfg.db.query(query_params)
        adapter = TypeAdapter(List[LayerStepModel])
        return adapter.validate_python(items)

    except Exception as e:
        print(f"Error getting layer step timesteps: {str(e)}")
        return []
