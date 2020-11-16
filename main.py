import my_regex


print("B17-515, Magazov Timur's regex library")
print("----------------------------------------")
print("""Поддерживается символ определяющий пустую подстроку ‘#,$’

операции:

Операция ‘или’: r1|r2 (метасимвол ‘|’)

Операция ‘конкатенация’: r1r2

Операция ‘замыкание Клини’: r* (метасимвол ‘*’, метасимвол ‘…’)

Операция ‘символ из набора’: [a1a2a3…] (метасимвол ‘[]’)

Операция ‘повтор выражения’: r{x} (метасимвол ‘{х}’, где x – количество повторов)

Операция ‘нумерованная группа захвата’: (r) (метасимвол ‘()’), выражения из групп захвата нумеруются в порядке их следования.

Операция ‘выражение из нумерованной группы захвата’: \\n (метасимвол ‘\’, n – номер группы захвата)\n\n""")
print("Enter your regular expression")
re = input()

fsm = my_regex.get_fsm_from_re(re)
print(fsm)
string = input("Enter string to check finite state machine:\n")
while string != "END":
    print(fsm.accepts(string))
    string = input("Enter string to check finite state machine:\n")
