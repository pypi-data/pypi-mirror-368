import uuid

from rastless.config import Cfg
from rastless.db.models import AccessToken, PermissionModel


def add_permission(cfg: Cfg, permission, layer_ids):
    """Add a role to one or multiple layers."""
    permissions = [PermissionModel(permission=permission, layer_id=layer) for layer in layer_ids]
    cfg.db.add_permissions(permissions)


def delete_permission_asdf(cfg: Cfg, permissions):
    """Delete one or multiple permissions."""

    for permission in permissions:
        cfg.db.delete_permission(permission)


def delete_layer_permission(cfg: Cfg, permission, layer_ids):
    """Delete one or multiple layer permissions."""
    permissions = [PermissionModel(permission=permission, layer_id=layer) for layer in layer_ids]
    cfg.db.delete_layer_from_layer_permission(permissions)


def get_permissions(cfg: Cfg, layer_id, permission):
    """Get layer ids for a role or get all permissions for a layer id."""
    items = []

    if permission:
        items = cfg.db.get_layers_for_permission(permission)

    if layer_id:
        items = cfg.db.get_permission_for_layer_id(layer_id)
    return items


def create_access_token(cfg: Cfg, layer_ids: [str], access_token_id: str = None) -> str:
    if not access_token_id:
        access_token_id = str(uuid.uuid4())

    access_token = AccessToken(token=access_token_id, layer_ids=set(layer_ids))
    cfg.db.create_access_token(access_token)

    return access_token_id


def delete_access_token(cfg: Cfg, access_token_id: str):
    cfg.db.delete_access_token(access_token_id)
