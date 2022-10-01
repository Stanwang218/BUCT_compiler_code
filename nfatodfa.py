# -*- coding: utf-8 -*-
import copy
import queue
from graphviz import Digraph


class transition:
    def __init__(self, source_state, target_state, character):
        self.source_state = source_state
        self.target_state = target_state
        self.char = character


class nfa:
    def __init__(self, transitions, ac=False):
        self.accepted = ac
        self.transition = transitions


def judge_word(character):
    if 'a' <= character <= 'z' or character == 'ε':
        return True


# 添加与运算符
def regular_model(forms):
    length = len(forms)
    forms_list = list(forms)
    number = 0
    for i in range(length - 1):
        if judge_word(forms[i]) and judge_word(forms[i + 1]):
            forms_list.insert(i + 1 + number, '·')
            number += 1
        if judge_word(forms[i]) and forms[i + 1] == '(':
            forms_list.insert(i + 1 + number, '·')
            number += 1
        if forms[i] == ')' and forms[i + 1] == '(':
            forms_list.insert(i + 1 + number, '·')
            number += 1
        if forms[i] == '*' and forms[i + 1] == '(':
            forms_list.insert(i + 1 + number, '·')
            number += 1
        if forms[i] == '*' and judge_word(forms[i + 1]):
            forms_list.insert(i + 1 + number, '·')
            number += 1
    return ''.join(forms_list)


# 调度场算法
def suffix_expression(forms):
    stack = []
    # 后缀表达式
    suffix = []
    length = len(forms)
    priority = {'(': 0, '|': 1, '·': 2, '*': 3}
    for i in range(length):
        if judge_word(forms[i]):
            suffix.append(forms[i])
        else:
            if forms[i] == ')':
                while stack[-1] != '(':
                    suffix.append(stack[-1])
                    stack.pop()
                # 左括号出栈
                stack.pop()
            # 栈空 或者 优先级低 或者 左括号 直接入栈
            elif len(stack) == 0 or priority[stack[-1]] < priority[forms[i]] or forms[i] == '(':
                stack.append(forms[i])
            elif priority[stack[-1]] >= priority[forms[i]]:
                while priority[stack[-1]] >= priority[forms[i]]:
                    suffix.append(stack[-1])
                    stack.pop()
                    if len(stack) == 0 or stack[-1] == '(':
                        break
                stack.append(forms[i])
    while len(stack) != 0:
        suffix.append(stack[-1])
        stack.pop()
    return ''.join(suffix)


def create_nfa(suffix):
    s = set()
    for i in suffix:
        if 'a' <= i <= 'z':
            s.add(i)
    # 统计所有字母

    word = list(s)
    word.append('ε')
    word.sort()

    table = {}
    stack = []
    dicts = {}
    for index, x in enumerate(word):
        dicts[x] = index
    # store nfa
    sentence_length = len(suffix)
    word_length = len(word)
    index = 0
    # num = 0
    for i in range(sentence_length):
        temp = []
        for j in range(word_length):
            temp.extend([[]])

        # 如果是字母
        if judge_word(suffix[i]):
            tran = transition(index, index + 1, suffix[i])
            temp[dicts[suffix[i]]].append(index + 1)
            # 从index -> index + 1
            _nfa = nfa(tran)
            table[index] = temp
            # num += 1
            stack.append(_nfa)
            # print(table)

        else:
            item1 = copy.deepcopy(temp)
            # 起始点
            item2 = copy.deepcopy(temp)
            # 终点
            if suffix[i] == '*':
                nfa1 = stack[-1]
                # 取栈顶，一个nfa
                stack.pop()

                item1[dicts['ε']].extend([nfa1.transition.source_state, index + 1])
                # [[],[],[],[取出的nfa起点, index+1 终点]]
                table[nfa1.transition.target_state] = item1
                # 将取出的nfa终点连接到item1

                item2[dicts['ε']].extend([nfa1.transition.source_state, index + 1])
                # [[],[],[],[取出的nfa起点, index+1 终点]]

                table[index] = item2
                # 新建nfa起点连接到item2

                tran = transition(index, index + 1, '(' + nfa1.transition.char + ')' + suffix[i])
                _nfa = nfa(tran)
                # print(_nfa.transition.char)
                stack.append(_nfa)
                # print(table)
            elif suffix[i] == '|' or '·':
                nfa1 = stack[-1]
                stack.pop()
                # 第一个nfa
                nfa2 = stack[-1]
                stack.pop()
                # 第二个nfa
                if suffix[i] == '|':
                    tran = transition(index, index + 1, nfa2.transition.char + suffix[i] + nfa1.transition.char)
                    # 构建 a|b
                    item1[dicts['ε']].extend([nfa2.transition.source_state, nfa1.transition.source_state])
                    # 两个nfa的起点连接到新建的起始点
                    table[index] = item1
                    # index 所能到的下标

                    item2[dicts['ε']].extend([index + 1])
                    # [[],[],[],[index+1]]

                    table[nfa2.transition.target_state] = item2
                    table[nfa1.transition.target_state] = item2
                    # a,b的两个终结点会通过ε到达index+1

                    _nfa = nfa(tran)
                    # print(_nfa.transition.char)
                    stack.append(_nfa)
                    # print(table)
                else:
                    # 加入3个ε
                    item3 = copy.deepcopy(temp)
                    item1[dicts['ε']].extend([nfa1.transition.source_state])
                    # 第一个nfa的起始状态

                    item2[dicts['ε']].extend([index + 1])
                    # 新增终点

                    item3[dicts['ε']].extend([nfa2.transition.source_state])
                    # 第二个nfa的起始状态

                    table[nfa2.transition.target_state] = item1
                    # 第二个nfa的终止状态连接到第一个nfa的起始状态

                    table[nfa1.transition.target_state] = item2
                    # 第二个nfa的终止状态连接到新增的终点状态

                    table[index] = item3
                    # 新增起点连接到第二个nfa的起点

                    tran = transition(index, index + 1,
                                      '(' + nfa2.transition.char + ')' + '(' + nfa1.transition.char + ')')
                    _nfa = nfa(tran)
                    stack.append(_nfa)

        index += 2
        temp = []
        for j in range(word_length):
            temp.extend([[]])
        table[index - 1] = temp
        # table[index - 2] = [temp for temp in word_length]
    # index - 2 为起点
    return table, index - 2, word_length, word


# 可接受状态还未确定


# recursive algorithm to calculate e_closure
def e_closure(s,solve_set):
    global nfa_table
    new_state = [s]
    if nfa_table[s][-1]:
        for x in nfa_table[s][-1]:
            if x not in solve_set:
                solve_set.add(x)
                new_state.extend(e_closure(x,solve_set))
    return new_state


def dfa(s, word_length):
    global nfa_table
    global words
    start = tuple(sorted(e_closure(s,set())))
    # 状态集合
    state_set = set()
    dicts = {}
    # dicts is the table of the dfa
    # the type of key is tuple

    state_set.add(start)
    # initialize the set

    q = queue.Queue()
    q.put(start)
    while not q.empty():
        temp = []
        # 当前的tuple
        temp_state = q.get()
        for i in range(word_length):
            temp.append([])
        # temp contains the transition of the word
        for word in range(word_length - 1):
            # to check each word
            target = []
            # target refers to the destination
            for x in temp_state:
                temp_list = nfa_table[x]
                # 当前转移表
                if temp_list[word]:
                    # print(temp_list[word])
                    target.extend(e_closure(temp_list[word][0],set()))

            temp_set = set(sorted(target))
            if len(temp_set) != 0:
                temp[word].extend(list(temp_set))
                if tuple(temp_set) in state_set:
                    continue
                state_set.add(tuple(temp_set))
                q.put(tuple(temp_set))
        dicts[temp_state] = temp
    order_set = {}
    orders = 0
    for sets in state_set:
        order_set[sets] = str(orders)
        orders += 1
    return dicts, order_set


def draw_nfa(table, start, word):
    g = Digraph('G', filename='NFA.gv', format='png')
    for key in table:
        # start是起始
        if key == start:
            g.node(str(key), label=str(key), color='red')
        elif key == start + 1:
            g.node(str(key), label=str(key), color='black',shape='doublecircle')
        else:
            g.node(str(key), label=str(key), color='black')
    for key in table:
        for i, temp in enumerate(table[key]):
            if not temp:
                continue
            else:
                for cursor in temp:
                    # print(word[i])
                    g.edge(str(key), str(cursor), label=word[i])
    g.view()


def draw_dfa(table, start, word, order_set):
    end_order = start + 1
    g = Digraph('G', filename='DFA.gv', format='png')
    for key in table:
        # start是起始
        if start in key:
            if end_order not in key:
                g.node(order_set[key], label=order_set[key], color='red')
            else:
                g.node(order_set[key], label=order_set[key], color='red',shape='doublecircle')
        elif end_order in key:
            g.node(order_set[key], label=order_set[key], color='black',shape='doublecircle')
        else:
            g.node(order_set[key], label=order_set[key], color='black')
    for key in table:
        for i, temp in enumerate(table[key]):
            if not temp:
                continue
            else:
                g.edge(order_set[key], order_set[tuple(temp)], label=word[i])
    g.view()


# def minimize_dfa(table,start,word,order_set):
#     final_table = {}
#     temp_table = {}
#     j = 2
#     for item in table:
#         if (start + 1) in item:
#             final_table[item] = 2
#         else:
#             final_table[item] = 1
#     # print(final_table)
#     for key in table:
#         temp = []
#         for item in table[key]:
#             if item:
#                 # print(tuple(item))
#                 temp.extend([final_table[tuple(item)]])
#             else:
#                 temp.extend([[]])
#         temp_table[key] = temp
#     # print(temp_table)
#     while True:
#         i = 1
#         final_table = {}
#         for key1 in temp_table:
#             for key2 in temp_table:
#                 if key1 == key2:
#                     continue
#                 if temp_table[key1] == temp_table[key2]:
#                     if final_table.get(key2, None) is None:
#                         final_table[key1] = i
#                         final_table[key2] = i
#                         i += 1
#             if final_table.get(key1,None) is None:
#                 final_table[key1] = i
#                 i += 1
#         for key in table:
#             temp = []
#             for item in table[key]:
#                 if item:
#                     # print(tuple(item))
#                     temp.extend([final_table[tuple(item)]])
#                 else:
#                     temp.extend([[]])
#             temp_table[key] = temp
#         if i == j:
#             break
#         j = i
#
#     print(temp_table)
#     return final_table


if __name__ == '__main__':
    # (a|b)*abb
    formula = str(input())
    formula = regular_model(formula)

    print(formula)
    # print(suffix_expression(formula))

    suffix = suffix_expression(formula)

    print(suffix)

    nfa_table, index, word_len, words = create_nfa(suffix)

    print(nfa_table)
    draw_nfa(nfa_table, index, words)

    dfa_table,order_set = dfa(index, word_len)
    print(dfa_table)
    # print(order_set)
    draw_dfa(dfa_table,index,words,order_set)

    # table = minimize_dfa(dfa_table,index,words,order_set)
    # print(table)