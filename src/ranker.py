import numpy as np


def rank(my_id_interests, other_users_id_interests):  # interests are lists in this moment
    '''
    Essa funcao ja vai receber apenas usuarios elegiveis para serem sugeridos
    '''
    aux = other_users_id_interests.keys()
    iterator = iter(aux)
    return next(iterator)  # first pos


def test():
    print('oit')


if __name__ == '__main__':
    test()
