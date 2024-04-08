def it(text):
    list = []
    if len(text) == 1:
        text = str(text).strip("[")
        text = str(text).strip("]")
        text = str(text).strip("(")
        text = str(text).strip(")")
        text = str(text).strip(",")
        text = str(text).strip("'")
        return text
    else:
        for item in text:
            text = str(text).strip("[")
            text = str(text).strip("]")
            item = str(item).strip("(")
            item = str(item).strip(")")
            item = str(item).strip(",")
            item = str(item).strip("'")
            list.append(item)                 
        return list