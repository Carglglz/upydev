from nanoglob import glob
from upysh import print_table


def _common_start(*strings):
    """ Returns the longest common substring
        from the beginning of the `strings`
    """
    def _iter():
        for z in zip(*strings):
            if z.count(z[0]) == len(z):  # check all elements in `z` are the same
                yield z[0]
            else:
                return

    return ''.join(_iter())


def _autocompsh(rest, silent=True, gts=(40, 0)):
    match = [file.rsplit('/')[-1] for file in glob(f'{rest}*')]
    if len(match) > 1:
        common = _common_start(*match)
        if rest.rsplit('/')[-1] == common or not common:
            if not silent:
                print_table(match, wide=28, format_SH=True, gts=gts)
            else:
                return
        else:
            return common

    else:
        return match
