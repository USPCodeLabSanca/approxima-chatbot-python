# This Python file uses the following encoding: utf-8

import numpy as np


def rank(my_interests, other_users_id_interests, log=False):  # interests are lists in this moment
    '''
    O segundo argumento é um map, que tem como chave o ID do Telegram do usuário
    e como valor os interesses dele (Python list).
    Essa funcao ja vai receber apenas usuarios elegiveis para serem sugeridos.
    '''
    if len(other_users_id_interests) == 0:
        return None

    my_interests = np.array(my_interests)

    scores = np.zeros((len(other_users_id_interests), 2), dtype=np.uint32)

    for i, user_id in enumerate(other_users_id_interests):
        their_interests = np.array(
            other_users_id_interests[user_id])
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
        msu_interests = other_users_id_interests[most_similar_user]
        print(
            f"\nMost similar: (userId: {most_similar_user}, interests: {msu_interests})"
        )

    return most_similar_user


def test():
    print('===== TESTE =====')

    my_interests = ['0', '1', '3']

    users_interests = {
        1111: ['0', '5'],    # 2nd tier (score 1)
        2222: ['3'],   # 2nd tier (score 1)
        3333: ['5'],   # 3rd tier (score 0)
        4444: ['3', '4'],    # 2nd tier (score 1)
        5555: ['0', '1', '4'],  # 1st tier (score 2)
        6666: ['1', '2'],    # 2nd tier (score 1)
        7777: ['1', '2', '3', '4'],  # 1st tier (score 2)
        8888: ['1', '5'],    # 2nd tier (score 1)
    }

    print(rank(my_interests, users_interests, log=True))


if __name__ == '__main__':
    test()
