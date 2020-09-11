# Tested and it's okay. Preserves the order of the input's elements
def unique_list(sequence):
    seen = dict.fromkeys(sequence)
    return list(seen)

def make_buttons(cur_page, final_page):
    # All pages are passed as 0-based. Then, when returning the buttons with
    # structure (text, callback_data), callback_data is 0-based and text is 1-based

    button_pairs = []

    if final_page == 0:  # there is only one page, button are not needed
        return button_pairs  # empty

    if final_page <= 4:
        # Sei que nro de botoes é certinho o nro de paginas
        num_buttons = final_page + 1

        for page in np.arange(num_buttons):
            if page == cur_page:
                button_pairs.insert(page, (f'⦗{page + 1}⦘', f'{page}'))
            else:
                button_pairs.insert(page, (f'{page + 1}', f'{page}'))

        return button_pairs

    # For here on it is guaranteed that there are more than 5 pages and, thus,
    # there are always 5 buttons

    # Build the first page button
    if cur_page == 0:
        button_pairs.append(('⦗1⦘', '0'))
    elif cur_page < 3:
        button_pairs.append(('1', '0'))
    else:   # going back to first page is a huge step
        button_pairs.append(('« 1 ', '0'))

    # Build the last page button
    if cur_page == final_page:
        button_pairs.append((f'⦗{final_page + 1}⦘', f'{final_page}'))
    elif cur_page > final_page - 3:
        button_pairs.append((f'{final_page + 1}', f'{final_page}'))
    else:   # going to the last page is a huge step
        button_pairs.append((f'{final_page + 1} »', f'{final_page}'))

    # Middle buttons

    if cur_page < 3:
        index = 1
        for page in np.arange(1, 3):
            if page == cur_page:
                button_pairs.insert(index, (f'⦗{page + 1}⦘', f'{page}'))
            else:
                button_pairs.insert(index, (f'{page + 1}', f'{page}'))
            index += 1
        button_pairs.insert(3, ('4 ›', '3'))

    elif cur_page > final_page - 3:
        index = 1
        for page in np.arange(final_page - 2, final_page):
            if page == cur_page:
                button_pairs.insert(index, (f'⦗{page + 1}⦘', f'{page}'))
            else:
                button_pairs.insert(index, (f'{page + 1}', f'{page}'))
            index += 1
        button_pairs.insert(1, (f'‹ {final_page - 2}', f'{final_page - 3}'))

    else:
        button_pairs.insert(1, (f'‹ {cur_page}', f'{cur_page - 1}'))
        button_pairs.insert(2, (f'⦗{cur_page + 1}⦘', f'{cur_page}'))
        button_pairs.insert(3, (f'{cur_page + 2} ›', f'{cur_page + 1}'))

    return button_pairs

def correct_friends_order(list_of_friends, correct_order):
    '''
        list_of_friends: a list of dicts with all the friend's info (including their _id)
        correct_order: a list of _ids that must be used to correct the order of the friends list

        returns:
            a list containing all dicts with friends infos, now sorted in the right order
    '''

    return [ friend_data for friend_id in correct_order for friend_data in list_of_friends if friend_data['_id'] == friend_id ]