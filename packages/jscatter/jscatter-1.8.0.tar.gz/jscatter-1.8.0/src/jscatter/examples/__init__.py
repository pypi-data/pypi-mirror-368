# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2024  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Some examples to show how to use Jscatter.

Functions show the code or run the examples in example directory.



"""

import os
import glob
import re
import platform
import subprocess
import tempfile
import numbers

from .. import graceplot
from .particlesWithInteraction import particlesWithInteraction

platformname = platform.uname()[0]

_path_ = os.path.realpath(os.path.dirname(__file__))
_expath = _path_
datapath = os.path.join(_expath, 'exampleData')
imagepath = os.path.join(_expath, 'images')


def _runsInNotebook():
    """
    Test if working in terminal or notebook

    Returns
    -------
        bool

    """
    try:
        ipy_str = str(type(get_ipython()))
        if 'zmqshell' in ipy_str:
            return 'jupyter'
        if 'terminal' in ipy_str:
            return False  # 'ipython'
    except:
        return False  # 'terminal'


isNotebook = _runsInNotebook()


def _multiple_replace(string, rep_dict):
    # from https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
    pattern = re.compile("|".join([re.escape(k) for k in sorted(rep_dict, key=len, reverse=True)]), flags=re.DOTALL)
    return pattern.sub(lambda x: rep_dict[x.group(0)], string)


def _multiple_replace2(string, rep_dict):
    # from https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
    for k, v in rep_dict.items():
        pattern = re.compile(k, flags=re.DOTALL)
        string = pattern.sub(v, string)
    return string


mplotreplace = {'.grace(': '.mplot(',
                '.plot(': '.Plot(',
                '.save(': '.Save(',
                '.xaxis(': '.Xaxis(',
                '.yaxis(': '.Yaxis(',
                '.legend(': '.Legend(',
                '.clear(': '.Clear(',
                '.title(': '.Title(',
                '.subtitle(': '.Subtitle(',
                '.multi(': '.Multi(',
                '.agr': '.png',
                '.text': '.Text',
                "(r'": "('",
                '.line': '.Arrow',
                r'\xp': 'pi', r'\N': '',
                'new_graph': 'Subplot',
                }
headlessreplace = {'fig.show()': 'fig.savefig("lastopenedplots_0.png")',
                   'fig0.show()': 'fig.savefig("lastopenedplots_0.png")',
                   'fig1.show()': 'fig.savefig("lastopenedplots_1.png")',
                   'fig2.show()': 'fig.savefig("lastopenedplots_2.png")',
                   'fig3.show()': 'fig.savefig("lastopenedplots_3.png")',
                   'fig4.show()': 'fig.savefig("lastopenedplots_4.png")',
                   'fig5.show()': 'fig.savefig("lastopenedplots_5.png")',
                   'pyplot.show': 'js.mpl.show',
                   }


def _getexamples():
    exfiles = glob.glob(_expath + '/example_*.py')
    return sorted(exfiles)


def showExampleList():
    """
    Show an updated list of all examples.

    Currently, availible examples ::

    """
    print('Example path : ', _expath)
    exfiles = _getexamples()
    for i, ff in enumerate(exfiles):
        print(i, '  ', os.path.basename(ff))


# string with example filenames for documentation appended to __doc__
_examplelist=''.join(['      {0:}  {1:} \n'.format(i, os.path.basename(ff)) for i, ff in enumerate(_getexamples())])
showExampleList.__doc__ += _examplelist + '\n'


def runExample(example, usempl=False):
    """
    Run example by number or name.

    Example and saved files go to JscatterExamples/example_name in the current working directory.

    Parameters
    ----------
    example: string,int
        Filename or number of the example to run
    usempl : bool, default False
        For using mpl set to True

    Examples
    -------- ::

     import jscatter as js
     js.examples.runExample('daily_use')

    """
    if not graceplot.GraceIsInstalled or isNotebook:
        usempl = True

    exfiles = _getexamples()
    if isinstance(example, numbers.Integral):
        example = exfiles[example]
        print('-----------------------------------')
        print(example)
    else:
        for ef in exfiles:
            if example in ef:
                example = ef
                break

    cwd = os.getcwd()
    # try and in anny case go back to cwd
    try:
        # change path to write into subfolder
        head, exname = os.path.split(os.path.splitext(example)[0])
        temppath = os.path.join(cwd, 'jscatterExamples', exname)
        if not os.path.exists(temppath):
            os.makedirs(temppath)
        os.chdir(temppath)
        with open(example) as f:
            if usempl:
                if 'grace' in example or 'makeJ' in example:
                    print('This example is not fo r mpl.')
                    return
                file = f.read()
                file = _multiple_replace2(file, {r'\.grace\(\d\.?\d?,\s?\d\.?\d?\)': ".mplot()"})
                file = _multiple_replace(file, mplotreplace)
            else:
                file=f.read()
            if graceplot._headless:
                print('headless')
                file = _multiple_replace(file, headlessreplace)
                # append this to close all opened mpl figures
                file+='\n\njs.mpl.close("all")\n\n'

        # now do it
        exec(file, {})
    finally:
        os.chdir(cwd)

    # write the executed file to the subfolder
    with open(os.path.join(temppath, exname+'.py'), 'w') as out_file:
        out_file.writelines(file)

    return


def showExample(example='.', usempl=False):
    """
    Opens example in default editor.

    Parameters
    ----------
    example : string, int
        Filename or number.
        If '.' the folder with the examples is opened.
    usempl : bool, default False
        For using mpl set to True.
        Then mpl examples are shown.

    """
    if not graceplot.GraceIsInstalled:
        usempl = True

    exfiles = _getexamples()
    if isinstance(example, numbers.Integral):
        example = exfiles[example]
        print('-----------------------------------')
        print(example)
    else:
        for ef in exfiles:
            if example in ef:
                example = ef
                break
    examplepath = example

    if usempl:
        if 'grace' in example:
            print('This example is not for mpl.', example)
            return
        with tempfile.NamedTemporaryFile(suffix=".txt", prefix=example, delete=False) as tf:
            with open(examplepath) as f:
                file = f.read()
            newfile = _multiple_replace(file, mplotreplace)
            if platformname == 'Darwin':
                tf.write(newfile.encode())
                tf.flush()
                examplepath = tf.name
                # open is broken but seem to be fixed in newest MACOS versions
                subprocess.call(('open',))
            elif platformname == 'Windows':
                tf.write(newfile.replace('\n', '\r\n').encode())
                tf.flush()
                examplepath = tf.name
                # noinspection PyUnresolvedReferences
                os.startfile(examplepath)
            else:
                tf.write(newfile.encode())
                tf.flush()
                examplepath = tf.name
                subprocess.call(('xdg-open', examplepath))
            tf.close()
            print(examplepath)
    else:
        print(examplepath)
        if platformname == 'Darwin':
            # open is broken but seem to be fixed in newest MACOS versions
            subprocess.call(('open',))
        elif platformname == 'Windows':
            # This should not happen
            pass
        else:
            subprocess.call(('xdg-open', examplepath))


def runAll(start=None, end=None):
    """
    Run all examples ( Maybe needs a bit of time ) .

    Example and saved files go to JscatterExamples/example_name in the current working directory.

    Parameters
    ----------
    start,end : int
        First and last example to run

    """
    exfiles = _getexamples()
    for ff in exfiles[start:end]:
        print('----------------------------------')
        print(os.path.basename(ff))
        runExample(ff)
