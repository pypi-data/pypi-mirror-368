import json
from typing import List, Union

import boto3
from boto3.dynamodb.conditions import Attr, Key
from pydantic import TypeAdapter

from rastless.db.models import AccessToken, BaseColorMap, LayerModel, LayerStepModel, PermissionModel


class Database:
    def __init__(self, table_name, resource=None):
        if not resource:
            resource = boto3.resource("dynamodb")

        self.table_name = table_name
        self.resource = resource
        self.table = self.resource.Table(table_name)

    def scan_table(self, pk_startswith, sk_startswith=None):
        filter_expression = Key("pk").begins_with(pk_startswith)
        if sk_startswith:
            filter_expression &= Key("sk").begins_with(sk_startswith)

        scan_kwargs = {"FilterExpression": filter_expression}

        items_list = []

        done = False
        start_key = None

        while not done:
            if start_key:
                scan_kwargs["ExclusiveStartKey"] = start_key
            response = self.table.scan(**scan_kwargs)
            if items := response.get("Items"):
                items_list.extend(items)
            start_key = response.get("LastEvaluatedKey", None)
            done = start_key is None

        return items_list

    def query(self, query_params: dict) -> List:
        response = self.table.query(**query_params)
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = self.table.query(ExclusiveStartKey=response["LastEvaluatedKey"], **query_params)
            items.extend(response["Items"])

        return items

    def get_item(self, pk, sk, gsi=None):
        response = self.table.get_item(Key={"pk": pk, "sk": sk})
        return response.get("Item")

    def list_layers(self, client=None, region=None, product=None):
        query_params = {"KeyConditionExpression": Key("pk").eq("layer")}
        filter_expressions = []

        if client:
            filter_expressions.append(Attr("client").eq(client))

        if region:
            try:
                numeric_region = int(region)
                filter_expressions.append(Attr("regionId").eq(numeric_region))
            except ValueError:
                return []

        if product:
            filter_expressions.append(Attr("product").eq(product))

        if filter_expressions:
            combined_filter_expression = filter_expressions[0]
            for expr in filter_expressions[1:]:
                combined_filter_expression &= expr

            query_params["FilterExpression"] = combined_filter_expression

        return self.query(query_params)

    def add_permissions(self, permissions: List[PermissionModel]):
        with self.table.batch_writer() as writer:
            for permission in permissions:
                writer.put_item(Item=permission.model_dump(by_alias=True))

    def get_permission(self, permission, layer_id):
        return self.get_item(f"permission#{permission}", f"layer#{layer_id}")

    def get_layers_for_permission(self, permission):
        query_parameters = {
            "KeyConditionExpression": Key("pk").eq(f"permission#{permission}") & Key("sk").begins_with("layer")
        }
        return self.query(query_parameters)

    def get_permission_for_layer_id(self, layer_id):
        query_parameters = {
            "IndexName": "gsi1",
            "KeyConditionExpression": Key("sk").eq(f"layer#{layer_id}") & Key("pk").begins_with("permission"),
        }
        return self.query(query_parameters)

    def add_layer(self, layer: LayerModel):
        self.table.put_item(Item=layer.model_dump(by_alias=True, exclude_none=True))

    def get_layer(self, pk, sk) -> Union[LayerModel, None]:
        if item := self.get_item(pk, sk):
            return LayerModel.model_validate(item)

        return None

    def get_layers(self, layer_ids: set):
        response = self.resource.batch_get_item(
            RequestItems={
                self.table_name: {"Keys": [{"pk": "layer", "sk": f"layer#{layer_id}"} for layer_id in layer_ids]}
            }
        )

        return response["Responses"][self.table_name]

    def delete_layer(self, layer_id: str):
        query_parameters = {"IndexName": "gsi1", "KeyConditionExpression": Key("sk").eq(f"layer#{layer_id}")}
        items = self.query(query_parameters)

        with self.table.batch_writer() as writer:
            for item in items:
                writer.delete_item(Key={"sk": item["sk"], "pk": item["pk"]})

    def delete_permission(self, permission: str):
        query_parameters = {"KeyConditionExpression": Key("pk").eq(f"permission#{permission}")}
        items = self.query(query_parameters)

        with self.table.batch_writer() as writer:
            for item in items:
                writer.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})

    def delete_layer_from_layer_permission(self, permissions: List[PermissionModel]):
        with self.table.batch_writer() as writer:
            for permission in permissions:
                writer.delete_item(
                    Key={"pk": f"permission#{permission.permission}", "sk": f"layer#{permission.layer_id}"}
                )

    def get_layer_step(self, step: str, layer_id: str) -> Union[LayerStepModel, None]:
        response = self.table.get_item(Key={"pk": f"step#{step}", "sk": f"layer#{layer_id}"})
        if item := response.get("Item"):
            return LayerStepModel.model_validate(item)

        return None

    def delete_layer_step(self, step: str, layer_id: str):
        self.table.delete_item(Key={"pk": f"step#{step}", "sk": f"layer#{layer_id}"})

    def get_layer_steps(self, layer_id: str) -> List[LayerStepModel]:
        query_params = {
            "IndexName": "gsi1",
            "KeyConditionExpression": Key("sk").eq(f"layer#{layer_id}") & Key("pk").begins_with("step"),
        }
        items = self.query(query_params)
        adapter = TypeAdapter(List[LayerStepModel])
        return adapter.validate_python(items)

    def add_layer_step(self, layer_step: LayerStepModel):
        self.table.put_item(Item=layer_step.model_dump(by_alias=True))

    def add_color_map(self, color_map: BaseColorMap):
        self.table.put_item(Item=color_map.model_dump(by_alias=True))

    def get_color_map(self, name: str) -> BaseColorMap:
        if item := self.get_item(pk="cm", sk=f"cm#{name}"):
            return BaseColorMap.colormap_factory(item)

    def get_color_maps(self):
        query_parameters = {
            "KeyConditionExpression": Key("pk").eq("cm"),
            "ProjectionExpression": "#name, description",
            "ExpressionAttributeNames": {"#name": "name"},
        }
        return self.query(query_parameters)

    def delete_color_map(self, name: str):
        self.table.delete_item(Key={"pk": "cm", "sk": f"cm#{name}"})

    def create_access_token(self, access_token: AccessToken):
        self.table.put_item(Item=access_token.model_dump(by_alias=True))

    def delete_access_token(self, access_token_id: str):
        self.table.delete_item(Key={"pk": f"token#{access_token_id}", "sk": "token"})

    def get_cached_statistics(self, cache_key_startswith: str) -> List:
        query_params = {
            "IndexName": "gsi1",
            "KeyConditionExpression": Key("sk").eq("cache") & Key("pk").begins_with(cache_key_startswith),
            "ProjectionExpression": "#1",
            "ExpressionAttributeNames": {"#1": "data"},
        }

        items = self.query(query_params)

        return [json.loads(item["data"]) for item in items]

    def set_cached_statistic(self, cache_key: str, data, ttl: int):
        self.table.put_item(Item={"pk": cache_key, "sk": "cache", "data": json.dumps(data), "ttl": ttl})

    def delete_cached_statistics(self, layer_id: str = None, datetime: str = None):
        key_condition_expression = Key("sk").eq("cache")
        if layer_id:
            key_condition_expression &= Key("pk").begins_with(f"cache#{layer_id}")

        query_params = {
            "IndexName": "gsi1",
            "KeyConditionExpression": key_condition_expression,
            "ProjectionExpression": "pk, sk",
        }

        items_to_delete = self.query(query_params)

        if datetime:
            items_to_delete = [item for item in items_to_delete if datetime in item["pk"]]

        with self.table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})
