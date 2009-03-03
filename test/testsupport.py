"""
Support routines for all tests.
"""

import sys, os, re
from os.path import *
from subprocess import *


__all__ = ('data', 'find_dirs', 'run_sfood', 'compare_expect')



def find_hg_root(start=__file__):
    "Find the root of a Mercurial repository."
    pdn, dn = None, start
    while not exists(join(dn, '.hg')) and pdn != dn:
        pdn, dn = dn, dirname(dn)
    return dn

# Root of the mercurial repo.
hgroot = find_hg_root()

# Executables directory and executables.
bindir = join(hgroot, 'bin')

# Root location where the data files are to be found.
data = join(dirname(__file__), 'data')


def find_dirs(startdir):
    "Returns a list of directories under startdir."
    rdirs = [startdir]
    for root, dirs, files in os.walk(abspath(startdir)):
        rdirs.extend(join(root, x) for x in dirs)
    return rdirs


def run_sfood(*args, **kw):
    """
    Run sfood with the given args, and capture and return output.
    If 'filterdir' is provided, remove those strings are replaced in the output.
    """
    filterdir = kw.get('filterdir', None)
    cmd = [join(bindir, args[0])] + list(args[1:])
    print >> sys.stderr, 'Running cmd:'
    print >> sys.stderr, ' '.join(cmd)
    print >> sys.stderr
    p = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    out, log = p.communicate()
    if filterdir is not None:
        from_, to_ = filterdir
        out = re.sub(re.escape(from_), to_, out)
        log = re.sub(re.escape(from_), to_, log)

    if p.returncode != 0:
        print >> sys.stderr, "Program failed to run: %s" % p.returncode
        print >> sys.stderr, ' '.join(cmd)

    return out, log



def compare_expect(exp_stdout, exp_stderr, *args, **kw):
    out, err = run_sfood(*args, **kw)

    filterdir = kw.get('filterdir', None)

    for name, efn, text in (('stdout', exp_stdout, out),
                            ('stderr', exp_stderr, err)):
        if efn is None:
            continue
        expected = open(efn).read()
        if filterdir is not None:
            from_, to_ = filterdir
            expected = re.sub(re.escape(from_), to_, expected)

        try:
            assert text == expected, "Unexpected text."
        except AssertionError:
            print >> sys.stderr, "%s:" % name
            print >> sys.stderr, "--------"
            sys.stderr.write(text)
            print >> sys.stderr, "--------"
            print >> sys.stderr
            print >> sys.stderr, "expected:"
            print >> sys.stderr, "--------"
            sys.stderr.write(expected)
            print >> sys.stderr, "--------"
            raise

