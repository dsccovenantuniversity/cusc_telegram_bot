from cerberus import Validator

ROLES = ["admin", "super_admin"]


def validate_add_admin(input: str):
    # parse id, name and role into a data structure
    # validate input with validation library
    # return data and errors depending on result
    schema = {
        "role": {"type": "string", "allowed": ROLES, "required": True},
        "id": {"type": "integer", "required": True, "coerce": int},
        "name": {"type": "string", "required": True},
    }

    params = extract_kv_from_text(input)

    v = Validator(schema=schema, purge_unknown=True)
    is_valid = v.validate(params)

    if not is_valid:
        return {"data": None, "errors": v.errors}

    return {"data": params, "errors": None}


def extract_kv_from_text(text: str) -> dict:

    lines = text.split("\n")

    key_value_pairs = {}
    for line in lines[1:]:
        kv = line.split("-", maxsplit=1)

        # Ignore invalid lines
        if len(kv) < 2:
            continue

        key = kv[0].strip()
        value = kv[1].strip()

        key_value_pairs[key] = value

    return key_value_pairs
