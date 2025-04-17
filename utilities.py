def readFilePlain(name):
    with open(name) as f:
        lines = f.readlines()
        return [l.strip()+'\n' for l in lines]

def init_tokens():
    ret = []
    with open('token.txt') as f:
        lines = f.readlines()
        for token in lines:
            ret.append(token.strip())
    return ret
