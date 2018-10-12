import json
import sys
from antlr4 import *
from tptp2tex.tLexer import tLexer
from tptp2tex.tListener import tListener
from tptp2tex.tParser import tParser
import pyperclip # copy to clipboard(ctrl-c) can be pasted with ctrl-v

"""
This module is intended for parsing the tptp input to latex and creating a tptp.tex 
"""

"""
TptpListener listens on rules and will be fired during the walkthrough of the parsed tree.
In addition to that it creates the latex file.
"""
class TptpListener(tListener):

    def __init__(self,**kwargs):
        # a tptp-file consists of one or more tptp-inputs (e.g. different axioms)
        self.latex_raw = []  # Contains all different tptp-inputs as raw latex
        with open('tptp2tex/tptp_2_latex.json') as f:  # tptp_2_latex: represent tptp in latex(e.g. ! is \forall)
            data = json.load(f)
        self.tptp_2_latex = data
        with open('tptp2tex/template.tex', 'r') as latex_template:
            data = latex_template.read()
        self.latex_template = data
        self.styling = kwargs.get(0,None)
        self.styling_type = kwargs.get(1,None)
        self.current_raw_latex = LatexRaw(self.styling, self.tptp_2_latex)  # Current raw latex code from tptp-input

    def enterTptp_input(self, ctx:tParser.Tptp_inputContext):
        print("tptp input(tptp_input): %s" % ctx.getText())
        self.current_raw_latex = LatexRaw(self.styling, self.tptp_2_latex)
        self.current_raw_latex.add_tptp_og_input(ctx.getText())

    def enterName(self, ctx: tParser.NameContext):
        print("Atomic_Word (tptp_input-Name): %s" % ctx.getText())
        self.current_raw_latex.add_name(ctx.getText())

    def enterFormula_role(self, ctx: tParser.Formula_roleContext):
        print("Formula_role: %s" % ctx.getText())
        self.current_raw_latex.add_formula_role(ctx.getText())

    def enterFof_formula(self, ctx: tParser.Fof_formulaContext):
        print("fof_formula: %s" % ctx.getText())
        self.current_raw_latex.add_tptp_og_formula(ctx.getText())
        self.latex_raw.append(self.current_raw_latex)

    def create_latex_from_raw(self):
        latex = "\\begin{enumerate} \n"
        for raw_latex in self.latex_raw:
            latex = latex + raw_latex.create_raw_latex() + "\n"
        latex = latex + "\\end{enumerate} \n"

        return latex

    def create_latex_file(self,latex_raw):
        print("creating latex file from template....")
        latex = self.latex_template.replace("___tptp_latex___",latex_raw)
        with open('tptp.tex', 'w') as latex_template:
            latex_template.write(latex)


"""LatexRaw contains information about one tptp_input and creates latex from it."""
class LatexRaw:

    def __init__(self, latex_styling, tptp_2_latex):
        self.tptp_2_latex = tptp_2_latex
        self.latex_styling = latex_styling
        self.tptp_input_name = ""
        self.tptp_formula_role = ""
        self.tptp_og_input = ""
        self.tptp_og_formula = ""



    def add_name(self, tptp_input_name):
        self.tptp_input_name = tptp_input_name

    def add_formula_role(self, tptp_formula_role):
        self.tptp_formula_role = tptp_formula_role

    def add_tptp_og_input(self, tptp_og_input):  # og stands for original
        self.tptp_og_input = tptp_og_input

    def add_tptp_og_formula(self,tptp_og_formula):
        self.tptp_og_formula = tptp_og_formula

    def create_raw_latex(self):
        raw_latex = "\\item {my_name} {my_role} \n".format(my_name=self.tptp_input_name, my_role=self.tptp_formula_role)
        raw_latex = raw_latex.replace("_","\_") # display underscore in latex
        raw_latex = raw_latex + "\\begin{flalign*} \n"
        tempFormula = self.tptp_og_formula # tempformula will be parsed from tptp to latex(math)
        for k in sorted(self.tptp_2_latex.keys(), key=len, reverse=True): # longest keywords will be matched first
            tempFormula = tempFormula.replace(k, self.tptp_2_latex.get(k)+" ")
        raw_latex = raw_latex + tempFormula + "\n"
        raw_latex = raw_latex + "\\end{flalign*} \n"
        tptp_latex_style = "\\begin{Verbatim}[fontsize=\\tptpfontsize]\n" + self.tptp_og_input + "\n\\end{Verbatim}"
        raw_latex = raw_latex + tptp_latex_style + "\n"

        return raw_latex

def main(argv):
    input = FileStream(argv[1])
    lexer = tLexer(input)
    stream = CommonTokenStream(lexer)
    parser = tParser(stream)
    tree = parser.tptp_file()
    printer = TptpListener() # <- Custom-Listener

    walker = ParseTreeWalker()

    walker.walk(printer, tree)

    latex_raw = printer.create_latex_from_raw()
#    pyperclip.copy(latex_raw) for debugging
    printer.create_latex_file(latex_raw)


if __name__ == '__main__':
    main(sys.argv)
