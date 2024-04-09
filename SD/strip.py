def it(text):
    list = []
    for item in text:
        text = str(text).strip("[")
        text = str(text).strip("]")
        item = str(item).strip("(")
        item = str(item).strip(")")
        item = str(item).strip(",")
        item = str(item).strip("'")
        list.append(item)                 
    return list