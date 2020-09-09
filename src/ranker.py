# This Python file uses the following encoding: utf-8

import numpy as np


def rank(my_interests, other_users_id_interests, log=False):  # interests are lists in this moment
    '''
    O segundo argumento é um map, que tem como chave o ID do Telegram do usuário
    e como valor um objeto contendo os interesses dele (Python list) e a posição original
    no vetor de allowed_users. A posição original deve ser ignorada por essa função.
    Essa funcao ja vai receber apenas usuarios elegiveis para serem sugeridos.
    '''
    if len(other_users_id_interests) == 0:
        return None

    my_interests = np.array(my_interests)

    scores = np.zeros((len(other_users_id_interests), 2), dtype=np.uint32)

    for i, user_id in enumerate(other_users_id_interests):
        their_interests = np.array(
            other_users_id_interests[user_id]['interests'])
        their_score = len(np.intersect1d(my_interests, their_interests))

        scores[i][0] = user_id
        scores[i][1] = their_score

    if log:
        print('\nPositional scores:\n', scores)

    ranking = scores[
        np.flip(np.argsort(scores[:, 1]))
    ]  # sort by score (flip to get in decreasing order)

    if ranking[0][1] == 0:
        # O maior score que o usuario conseguiu foi 0...
        return None

    most_similar_user = ranking[0][0]
    # until this point it is a np.uint32
    most_similar_user = int(most_similar_user)

    if log:
        print('\nRanking:\n', ranking)
        # Most Similar User interests
        msu_interests = other_users_id_interests[most_similar_user]['interests']
        print(
            f"\nMost similar: (userId: {most_similar_user}, interests: {msu_interests})"
        )

    return most_similar_user


def test():
    print('===== TESTE =====')

    my_interests = ['0', '1', '3', '6,2', '7,3']

    users_interests = {
        1111: {
            "interests": ['0', '5', '6,0', '7,2'],
            "original_pos": -1
        },
        2222: {
            "interests": ['3', '6,1', '6,2'],
            "original_pos": -1
        },
        3333: {
            "interests": ['5', '7,3'],
            "original_pos": -1
        },
        4444: {
            "interests": ['3', '4', '7,3', '7,4'],
            "original_pos": -1
        },
        5555: {
            "interests": ['0', '1', '4', '7,4', '6,1'],
            "original_pos": -1
        },
        6666: {
            "interests": ['1', '2', '6,2', '7,3'],
            "original_pos": -1
        },
        7777: {
            "interests": ['1', '2', '3', '4', '6,3'],
            "original_pos": -1
        },
        8888: {
            "interests": ['1', '5'],
            "original_pos": -1
        },
    }

    print(rank(my_interests, users_interests, log=True))


if __name__ == '__main__':
    test()
