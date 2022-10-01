# -*- coding:utf-8 -*-
from copy import deepcopy
from graphviz import Digraph


class dfa:
    def __init__(self, core_item, index):
        self.core = core_item
        self.index = index
        self.expressions = {}
        for item in core_item:
            temp = item.split('->')
            left_part = ''.join(temp[:1])
            right_part = temp[1:]
            right_part = ''.join(right_part)
            temp_exp = right_part.split(' ')
            if self.expressions.get(left_part, None) is None:
                self.expressions[left_part] = [temp_exp]
            else:
                self.expressions[left_part].append(temp_exp)
        self.next = {}
        self.expanded_set = set()
        self.reduction = False
        self.reduction_item = []


def input_expr(n):
    start_non = ''
    non_terminal = set()
    whole_set = set()
    whole_set.add('ε')
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

    s = start_non + '\''
    non_terminal.add(s)
    whole_set.add(s)
    expr_dicts[s] = [[start_non]]
    terminal = whole_set - non_terminal

    return s, terminal, non_terminal, whole_set, expr_dicts


def construct_dfa(expr_dicts, s, non_terminal):
    # dfa 序号
    index = 0
    core = ['.']
    core.extend(expr_dicts[s][0])
    # S' -> .S
    string = s + '->' + ' '.join(core)
    temp_dfa = dfa([string], index)
    core_dict = {string: temp_dfa}
    # print(core)
    core_list = [string]
    cursor = 0
    dfa_list = [temp_dfa]

    # 如果没有新的状态 则循环终止
    while True:
        temp_dfa = dfa_list[cursor]
        print(temp_dfa.expressions)
        # print(len(dfa_list))
        # 扩展产生式
        while True:
            new_dicts = deepcopy(temp_dfa.expressions)
            for key in temp_dfa.expressions:
                for production in temp_dfa.expressions[key]:
                    posi = production.index('.')
                    # 可以进行规约
                    if production[posi] == production[-1] or production[posi + 1] == 'ε':
                        temp_dfa.reduction = True
                        if production[posi] == production[-1]:
                            temp_expr = key + ' -> ' + ' '.join(production[:-1])
                            if temp_expr not in temp_dfa.reduction_item:
                                temp_dfa.reduction_item.append(temp_expr)
                        else:
                            temp_expr = key + ' -> ε'
                            if temp_expr not in temp_dfa.reduction_item:
                                temp_dfa.reduction_item.append(temp_expr)
                    # elif production[posi + 1] == '':
                    #     continue
                    else:
                        if production[posi + 1] in non_terminal and production[posi + 1] not in temp_dfa.expanded_set:
                            # 当前是非终结符，且未扩展
                            temp_non = production[posi + 1]
                            temp_dfa.expanded_set.add(temp_non)
                            if new_dicts.get(temp_non, None) is None:
                                new_dicts[temp_non] = []
                            for expression in expr_dicts[temp_non]:
                                temp = expression.copy()
                                temp.insert(0, '.')
                                new_dicts[temp_non].append(temp)
            if new_dicts == temp_dfa.expressions:
                break
            else:
                temp_dfa.expressions = new_dicts
        # print(temp_dfa.expressions)
        item_dicts = {}
        for key in temp_dfa.expressions:
            for production in temp_dfa.expressions[key]:
                # . 无法后移
                posi = production.index('.')
                if production[posi] == production[-1] or production[posi + 1] == 'ε':
                    continue
                else:
                    temp_production = production.copy()
                    identifier = temp_production[posi + 1]
                    temp_production[posi], temp_production[posi + 1] = temp_production[posi + 1], temp_production[posi]
                    # 核心项字符串
                    string = key + '->' + ' '.join(temp_production)
                    if item_dicts.get(identifier, None) is None:
                        item_dicts[identifier] = [string]
                    else:
                        item_dicts[identifier].append(string)
        # print(item_dicts)
        for key in item_dicts:
            string = item_dicts[key]
            # key 指代通过哪个标识符进行转移
            string_key = '\n'.join(string)
            if string_key in core_list:
                temp_dfa.next[key] = core_dict[string_key]
            else:
                index += 1
                new_dfa = dfa(string, index)
                core_dict[string_key] = new_dfa
                core_list.append(string_key)
                dfa_list.append(new_dfa)
                temp_dfa.next[key] = core_dict[string_key]
        if cursor >= index:
            break
        cursor += 1
    # print(core_dict)
    for _dfa in dfa_list:
        print(_dfa.index)
        print(_dfa.expressions)
        print(_dfa.reduction)
        for identifier in _dfa.next:
            print(identifier, end=' ')
            print(_dfa.next[identifier].index)

    return dfa_list, core_dict


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


def construct_slr1_table(s, whole_set, nonterminal, dfa_list, core_dicts):
    whole_set.add('$')
    terminal = whole_set - nonterminal
    lr0_dicts = {}
    first_dict = cal_first_set(terminal, nonterminal, whole_set)
    follow_dict = cal_follow_set(s, terminal, nonterminal, first_dict)
    print(whole_set)
    print(nonterminal)
    print(terminal)
    print(follow_dict)
    for _dfa in dfa_list:
        lr0_dicts[_dfa.index] = {}
        for item in whole_set:
            if item == 'ε':
                continue
            lr0_dicts[_dfa.index][item] = []
        for item in _dfa.next:
            if item in terminal:
                lr0_dicts[_dfa.index][item].append("s" + str(_dfa.next[item].index))
            else:
                lr0_dicts[_dfa.index][item].append(_dfa.next[item].index)
        if _dfa.reduction:
            for key in core_dicts:
                if _dfa == core_dicts[key]:
                    for exp in _dfa.reduction_item:
                        temp_exp = deepcopy(exp).split(' ')
                        temp_exp = ''.join(temp_exp)
                        temp_exp = temp_exp.split('->')
                        follow_set = follow_dict[temp_exp[0]]
                        for item in follow_set:
                            lr0_dicts[_dfa.index][item].append(exp)
                    break
            if _dfa.index == 1:
                lr0_dicts[_dfa.index]['$'] = ['acc']
    return lr0_dicts


def slr1(table):
    stack = ['$', 0]
    string = input().split(' ')
    string.reverse()
    string.insert(0, '$')
    # print(string)
    step = 1
    while True:
        index = stack[-1]
        step += 1
        op = table[index].get(string[-1], None)
        # print(op)
        if not op:
            return 0
        else:
            if len(op) >= 2:
                return 0
            else:
                if op[0] == 'acc':
                    print('acc')
                    print(step)
                    return 1
                if op[0][0] == 's':
                    stack.append(string[-1])
                    stack.append(int(op[0][1:]))
                    print("shift {} {}".format(string[-1], op[0][1]))
                    string.pop()
                else:
                    lists = op[0].split(' ')
                    # print(lists)
                    right = lists[2:]
                    length = len(right)
                    for i in range(length):
                        if right[i] == 'ε':
                            continue
                        stack.pop()
                        stack.pop()
                    print(op[0])
                    stack.append(lists[0])
                    states = table[stack[-2]].get(stack[-1], None)[0]
                    if states is None:
                        return 0
                    else:
                        stack.append(states)


def draw_dfa(table, dfa_list):
    g = Digraph('G', filename='SLR1_DFA.gv', format='png')
    for key in table:
        _dfa = dfa_list[key]
        content = []
        for keys in _dfa.expressions:
            for exp in _dfa.expressions[keys]:
                temp = str(keys) + '->' + ' '.join(exp)
                content.append(temp)
        strings = '\n'.join(content)
        strings = strings + '\n' + str(_dfa.index)
        if key == 0:
            g.node(str(key), label=strings, color='red')
        else:
            if _dfa.reduction:
                g.node(str(key), label=strings, color='black', shape='doublecircle')
            else:
                g.node(str(key), label=strings, color='black')
    for key in table:
        # if dfa_list[key].reduction:
        #     continue
        for edges in dfa_list[key].next:
            # print(edges)
            g.edge(str(key), str(dfa_list[key].next[edges].index), label=edges)
    g.view()


if __name__ == '__main__':
    n = int(input())
    s, terminal, non_terminal, whole_set, expr_dicts = input_expr(n)
    # print(expr_dicts)

    dfa_list, core_dicts = construct_dfa(expr_dicts, s, non_terminal)
    table = construct_slr1_table(s, whole_set, non_terminal, dfa_list, core_dicts)
    print(table)
    draw_dfa(table, dfa_list)
    if not slr1(table):
        print('fail')
