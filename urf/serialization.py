from flask.json import JSONEncoder

class BartenderJSONEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, "to_dict"):
            return o.to_dict()

        if hasattr(o, "to_json"):
            return o.to_json()

        return super().default(o)