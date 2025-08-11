import os
import os.path as osp
import sys
from subprocess import PIPE, Popen, STDOUT
from unittest import TestCase, main

DATADIR = osp.join(osp.abspath(osp.dirname(__file__)), "data")


def load_po(fname):
    """load a po file and  return a set of encountered (msgid, msgctx)"""
    msgs = set()
    msgid = msgctxt = None
    with open(fname) as fobj:
        for line in fobj:
            if line.strip() in ("", "#"):
                continue
            if line.startswith("msgstr"):
                assert not (msgid, msgctxt) in msgs
                msgs.add((msgid, msgctxt))
                msgid = msgctxt = None
            elif line.startswith("msgid"):
                msgid = line.split(" ", 1)[1][1:-1]
            elif line.startswith("msgctx"):
                msgctxt = line.split(" ", 1)[1][1:-1]
            elif msgid is not None:
                msgid += line[1:-1]
            elif msgctxt is not None:
                msgctxt += line[1:-1]
    return msgs


class CubePotGeneratorTC(TestCase):
    """test case for i18n pot file generator"""

    def test_i18ncube(self):
        env = os.environ.copy()
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] += os.pathsep
        else:
            env["PYTHONPATH"] = ""

        env["PYTHONPATH"] += osp.join(DATADIR, "libpython")

        # launch i18ncube
        cmd = [sys.executable, "-m", "cubicweb", "i18ncube", "i18ntestcube"]
        proc = Popen(cmd, env=env, stdout=PIPE, stderr=STDOUT)
        stdout, _ = proc.communicate()
        msg = stdout.decode(sys.getdefaultencoding(), errors="replace")
        self.assertEqual(proc.returncode, 0, msg=msg)

        # compare en.po.ref and en.po
        cubedir = osp.join(DATADIR, "libpython", "cubicweb_i18ntestcube")
        msgs = load_po(osp.join(cubedir, "i18n", "en.po.ref"))
        newmsgs = load_po(osp.join(cubedir, "i18n", "en.po"))
        self.assertEqual(msgs, newmsgs)


if __name__ == "__main__":
    main()
