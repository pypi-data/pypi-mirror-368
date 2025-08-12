import argparse

def generate_argparse_docs(parser):
    """
    Try to generate a nice markdown with all help from a parser
    """
    s = recursive_get_argparse_help(parser, 'avrs', True)
    #print(s)

    with open('out.txt', 'w', encoding='utf-8') as f:
        f.write(s)

def recursive_get_argparse_help(parser, parent_name, is_root):

    s = ''
    if not is_root:
        s += '\n' + '_' * 72 + '\n\n'

    s += '{}\n'.format(parent_name)
    s += '{}\n'.format(parser.format_help())

    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            #s += '{}\n'.format(dir(action))
            #s += '{}\n'.format(action._choices_actions)
            #for a in action._choices_actions:
            #   s += '{}\n'.format(a.dest)
            for subcmd, subpsr in action.choices.items():
                s += recursive_get_argparse_help(subpsr, parent_name + ' ' + subcmd, False)
    return s
