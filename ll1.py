# -*- coding:utf-8 -*-
from copy import deepcopy


def input_expr(n):
    start_non = ''
    non_terminal = set()
    whole_set = set()
    expr_dicts = {}
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
    terminal = whole_set - non_terminal
    return start_non, terminal, non_terminal, whole_set, expr_dicts


def cal_first_set(terminal, non_terminal, whole_set):
    first_dict = {'ε': {'ε'}}

    for item in non_terminal:
        first_dict[item] = set([])
    for item in terminal:
        first_dict[item] = {item}

    temp_dict = deepcopy(first_dict)
    while True:
        for non_terminals in non_terminal:
            for expressions in expr_dicts[non_terminals]:
                for index, item in enumerate(expressions):
                    # 如果第一个是终结符直接加入
                    if expressions[index] in terminal:
                        first_dict[non_terminals] |= first_dict[expressions[index]]
                        break
                    else:
                        if len(first_dict[expressions[index]]) == 0:
                            break
                        first_dict[non_terminals] |= first_dict[expressions[index]] - {'ε'}
                        if 'ε' not in first_dict[expressions[index]]:
                            break
                        if index == len(expressions) - 1:
                            first_dict[non_terminals] |= {'ε'}
        if temp_dict == first_dict:
            break
        else:
            temp_dict = deepcopy(first_dict)

    return first_dict


def cal_follow_set(start_non, terminal, non_terminal, first_dict):
    terminal.add('ε')
    follow_dict = {}

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

    return follow_dict


def eliminate_left_recursive(expr_dicts, nonterminal):
    temp_dicts = {}
    for key in expr_dicts:
        alpha = []
        # 存储含有左递归的项
        beta = []
        for expressions in expr_dicts[key]:
            if expressions[0] == key:
                alpha.append(expressions)
            else:
                beta.append(expressions)
        if len(alpha) == 0:
            temp_dicts[key] = expr_dicts[key]
        else:
            key_ = key + '\''
            nonterminal.add(key_)
            temp_dicts[key] = []
            if temp_dicts.get(key_, None) is None:
                temp_dicts[key_] = []
            for item in beta:
                # 不含有左递归的表达式
                temp = item
                temp.append(key_)
                temp_dicts[key].append(temp)
            for item in alpha:
                temp = item[1:]
                temp.append(key_)
                temp_dicts[key_].append(temp)
            temp_dicts[key_].append(['ε'])

    return temp_dicts, nonterminal


def eliminate_left_factor(expr_dicts, nonterminal):
    temp_dicts = {}
    for key in expr_dicts:
        l = r = 0
        flag = True
        while flag:
            if len(expr_dicts[key]) == 1:
                break
            for expression in expr_dicts[key]:
                if r >= len(expression) or expression[r] != expr_dicts[key][0][r]:
                    flag = False
                    break
            if flag:
                r += 1
        prefix = expr_dicts[key][0][l:r]
        if not prefix:
            temp_dicts[key] = expr_dicts[key]
            continue
        key_ = key + '\''
        nonterminal.add(key_)
        temp_dicts[key_] = []
        temp_dicts[key] = []
        prefix.append(key_)
        temp_dicts[key].append(prefix)
        for expression in expr_dicts[key]:
            if not expression[r:]:
                temp = ['ε']
            else:
                temp = expression[r:]
            temp_dicts[key_].append(temp)

    return temp_dicts, nonterminal


def construct_ll1_table(expr_dicts, nonterminal, first_dict, follow_dict):
    table_dict = {}
    for non_terminals in nonterminal:
        table_dict[non_terminals] = {}
        for expression in expr_dicts[non_terminals]:
            # 产生式的头部
            temp = expression[0]
            # 循环temp的first 集合
            for item in first_dict[temp]:
                if item != 'ε':
                    table_dict[non_terminals][item] = expression
            if 'ε' in first_dict[temp]:
                for item in follow_dict[non_terminals]:
                    table_dict[non_terminals][item] = expression

    return table_dict


def ll1(table_dict, string):
    start_state = input()
    string = input().split(' ')
    string.reverse()
    string.insert(0, '$')
    stack = ['$', start_state]
    step = 0
    while True:
        step += 1
        if stack[-1] == string[-1]:
            if stack[-1] == '$':
                break
            print("accept")
            stack.pop()
            string.pop()
        else:
            if stack[-1] == '$':
                return 0
            temp = string[-1]
            head = stack[-1]
            # LL1 分析表的项
            temp_dict = table_dict[head]
            expr = temp_dict.get(temp)
            if expr is None:
                return 0
            else:
                print("{} -> {}".format(head, ' '.join(expr)))
                stack.pop()
                if expr == ['ε']:
                    continue
                rev_expr = expr.copy()
                rev_expr.reverse()
                for item in rev_expr:
                    stack.append(item)
    print("accept")
    print(step)
    return 1


if __name__ == '__main__':
    n = int(input())
    start_nonterminal, terminal, non_terminal, whole_set, expr_dicts = input_expr(n)

    print(expr_dicts)

    expr_dicts, non_terminal = eliminate_left_recursive(expr_dicts, non_terminal)

    # print(expr_dicts)

    expr_dicts, non_terminal = eliminate_left_factor(expr_dicts, non_terminal)

    # print(expr_dicts)

    first_dict = cal_first_set(terminal, non_terminal, whole_set)
    # for item in non_terminal:
    #     print(item, end=' ')
    #     print(first_dict[item])

    print('\n')

    follow_dict = cal_follow_set(start_nonterminal, terminal, non_terminal, first_dict)
    # for item in non_terminal:
    #     print(item, end=' ')
    #     print(follow_dict[item])

    print(expr_dicts)

    table_dict = construct_ll1_table(expr_dicts, non_terminal, first_dict, follow_dict)

    print(table_dict)

    if not ll1(table_dict, expr_dicts):
        print('fail')
