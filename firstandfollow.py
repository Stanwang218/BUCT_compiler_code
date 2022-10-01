# -*- coding: utf-8 -*-
from copy import deepcopy


def input_expr():
    global start_non
    # 输入处理
    for i in range(n):
        sentence = input()
        split1 = sentence.split(' ')
        temp_non = split1[0]
        if i == 0:
            start_non = temp_non
        non_terminal.add(temp_non)
        whole_set.add(temp_non)

        if expr_dicts.get(temp_non, None) is None:
            expr_dicts[temp_non] = []
        right_side = split1[2:]
        l = r = 0
        length = len(right_side)
        while r < length:
            if right_side[r] != '|':
                r += 1
            else:
                expr_dicts[temp_non].append(right_side[l:r])
                for t in range(l, r):
                    whole_set.add(right_side[t])
                r += 1
                l = r
        expr_dicts[temp_non].append(right_side[l:r])
        for t in range(l, r):
            whole_set.add(right_side[t])

        # print(non_terminal)


def cal_first_set():
    terminal = whole_set - non_terminal

    for item in whole_set:
        if item in terminal:
            first_dict[item] = {item}
        else:
            first_dict[item] = set([])

    temp_dict = deepcopy(first_dict)
    while True:
        for non_termninals in non_terminal:
            for expressions in expr_dicts[non_termninals]:
                for index, item in enumerate(expressions):
                    # 如果第一个是终结符直接加入
                    if expressions[index] in terminal:
                        first_dict[non_termninals] |= first_dict[expressions[index]]
                        break
                    else:
                        if len(first_dict[expressions[index]]) == 0:
                            break
                        first_dict[non_termninals] |= first_dict[expressions[index]] - {'ε'}
                        if 'ε' not in first_dict[expressions[index]]:
                            break
                        if index == len(expressions) - 1:
                            first_dict[non_termninals] |= {'ε'}
        if temp_dict == first_dict:
            break
        else:
            temp_dict = deepcopy(first_dict)
    # print(expr_dicts)
    for item in non_terminal:
        print(item, end=' ')
        print(first_dict[item])


def cal_follow_set():
    terminal = whole_set - non_terminal
    terminal.add('ε')

    for item in non_terminal:
        follow_dict[item] = set([])
    follow_dict[start_non].add('$')

    _expr_dict = deepcopy(expr_dicts)
    for key in _expr_dict:
        for expression in _expr_dict[key]:
            expression.append('ε')

    temp_dict = deepcopy(follow_dict)

    while True:
        for non_termninals in non_terminal:
            for expressions in _expr_dict[non_termninals]:
                length = len(expressions)
                for index in range(length - 1):
                    if expressions[index] in non_terminal:
                        follow_dict[expressions[index]] |= first_dict[expressions[index + 1]] - {'ε'}
                        if 'ε' in first_dict[expressions[index + 1]]:
                            follow_dict[expressions[index]] |= follow_dict[non_termninals]
        if temp_dict == follow_dict:
            break
        else:
            temp_dict = deepcopy(follow_dict)

    for item in non_terminal:
        print(item, end=' ')
        print(follow_dict[item])


if __name__ == '__main__':
    n = int(input())
    terminal = set()
    non_terminal = set()
    whole_set = set()
    expr_dicts = {}
    first_dict = {}
    follow_dict = {}
    start_non = ''
    input_expr()
    print(expr_dicts)
    cal_first_set()
    first_dict['ε'] = {'ε'}
    print('\n')
    cal_follow_set()
