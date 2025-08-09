from pydantic import BaseModel


def generate_tool_schema(name: str, description: str, param_schema: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": param_schema,
        },
    }


def generate_param_schema(param_model_class: type[BaseModel]) -> dict:
    param_schema = param_model_class.model_json_schema()
    clean_schema(param_schema)
    return param_schema


def clean_schema(schema: dict):
    # 移除title字段
    if "title" in schema and isinstance(schema["title"], str):
        schema.pop("title", None)
    # 移除值为None的字段
    keys_to_remove = [k for k, v in schema.items() if v is None]
    for key in keys_to_remove:
        del schema[key]
    # 递归处理嵌套字典
    for value in schema.values():
        if isinstance(value, dict):
            clean_schema(value)
