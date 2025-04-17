import os


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


def file_exists(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for _ in file:
                break
    except FileNotFoundError:
        return False

    return True