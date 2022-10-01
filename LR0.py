# -*- coding:utf-8 -*-
from copy import deepcopy
from graphviz import Digraph


class dfa:
    def __init__(self, core_item, index):
        self.core = core_item
        self.index = index
        self.expressions = { }
        for item in core_item:
            temp = item.split('->')
            left_part = ''.join(temp[:1])
            right_part = temp[1:]
            right_part = ''.join(right_part)
            temp_exp = right_part.split(' ')
            if self.expressions.get(left_part,None) is None:
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
                new_dfa = dfa(string,index)
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


def construct_lr0_table(s, whole_set, nonterminal, dfa_list, core_dicts):
    whole_set.add('$')
    terminal = whole_set - nonterminal
    lr0_dicts = {}
    print(whole_set)
    print(nonterminal)
    for _dfa in dfa_list:
        lr0_dicts[_dfa.index] = {}
        for item in whole_set:
            lr0_dicts[_dfa.index][item] = []
        for item in _dfa.next:
            if item in terminal:
                lr0_dicts[_dfa.index][item].append("s" + str(_dfa.next[item].index))
            else:
                lr0_dicts[_dfa.index][item].append(_dfa.next[item].index)
        if _dfa.reduction:
            for key in core_dicts:
                if _dfa == core_dicts[key]:
                    for terminals in terminal:
                        for exp in _dfa.reduction_item:
                            lr0_dicts[_dfa.index][terminals].append(exp)
                    break
            if _dfa.index == 1:
                lr0_dicts[_dfa.index]['$'] = ['acc']
    return lr0_dicts


def lr0(table):
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
        if op is None:
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
    g = Digraph('G', filename='LR0_DFA.gv', format='png')
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
    table = construct_lr0_table(s, whole_set, non_terminal, dfa_list, core_dicts)
    print(table)
    draw_dfa(table, dfa_list)
    if not lr0(table):
        print('fail')
