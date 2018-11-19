def tuple2select(tuple, blankable=False):
    # if blankable == True:
    #     adict = dict(tuple)
    #     adict[''] = ''
    #     return [{"value": k, "text": v} for k, v in adict.items()]

    return [{"value": k, "text": v} for k, v in dict(tuple).items()]


