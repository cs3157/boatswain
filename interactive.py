import os


def output(*args):
    print(*args)


def promptInput(prompt, fmt='', default=''):
    if fmt != '':
        promptf = f'{prompt} [{fmt}]'
    elif default != '':
        promptf = f'{prompt} [{default}]'
    else:
        promptf = prompt

    promptf = '{promptf}: '

    while True:
        inp = input(promptf)
        if inp != '':
            return inp
        elif default != '' and inp == '':
            return default
        # empty input with no default
        output('Please enter non-empty string.')


def promptValidate(prompt, validator, fmt='', default=''):
    while True:
        inp = promptInput(prompt, fmt=fmt, default=default)
        v = validator(inp)
        if v == '':
            return inp
        output(f'Invalid input (case-insensitive): {v}')


def selectorValidator(options, default=''):
    def validator(inp):
        i = inp.lower()
        if default != '':
            if i == default.lower() or i == '':
                return ''
        if i in options:
            return ''
        return i
    return validator


'''
e.g. promptInput('Do you want to continue?', ['n'], default='y')
input with validation
'''
def promptSelect(prompt, alts, default=''):
    default = default.lower()

    options = []
    if default != '':
        options.append(default.upper())
    for a in alts:
        options.append(a.lower())

    fmt = '/'.join(options)
    validator = selectorValidator(options, default=default)
    inp = promptValidate(prompt, validator, fmt=fmt, default=default)

    return inp.lower()


def newFileValidator():
    def validator(inp):
        try:
            if os.path.exists(inp):
                return f'{inp} already exists'
            else:
                open(inp, 'w').close()
                os.unlink(inp)
                return ''
        except OSError as e:
            return str(e)
    return validator
