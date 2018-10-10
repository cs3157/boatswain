import os


def output(*args):
    print(*args)


def promptInput(prompt, fmt='', default=''):
    if fmt != '':
        promptf = '{} [{}]'.format(prompt, fmt)
    elif default != '':
        promptf = '{} [{}]'.format(prompt, default)
    else:
        promptf = prompt

    promptf = '{}: '.format(promptf)

    while True:
        inp = input(promptf)
        inp = inp.lower()
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
        output('Invalid input (case-insensitive): {}'.format(v))


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

    return inp


def selectorValidator(options, default=''):
    def validator(inp):
        if default != '':
            if inp == default.lower() or inp == '':
                return ''
        if inp in options:
            return ''
        return inp
    return validator


def newFileValidator():
    def validator(inp):
        try:
            if os.path.exists(inp):
                return '{} already exists'.format(inp)
            else:
                open(inp, 'w').close()
                os.unlink(inp)
                return ''
        except OSError as e:
            return str(e)
    return validator
