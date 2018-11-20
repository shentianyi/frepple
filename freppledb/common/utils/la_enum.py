def tuple2select(tuple):
    # if blankable == True:
    #     adict = dict(tuple)
    #     adict[''] = ''
    #     return [{"value": k, "text": v} for k, v in adict.items()]

    return [{"value": k, "text": v} for k, v in dict(tuple).items()]


def enum2select(x):

    return [{"value": a.name, "text": a.value} for a in x]


