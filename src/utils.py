# Tested and it's okay. Preserves the order of the input's elements
def unique_list(sequence):
    seen = dict.fromkeys(sequence)
    return list(seen)
