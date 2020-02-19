#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Fuzzy increasing sequence verifier
"""


def fuzzy_increase(statement_attribute, sequence):
    def __check_increasing(seq: list) -> bool:
        comp = statement_attribute.operation
        count = 0
        max_count = 1
        for i in range(len(seq) - 1):
            if comp(seq[i], seq[i + 1]):
                if count == max_count:
                    return False
                else:
                    count = count + 1
        return True

    check = __check_increasing(sequence)
    if check:
        return True
    if __check_increasing(sequence[check - 1:check] + sequence[check + 1:]) or __check_increasing(
            sequence[check:check + 1] + sequence[check + 2:]):
        return True
    return False
