# -*- coding:utf-8 -*-
from copy import deepcopy
from graphviz import Digraph


class dfa:
    def __init__(self, core_item, index):
        self.core = core_item
        self.index = index
        self.expressions = {}
        self.search_symbol = {}
        print(core_item)
        for item in core_item:
            split_list = item.split(',')
            temp = split_list[0]
            temp = ''.join(temp)

            temp = temp.split('->')
            left_part = ''.join(temp[:1])
            right_part = temp[1:]
            right_part = ''.join(right_part)
            temp_exp = right_part.split(' ')
            if self.expressions.get(left_part, None) is None:
                self.expressions[left_part] = [temp_exp]
            else:
                self.expressions[left_part].append(temp_exp)
            search_temp = split_list[1]
            if self.search_symbol.get(left_part,None) is None:
                self.search_symbol[left_part] = []
            # search_temp = list(map(str,search_temp))

            search_temp = search_temp.split(' ')
            # print(search_temp)
            for x in search_temp:
                self.search_symbol[left_part].append([x])
            #     self.search_symbol[left_part] = [search_temp]
            # else:
            #     self.search_symbol[left_part].append(search_temp)
        self.next = {}
        self.expanded_set = set()
        self.reduction = False
        self.reduction_item = []
        self.search_item = []


def input_expr(n):
    start_non = ''
    non_terminal = set()
    whole_set = set()
    whole_set.add('$')
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


def construct_dfa(expr_dicts, s, non_terminal,first_dict):
    # dfa 序号
    index = 0
    core = ['.']
    core.extend(expr_dicts[s][0])
    # S' -> .S
    string = s + '->' + ' '.join(core) + ',$'
    temp_dfa = dfa([string], index)
    # temp_dfa.search_symbol[s] = [['$']]
    # string += ',$'
    core_dict = {string: temp_dfa}
    # print(core)
    core_list = [string]
    cursor = 0
    dfa_list = [temp_dfa]

    # 如果没有新的状态 则循环终止
    while True:
        temp_dfa = dfa_list[cursor]
        print()
        # print(temp_dfa.expressions)
        # print(len(dfa_list))
        # 扩展产生式
        while True:
            new_dicts = deepcopy(temp_dfa.expressions)
            for key in temp_dfa.expressions:
                for i,production in enumerate(temp_dfa.expressions[key]):
                    posi = production.index('.')
                    # 可以进行规约
                    if production[posi] == production[-1] or production[posi + 1] == 'ε':
                        temp_dfa.reduction = True
                        if production[posi] == production[-1]:
                            # 规约项
                            temp_expr = key + ' -> ' + ' '.join(production[:-1])
                            if temp_expr not in temp_dfa.reduction_item:
                                temp_dfa.reduction_item.append(temp_expr)
                                temp_dfa.search_item.append(temp_dfa.search_symbol[key][i])
                        else:
                            temp_expr = key + ' -> ε'
                            if temp_expr not in temp_dfa.reduction_item:
                                temp_dfa.reduction_item.append(temp_expr)
                                temp_dfa.search_item.append(temp_dfa.search_symbol[key][i])
                    # elif production[posi + 1] == '':
                    #     continue
                    else:
                        if production[posi + 1] in non_terminal and production[posi + 1] not in temp_dfa.expanded_set:
                            # 当前是非终结符，且未扩展
                            temp_non = production[posi + 1]
                            # 当前的非终结符
                            temp_dfa.expanded_set.add(temp_non)
                            if new_dicts.get(temp_non, None) is None:
                                new_dicts[temp_non] = []
                            if temp_dfa.search_symbol.get(temp_non, None) is None:
                                temp_dfa.search_symbol[temp_non] = []
                            search_str = deepcopy(production[posi + 2:])
                            print(search_str)
                            print(temp_dfa.search_symbol)
                            search_str.extend(temp_dfa.search_symbol[key][i])
                            ans = cal_first_set_in_a_string(first_dict,search_str,terminal,non_terminal)
                            # print(ans)
                            for expression in expr_dicts[temp_non]:
                                temp = expression.copy()
                                temp.insert(0, '.')
                                new_dicts[temp_non].append(temp)
                                temp_dfa.search_symbol[temp_non].append(list(ans))
            if new_dicts == temp_dfa.expressions:
                break
            else:
                temp_dfa.expressions = new_dicts
        # print(temp_dfa.expressions)
        item_dicts = {}
        for key in temp_dfa.expressions:
            for i,production in enumerate(temp_dfa.expressions[key]):
                # . 无法后移
                posi = production.index('.')
                if production[posi] == production[-1] or production[posi + 1] == 'ε':
                    continue
                else:
                    temp_production = production.copy()
                    identifier = temp_production[posi + 1]
                    temp_production[posi], temp_production[posi + 1] = temp_production[posi + 1], temp_production[posi]
                    # 核心项搜索符字符串
                    string = key + '->' + ' '.join(temp_production) + ',{}'.format(' '.join(temp_dfa.search_symbol[key][i]))

                    # print(string)
                    # string 是移动后的产生式
                    # 做一个记录移动哪个identifier: 产生式 string
                    if item_dicts.get(identifier, None) is None:
                        item_dicts[identifier] = [string]
                    else:
                        item_dicts[identifier].append(string)
        # print(item_dicts)
        for key in item_dicts:
            string = item_dicts[key]
            # key 指代通过哪个标识符进行转移
            # [[]]
            string_key = '\n'.join(string)
            # 该核心项已经出现
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
        print(_dfa.search_symbol)
        print(_dfa.reduction)
        print(_dfa.reduction_item)
        print(_dfa.search_item)
        for identifier in _dfa.next:
            print(identifier, end=' ')
            print(_dfa.next[identifier].index)

    return dfa_list, core_dict


def construct_lr1_table(s, whole_set, nonterminal, dfa_list, core_dicts):
    whole_set.add('$')
    terminal = whole_set - nonterminal
    lr1_dicts = {}
    for _dfa in dfa_list:
        lr1_dicts[_dfa.index] = {}
        for item in whole_set:
            lr1_dicts[_dfa.index][item] = []
        for item in _dfa.next:
            if item in terminal:
                lr1_dicts[_dfa.index][item].append("s" + str(_dfa.next[item].index))
            else:
                lr1_dicts[_dfa.index][item].append(_dfa.next[item].index)
        if _dfa.reduction:
            for key in core_dicts:
                if _dfa == core_dicts[key]:
                    for i,item in enumerate(_dfa.reduction_item):
                        for items in _dfa.search_item[i]:
                            lr1_dicts[_dfa.index][items].append(item)
                    break
            if _dfa.index == 1:
                lr1_dicts[_dfa.index]['$'] = ['acc']
    return lr1_dicts


def lr1(table):
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
            for index,exp in enumerate(_dfa.expressions[keys]):
                search_temp = '/'.join(_dfa.search_symbol[keys][index])
                temp = str(keys) + '->' + ''.join(exp) + ',{}'.format(search_temp)
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


def cal_first_set_in_a_string(first_dict, string,terminal,non_terminal):
    ans = set()
    print(string)
    for i,item in enumerate(string):
        if item in terminal:
            ans.add(item)
            break
        else:
            temp_set = first_dict[item]
            ans |= temp_set - {'ε'}
            if 'ε' not in first_dict[item]:
                break
        if i == len(string) - 1:
            ans.add('ε')
    return ans


if __name__ == '__main__':
    n = int(input())
    s, terminal, non_terminal, whole_set, expr_dicts = input_expr(n)
    # print(expr_dicts)
    first_dict = cal_first_set(terminal, non_terminal, whole_set)
    print(first_dict)
    dfa_list, core_dicts = construct_dfa(expr_dicts, s, non_terminal,first_dict)
    table = construct_lr1_table(s, whole_set, non_terminal, dfa_list, core_dicts)
    print(table)
    draw_dfa(table, dfa_list)
    if not lr1(table):
        print('fail')
