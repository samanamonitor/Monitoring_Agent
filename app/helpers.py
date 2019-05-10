def changes(default, new):
    out = {}
    for k,v in default.items():
        if type(v) is list:
            if set(v) != set(new[k]):
                out[k] = new[k]
        else:
            if v != new[k]:
                out[k] = new[k]
    return out