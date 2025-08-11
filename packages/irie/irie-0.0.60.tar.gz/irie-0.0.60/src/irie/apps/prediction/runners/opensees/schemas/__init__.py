from pathlib import Path

def load(name):
    import json
    with open(Path(__file__).parents[0]/name, "r") as f:
        return json.load(f)
    

from jsonschema import Draft202012Validator, validators


def _extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(
            validator, properties, instance, schema,
        ):
            yield error

    return validators.extend(
        validator_class, {"properties" : set_defaults},
    )


DefaultValidatingValidator = _extend_with_default(Draft202012Validator)

def default(schema):
    obj = {}
    DefaultValidatingValidator(load(schema)).validate(obj)
    return obj

if __name__ == "__main__":
    obj = {}
    print(default("hwd_conf.schema.json"))