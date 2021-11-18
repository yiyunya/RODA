import json, re, random, sympy, copy
import argparse

# dataPath = './train23k_processed.json'
# newJson = './PreprocessedQuestion_enumeratefiltered2.json'
errorPath = './error_pre.txt'
partialPath = './partial.txt'
signList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


class NUM(object):
    def __init__(self, begin, end, string, index):
        if string.endswith('/'):
            string = string[:-1]
        self.begin = begin
        self.end = end
        self.string = string
        self.index = signList[index]
        # self.index = 'temp_' + signList[index]
        self.num = self.string2num(string)

    def string2num(self, text):
        if text.endswith('%'):
            return float(text[:-1]) / 100
        else:
            if '/' in text:
                [a, b] = text.split('/')
                return float(a) / float(b)
            else:
                return float(text)





def prefix_to_infix(formula):
    op_list = ['+', '-', '*', '/', '^']
    priori = {'^': 3, '*': 2, '/': 2, '+': 1, '-': 1}
    stack = []
    prev_op = None
    for ch in reversed(formula):
        if not ch in op_list:
            stack.append(ch)
        else:
            a = stack.pop()
            b = stack.pop()
            exp = '(' + a + ')' + ch + '(' + b + ')'
            # if prev_op and priori[prev_op] < priori[ch]:
            #     exp = '(' + b + ')' + ch + a
            # else:
            #     exp = a+ch+b
            stack.append(exp)
            prev_op = ch
    return stack[-1]


def postfix_equation(equ_list):
    stack = []
    post_equ = []
    op_list = ['+', '-', '*', '/', '^']
    priori = {'^': 3, '*': 2, '/': 2, '+': 1, '-': 1}
    for elem in equ_list:
        elem = str(elem)
        if elem == '(':
            stack.append('(')
        elif elem == ')':
            while 1:
                op = stack.pop()
                if op == '(':
                    break
                else:
                    post_equ.append(op)
        elif elem in op_list:
            while 1:
                if stack == []:
                    break
                elif stack[-1] == '(':
                    break
                elif priori[elem] > priori[stack[-1]]:
                    break
                else:
                    op = stack.pop()
                    post_equ.append(op)
            stack.append(elem)
        else:
            #if elem == 'PI':
            #    post_equ.append('3.14')
            #else:
            #    post_equ.append(elem)
            post_equ.append(elem)
    while stack != []:
        post_equ.append(stack.pop())
    return post_equ


def checkbrackets(string):
    # print(string)
    if len(string) <= 3:
        return False
    elif string[0] == '(' or string[-1] == ')':
        if '(' not in string[1:-1] and ')' not in string[1:-1]:
            return False
        elif string[0] != '(' or string[-1] != ')':
            return True
        else:
            i = 0
            bracketsCnt = 0
            while i < len(string):
                if string[i] == '(':
                    bracketsCnt += 1
                elif string[i] == ')':
                    bracketsCnt -= 1
                if bracketsCnt == 0:
                    break
                i += 1
            # print(i)
            if i < len(string) - 1:
                return True
            else:
                return False
    elif '(' in string:
        return True
    else:
        return False


def removeNegative(string):
    # print('string:' + string)
    if len(string) <= 2:
        return string
    elif checkbrackets(string):
        i = 0
        j = 0
        res = ''
        while i < len(string):
            bracketsCnt = 0
            res += string[j + 1:i]
            j = i
            while j < len(string):
                if string[j] == '(':
                    bracketsCnt += 1
                elif string[j] == ')':
                    bracketsCnt -= 1
                if bracketsCnt == 0:
                    break
                j += 1
            res += removeNegative(string[i: j + 1])
            i = j
            i += 1
        # print('res:' + res)
        if res[0]!= '-':
            return res
        else:
            string = res
    elif len(list(set(list(string)) & set(list('()+-')))) == 0:
        return string
    if string[0] == '(' and string[-1] == ')':
        brackets = True
        string = string[1:-1]
    else:
        brackets = False
    if string[0] != '+' and string[0] != '-':
        string = '+' + string
    i = 0
    j = 0
    numList = []
    while i < len(string):
        if string[i] == '-' or string[i] == '+':
            j = i + 1
            bracketsCnt = 0
            while j < len(string) and ((string[j] != '-' and string[j] != '+') or bracketsCnt != 0 or j == i + 1):
                if string[j] == '(':
                    bracketsCnt += 1
                elif string[j] == ')':
                    bracketsCnt -= 1
                j += 1
            operator = string[i]
            express = string[i+1: j]
            # print('express:'+express)
            numList.append([operator, removeNegative(express)])
            i = j
        else:
            i += 1
    for k in range(len(numList)):
        if numList[k][0] == '+' and k < len(numList) - 1:
            numList = [numList[k]] + numList[:k] + numList[k + 1:]
            break
        elif numList[k][0] == '+':
            numList = [numList[k]] + numList[:k]
            break
    stringList = [item[0] + item[1] for item in numList]
    string = ''.join(stringList)
    if string[0] == '+':
        string = string[1:]
    # print('????? '+string)
    if brackets and len(string) > 1:
        return '(' + string + ')'
    else:
        return string


def find_express(string):
    index = 0
    operator_cnt = 0
    num_cnt = 0
    while num_cnt < operator_cnt + 1 and index < len(string):
        if string[index] in ['+', '-', '*', '/', '^']:
            operator_cnt += 1
        else:
            num_cnt += 1
        index += 1
    return index


def equation_trans(ans, equation):
    new_equation = [ans]
    while len(equation) > 1:
        operator = equation[0]
        num1 = equation[1: find_express(equation[1:]) + 1]
        num2 = equation[find_express(equation[1:]) + 1:]
        if 'X' in num1 and 'X' in num2:
            print('ERROR0')
        if 'X' in num1:
            var_part = num1
            num_part = num2
        elif 'X' in num2:
            num_part = num1
            var_part = num2
        else:
            print('ERROR1')
            return False
        if operator == '+':
            new_equation = ['-'] + new_equation + num_part
            equation = var_part
        elif operator == '*':
            new_equation = ['/'] + new_equation + num_part
            equation = var_part
        elif operator == '-':
            if num1 == var_part:
                new_equation = ['+'] + new_equation + num_part
            else:
                new_equation = ['-'] + num_part + new_equation
                # new_equation = ['-'] + new_equation + num_part
            equation = var_part
        elif operator == '/':
            if num1 == var_part:
                new_equation = ['*'] + new_equation + num_part
            else:
                new_equation = ['/'] + num_part + new_equation
                # new_equation = ['/'] + new_equation + num_part
            equation = var_part
    return new_equation


def suffix2prefix(seq):
    op_list = ['+', '-', '*', '/', '^']
    op_stack = []
    vT_stack = []
    result_stack = []
    seq.reverse()
    for s in seq:
        while vT_stack and vT_stack[-1] <= 0:
            result_stack.append(op_stack[-1])
            op_stack.pop()
            vT_stack.pop()
        if vT_stack:
            vT_stack[-1] -= 1
        if s in op_list:
            op_stack.append(s)
            vT_stack.append(2)
        else:
            result_stack.append(s)
    while vT_stack and vT_stack[-1] <= 0:
        result_stack.append(op_stack[-1])
        op_stack.pop()
        vT_stack.pop()
    result_stack.reverse()
    return result_stack


def replace1(string):
    re_obj = re.compile('\d+/\d+')
    num_iter = re_obj.finditer(string)
    for iter in num_iter:
        s = iter.start()
        e = iter.end()
        if s == 0 or string[s-1] != '(':
            string = string[0: s] + string[s: e].replace('/', ' / ') + string[e:]
            string = replace1(string)
            break
        elif e == len(string) or string[e] != ')':
            string = string[0: s] + string[s: e].replace('/', ' / ') + string[e:]
            string = replace1(string)
            break
    return string

def find(string):
    re_obj1 = re.compile('\(\d+/\d+\)')
    re_obj2 = re.compile('\d+\.?\d*\%?')
    num_iter1 = re_obj1.finditer(string)
    num_iter2 = re_obj2.finditer(string)
    nums_1, nums_2, nums = [], [], []
    # print('rule1')
    for iter in num_iter1:
        s = iter.start()
        e = iter.end()
        # print(string[s:e])
        nums_1.append(string[s+1:e-1])
        nums.append([[s, e], string[s+1:e-1]])
    # print('rule2')
    sign = 0
    for iter in num_iter2:
        s = iter.start()
        e = iter.end()
        if (s > 0 and e < len(string) and string[s - 1] not in ['(', '/'] and string[e] not in [')', '/']) or (\
            s > 0 and e == len(string) and string[s - 1] not in ['(', '/']) :
            # print(string[s:e])
            nums_2.append(string[s:e])
            if sign < len(nums):
                while sign < len(nums) and s > nums[sign][0][1]:
                    sign += 1
                nums.insert(sign, [[s, e], string[s:e]])
            else:
                nums.append([[s, e], string[s:e]])
        else:
            continue

    num_list = [NUM(item[0][0], item[0][1], item[1], i) for i, item in enumerate(nums)]
    # print([item[1] for item in nums])
    return num_list

def findNum(text):
    numList = []
    nums = re.finditer(r"\d+[\./]?\d*\%?", text)
    for iter in nums:
        begin, end = iter.span()
        numList.append(NUM(begin, end, text[begin: end], len(numList)))
    return numList


def replace(tok, string, new_variable, answer, new_question_list):
    if new_variable in string:
        new_last = string.replace(new_variable, tok, 1).replace('(' + tok + ')', tok)
    elif '几' in string:
        string = string.replace('几', answer, 1)
        new_question_list.append(string)
    else:
        new_question_list.append(string)
    return new_last

def findNum2(text):
    numList = []
    nums = re.finditer(r"\d+[\./]?\d*\%?", text)
    for iter in nums:
        begin, end = iter.span()
        if '/' in text[begin: end]:
            if text[begin: end].endswith('/'):
                numList.append(NUM(begin, end - 1, text[begin: end-1], len(numList)))
                continue
            elif begin == 0 or text[begin-1] is not '(':
                tmp = text[begin: end].split('/')
                numList.append(NUM(begin, begin+len(tmp[0]), tmp[0], len(numList)))
                numList.append(NUM(begin+len(tmp[0])+1, end, tmp[1], len(numList)))
                continue
        numList.append(NUM(begin, end, text[begin: end], len(numList)))
    return numList

bad_case = ['5860', '17520', '20209', '2862', '6448']
# ops = ['+', '-', '*', '/']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='./train23k_processed.json',
                        help='data to perform augmentation')
    parser.add_argument('--out_path', type=str, default='./PreprocessedQuestion_enumeratefiltered2.json',
                        help='output path')

    args= parser.parse_args()
    dataPath = args.data_path
    newJson = args.out_path
    invalid = 0
    partial = 0
    f_err =  open(errorPath, 'w')
    f_partial = open(partialPath, 'w')
    with open(dataPath, 'r') as f:
        origin_data = json.load(f)
    # print(len(origin_data))
    numbers = 0
    valid_numbers = 0
    with open(newJson, 'w+') as f:
        new_id = 1
        new_data = []
        for counter, item in enumerate(origin_data):
        #     # print(counter)
            originID = item["id"]
            numbers += len(item['num_list'])
            # print(originID)
            if originID in bad_case:
                invalid += 1
                print(questionText, file=f_err)
                print(equation_string, file=f_err)
                continue
            questionText = item["text"]
        #     questionText = replace1(questionText)
            equation_string = item["target_norm_post_template"][2:]
            ans = item["answer"]
            questionSplit = re.split(r'[，．？]', questionText)
        #     print(questionText)
            if questionText.count('temp_')*6 > len(questionText)//2:
                invalid += 1
                print(questionText, file=f_err)
                print(equation_string, file=f_err)
                continue
            if len(questionText) < 5 or ('多少' not in questionText and '几' not in questionText and '((())/(()))' not in questionText and '=' not in questionText and '求' not in questionText) and '多' not in questionSplit[-1] or '^' in equation_string or len(equation_string) < 3:
                # if '^' not in equation_string:
                invalid += 1
                print(questionText, file=f_err)
                print(equation_string, file=f_err)
                continue
        #     # if '7/917再加上25得多少' in questionText or '639/25与16的差，商上多少' in questionText:
        #     #     print(questionText, file=f_err)
        #     #     print(equation_string, file=f_err)
        #     #     continue
        #     # if '48/多少=5…3' in questionText:
        #     #     continue
        #     # if '几分之几' in questionText:
        #     #     print(questionText, file=f_err)
        #     #     print(equation_string, file=f_err)
        #     #     continue
            num_list = item["num_list"]
            answer = 'temp_' + signList[len(num_list)]
        #     num_list = findNum2(questionText)
            if len(num_list) < 2:
                invalid += 1
                print(questionText, file=f_err)
                print(equation_string, file=f_err)
                continue
            # no_sub_list = num_list
        #     no_sub_list = []
        #     for num in num_list:
        #         sign = True
        #         for num_1 in num_list:
        #             if num.string in num_1.string and num != num_1:
        #                 sign = False
        #                 break
        #             else:
        #                 continue
        #         if sign and '3.14' not in num.string:
        #             no_sub_list.append(num)
        #     if len(no_sub_list) < 2:
        #         continue
        #
        #
            valid_list = ['temp_' + sym for sym in signList[:len(num_list)]]
            valid_numbers += len(valid_list)
        #     valid_list = []
        #     for variable in no_sub_list:
        #         if variable.string in equation_string:
        #             valid_list.append(variable)
        #             # print(variable.string)
        #     if len(valid_list) == 0:
        #         print(questionText, file=f_err)
        #         print(equation_string, file=f_err)
        #         continue
        #     # valid_list = sorted(valid_list, key=lambda x: len(x.string), reverse=True)
        #     # if '4/2.1的商再加上3.6与2.5的积' in questionText:
        #     #     # continue
        #     #     for v in valid_list:
        #     #         print(v.string)
        #     #     break
        #     # print([item.num for item in num_list])
            for new_variable in valid_list:
                # print(questionText)
                # print(equation_string.count(new_variable))
                # print(equation_string)
                # print(new_variable)
                if equation_string.count(new_variable) > 1:
                    partial += 1
                    print(questionText, file=f_partial)
                    print(equation_string, file=f_partial)
                    continue
        #         # print(equation_string)
        #         num_list_s = sorted(num_list, key=lambda x: len(x.string), reverse=True)
        #         if '3.14%' not in equation_string:
        #             equation_string_n = equation_string.replace('3.14', 'P')
        #         for num in num_list_s:
        #             equation_string_n = equation_string_n.replace(num.string, num.index)

                if new_variable not in equation_string:
                    partial += 1
                    print('ERROR2')
                    print(questionText, file=f_partial)
                    print(equation_string, file=f_partial)
                    continue
        #         # equation_string = equation_string.replace(new_variable.index, 'X', 1).replace(' ', '')
        #         equation_string_l = list(equation_string.replace(' ', ''))
                equation_string_l = copy.deepcopy(equation_string)
                equation_string_l[equation_string_l.index(new_variable)] = 'X'
        #         # print(equation_string)
                pre_equation = suffix2prefix(equation_string_l)
        #         pre_equation = suffix2prefix(postfix_equation(equation_string_l))
                new_equation = equation_trans(ans=answer, equation=pre_equation)
                if not new_equation:
                    partial += 1
                    print(questionText, file=f_partial)
                    print(equation_string, file=f_partial)
                    continue
                # print(new_variable, pre_equation, new_equation)
        #         # print([item.num for item in num_list])
        #         for i in range(len(new_equation)):
        #             if new_equation[i][-1] in signList:
        #                 new_equation[i] = num_list[signList.index(new_equation[i])].string
                new_question_list = []
                for string in questionSplit:
                    # if '多少' in questionText:
                    #     new_last = replace('多少', string, new_variable, answer, new_question_list)
                    # elif '几' in questionText and '几分之几' not in questionText:
                    #     new_last = replace('几', string, new_variable, answer, new_question_list)
                    # elif '几分之几' in questionText:
                    #     new_last = replace('几分之几', string, new_variable, answer, new_question_list)
                    if '多少' in questionText:
                        if new_variable in string and '多少' in string:
                            new_last = string.replace('多少', ' ' + answer + ' ', 1)
                            new_last = new_last.replace(new_variable, '多少', 1).replace('(多少)', '多少')
                        elif new_variable in string:
                            new_last = string.replace(new_variable, '多少', 1).replace('(多少)', '多少')
                        elif '多少' in string:
                            # if string[string.index('多少')+1] != ' ':
                            #     string = string.replace('多少', answer + ' ', 1)
                            # elif string[string.index('多少')-1] != ' ':
                            #     string = string.replace('多少', ' ' + answer, 1)
                            # else:
                            #     string = string.replace('多少', ' ' + answer + ' ', 1)
                            string = string.replace('多少', ' ' + answer + ' ', 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '几分之几' in questionText:
                        if new_variable in string:
                            new_last = string.replace(new_variable, '几分之几', 1).replace('(几分之几)', '几分之几')
                        elif '几分之几' in string:
                            string = string.replace('几分之几', answer, 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '几分 之 几' in questionText:
                        if new_variable in string and '几分 之 几' in string:
                            new_last = string.replace('几分 之 几', ' ' + answer + ' ', 1)
                            new_last = new_last.replace(new_variable, '几分 之 几', 1)
                        elif new_variable in string:
                            new_last = string.replace(new_variable, '几分 之 几', 1)
                        elif '几分 之 几' in string:
                            string = string.replace('几分 之 几', ' ' + answer + ' ', 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '几' in questionText:
                        if new_variable in string and '几' in string:
                            new_last = string.replace('几', ' ' + answer + ' ', 1)
                            new_last = new_last.replace(new_variable, '几', 1).replace('(几)', '几')
                        elif new_variable in string:
                            new_last = string.replace(new_variable, '几', 1).replace('(几)', '几')
                        elif '几' in string:
                            if string[string.index('几')-1] != ' ' and string[string.index('几')+1] != ' ':
                                string = string.replace('几', ' ' + answer + ' ', 1)
                            elif string[string.index('几')-1] != ' ':
                                string = string.replace('几', ' ' + answer, 1)
                            elif string[string.index('几')+1] != ' ':
                                string = string.replace('几', answer + ' ', 1)
                            else:
                                string = string.replace('几', answer, 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '=' in questionText:
                        if new_variable in string and '=' in string:
                            new_last = string.replace('=', answer, 1)
                            new_last = new_last.replace(new_variable, '=', 1)
                        elif new_variable in string:
                            new_last = string.replace(new_variable, '=', 1)
                        elif '=' in string:
                            string = string.replace('=', answer, 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '求' in questionText:
                        if new_variable in string:
                            new_last = '求' + ' ' + string.replace(new_variable, '', 1)
                        elif '求' in string:
                            string = string.replace('求', '', 1) + answer
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '多' in questionSplit[-1]:
                        if new_variable in string:
                            new_last = string.replace(new_variable, '多', 1).replace('(多)', '多')
                        elif '多' in string:
                            if string[string.index('多')+1] != ' ' and string[string.index('多')+1] != ' ':
                                string = string.replace('多', ' '+ answer + ' ', 1)
                            elif string[string.index('多')+1] != ' ':
                                string = string.replace('多', answer + ' ', 1)
                            elif string[string.index('多') - 1] != ' ':
                                string = string.replace('多', ' ' + answer, 1)
                            else:
                                string = string.replace('多', answer, 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                    elif '((())/(()))' in questionText:
                        if new_variable in string:
                            new_last = string.replace(new_variable, '((())/(()))', 1)
                        elif '((())/(()))' in string:
                            string = string.replace('((())/(()))', answer, 1)
                            new_question_list.append(string)
                        else:
                            new_question_list.append(string)
                new_question_list.append(new_last)
                if '' in new_question_list:
                    new_question_list.remove('')
                for i, n in enumerate(new_question_list):
                    if ',' in n:
                        new_question_list[i].replace(',', '')
                # new_question = ','.join(new_question_list) + '？'
                new_num_list = []
                new_sym_list = {}
                i = 0
                new_question = ' , '.join(new_question_list)
                # print(new_question)
                new_question_n = []
                for tok in new_question.split():
                    if 'temp' in tok:
                        if tok not in new_sym_list.keys():
                            new_sym_list[tok] = 'temp_' + signList[i]
                            j = signList.index(tok[-1])
                            if tok in valid_list:
                                new_num_list.append(num_list[j])
                            else:
                                new_num_list.append(ans)
                            new_question_n.append('temp_' + signList[i])
                            i += 1
                    else:
                        new_question_n.append(tok)
                new_question = ' '.join(new_question_n) + '？'

                # print(new_sym_list)
                new_equation_n = [new_sym_list[tok][-1] if 'temp' in tok else tok for tok in new_equation]
                infix = prefix_to_infix(new_equation_n)
                # print(infix)
                infix_norm = str(sympy.sympify(''.join(infix)))
                infix_norm = infix_norm.replace(' ', '')
                infix_norm = infix_norm.replace('**', '^')
                infix_norm = infix_norm.replace('PI', 'P')
                # print(infix_norm)
                infix_norm = removeNegative(infix_norm)
                # print(infix_norm)
                infix_norm = ['temp_' + tok if tok in signList else tok for tok in infix_norm]
                infix_norm = ['PI' if tok=='P' else tok for tok in infix_norm]
                suffix_norm = ['x', '='] + postfix_equation(infix_norm)
                infix_norm = ['x', '='] + infix_norm
                # suffix_norm = postfix_equation(infix)
                # print(suffix_norm)


        #
        #         print('new question:' + new_question)
                new_data.append({'id': str(new_id), 'origin_id': originID, 'target_template': infix_norm,
                                 'target_norm_post_template': suffix_norm, 'num_list': new_num_list,
                                 'text': new_question, 'answer':num_list[signList.index(new_variable[-1])]})
                new_id += 1
        # print(len(new_data))
        # f.write(str(new_data))
        # print(new_id)
        # print(invalid)
        # print(partial)
        # print(numbers)
        # print(valid_numbers)
        f.write(json.dumps(new_data))


if __name__ == '__main__':
    main()
