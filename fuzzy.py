def _fuzzy_increase(statement_attribute, sequence):
    def __check_increasing(seq):
        comp = statement_attribute.operation
        for i in range(len(seq)-1):
            if comp(seq[i], seq[i+1]):
                return False
        return True

    check = __check_increasing(sequence)
    if check:
        return True
    if __check_increasing(sequence[check-1:check] + sequence[check+1:]) or __check_increasing(sequence[check:check+1] + sequence[check+2:]):
        return True
    return False
