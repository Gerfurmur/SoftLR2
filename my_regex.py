import lexer
import greenery.fsm


class State:
    def __init__(self, name):
        self.name = name
        self.conditions = []

    def add_condition(self, condition):
        self.conditions.append(condition)
        return self

    def get_conditions(self):
        return self.conditions

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name
        return self

    def __repr__(self):
        return [self.name, self.conditions].__repr__()


def concat(avt1, avt2):
    global state_id
    state_id -= 1
    for st in avt2:
        st.set_name(st.get_name() - 1)
        for k, cond in enumerate(st.conditions):
            st.conditions[k] = [cond[0] - 1, cond[1] - 1, cond[2]]
    avt1[-1] = avt2[0]
    return avt2


state_id = 1
unpermitted_states = ["TIMES", "CLINI", "GROUP"]


def create_state_name(token):
    global state_id
    st_start = State(state_id)
    state_id += 1
    st_start.add_condition([state_id - 1, state_id, token.value])
    st_end = State(state_id)
    state_id += 1
    st_end.add_condition([state_id - 1, state_id, ''])
    return [st_start, st_end]


def create_state_bracket(token):
    global state_id
    token = lexer.lexer.token()
    if token.value == "EMPTY":
        token = lexer.lexer.token()
        return []
    st_start = State(state_id)
    state_id += 1
    while token.type != "RBRACKET":
        st_start.add_condition([state_id - 1, state_id, token.value])
        token = lexer.lexer.token()
    if len(st_start.get_conditions()) == 0:
        st_start.add_condition([state_id - 1, state_id, ''])
    st_end = State(state_id)
    state_id += 1
    st_end.add_condition([state_id - 1, state_id, ''])
    return [st_start, st_end]


def create_state_paren(token):
    global state_id
    token = lexer.lexer.token()
    if token.value == "EMPTY":
        token = lexer.lexer.token()
        token = lexer.lexer.token()
        return []
    st_res = []
    while token.type != "RPAREN":
        name_st_lst = create_state_name(token)
        if len(st_res) == 0:
            st_res.extend(name_st_lst)
        else:
            name_st_lst = concat(st_res, name_st_lst)
            st_res.append(name_st_lst[1])
        token = lexer.lexer.token()
    return st_res


def copy_avt(avt):
    global state_id
    states = []
    for state in avt:
        st = State(state_id)
        dif = state_id - state.get_name()
        for cond in state.conditions:
            tmp = cond.copy()
            tmp[0] += dif
            tmp[1] += dif
            st.add_condition(tmp)
        state_id += 1
        states.append(st)
    return states


def create_state_times(avt, token):
    global state_id
    times = int(token.value[1:-1])
    states = []
    for i in range(times - 1):
        states.extend(copy_avt(avt))
    return states


def create_state_clini(avt):
    global state_id
    avt[-1].add_condition([avt[-1].get_name(), avt[0].get_name(), ''])
    avt[0].add_condition([avt[0].get_name(), avt[-1].conditions[0][1], ''])
    return avt


def create_state_group(avt):
    st = copy_avt(avt)
    return st


def re_pars(reg):
    global state_id, unpermitted_states
    lexer.lexer.input(reg)
    states = []
    last_token = None
    gr_avts = []
    last_avt = None
    or_st = []
    while True:
        tok = lexer.lexer.token()
        if not tok:
            break
        if tok.type == "LBRACKET":
            last_avt = create_state_bracket(tok)
            states.extend(last_avt)
        elif tok.type == "LPAREN":
            last_avt = create_state_paren(tok)
            gr_avts.append(last_avt)
            states.extend(last_avt)
        elif tok.type == "TIMES":
            if not last_token is None and last_token in unpermitted_states:
                raise ValueError("unexpected symbol before {n}")
            states.extend(create_state_times(last_avt, tok))
        elif tok.type == "CLINI":
            if not last_token is None and last_token in unpermitted_states:
                raise ValueError("unexpected symbol before *")
            create_state_clini(last_avt)
        elif tok.type == "GROUP":
            gr_num = int(tok.value[1:])
            if len(gr_avts) < gr_num:
                raise ValueError("wrong group pointer number")
            states.extend(create_state_group(gr_avts[gr_num - 1]))
        elif tok.type == "NAME":
            last_avt = create_state_name(tok)
            states.extend(last_avt)
        else:
            states[0].add_condition([states[0].get_name(), state_id, ''])
            or_st.append(states[-1])
        last_token = tok
    for st in or_st:
        st.conditions[0][1] = state_id
    states.append(State(state_id))
    nka = {}
    for st in states:
        nka[st.get_name()] = st.conditions
    return nka


def nka_to_dka(nka):
    for st in nka:
        if len(nka[st]) == 0:
            break
        poper = []
        for k, cond in enumerate(nka[st]):
            if cond[2] == '':
                nka[st].extend(nka[cond[1]])
                if len(nka[cond[1]]) == 0:
                    continue
                poper.append(k)
        for z, i in enumerate(poper):
            nka[st].pop(i - z)
    return nka


def get_fsm_from_re(re):
    global state_id
    state_id = 1
    alphabet = set()
    q_states = set()
    finals = set()
    initial = 1
    map = {}
    nka = re_pars(re)
    dka = nka_to_dka(nka)
    for i, st in enumerate(dka):
        q_states.add(st)
        map[st] = {}
        for cond in nka[st]:
            map[st][cond[2]] = cond[1]
            alphabet.add(cond[2])
            if len(nka[cond[1]]) == 0:
                finals.add(st)
    res_fsm = greenery.fsm.fsm(alphabet, q_states, initial, finals, map)
    res = res_fsm.reduce()
    return res


if __name__ == "__main__":
    data = "(r|e)*|o*"
    res = re_pars(data)
    print(res)
    fs = get_fsm_from_re(data)
    print(fs)
    print(fs.accepts(""))           # True
    print(fs.accepts("r|e"))        # True
    print(fs.accepts("r|er|e"))     # True
    print(fs.accepts("reer"))       # False
    print(fs.accepts("o"))          # True

    data = "(ab)c\\1[qw]*f|hello{4}"
    my_fsm = get_fsm_from_re(data)
    print(my_fsm)
    print(my_fsm.accepts("abcabqqf"))   # True
    print(my_fsm.accepts("abcabqq"))    # False
    print(my_fsm.accepts("abcabqf"))    # True
    print(my_fsm.accepts("abcabf"))     # True
    print(my_fsm.accepts("a"))          # False
    print(my_fsm.accepts("ab"))         # False
    print(my_fsm.accepts("abc"))        # False
    print(my_fsm.accepts("abca"))       # False
    print(my_fsm.accepts("abcab"))      # False
    print(my_fsm.accepts("h"))          # False
    print(my_fsm.accepts("he"))         # False
    print(my_fsm.accepts("hel"))        # False
    print(my_fsm.accepts("hell"))       # False
    print(my_fsm.accepts("hello"))      # False
    print(my_fsm.accepts("helloo"))     # False
    print(my_fsm.accepts("hellooo"))    # False
    print(my_fsm.accepts("helloooo"))   # True

