
"""
Frame assertion setting.
"""
class Ac:
    """
    Set assertion constant.
    Const:
        eq: Assertion is equal.
        nq: Assert inequality.
        at: Assertion is True.
        af: Assertion is False.
        als: Assert a is b.
        alst: Assert a is not b. 
        an: Assertion is None.
        ann: Assertion is not None.
        ain: Assert a in b.
        nin: Assert a in not b.
        ins: Assert isinstance(a, b).
        nins: Assert not isinstances(a, b).
    """
    eq = "'{}'=='{}'"   
    nq = "'{}'!='{}'"
    al = "{} is {}"
    at = "{} is not {}"
    ai = "'{}' in '{}'"
    ani = "not '{}' in '{}'"
    ais = "isinstance({},{})"
    anis = "not isinstance({},{})"
    
    ln = "{}==None"
    lnn = "{}!=None"
    bt = "{}"
    bf = "not {}"
