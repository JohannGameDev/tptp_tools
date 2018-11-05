import json
import sys
import os
import pathlib
from antlr4 import *
if __name__ == '__main__':
    from tptp2tex.tLexer import tLexer
    from tptp2tex.tListener import tListener
    from tptp2tex.tParser import tParser
else :
    from .tptp2tex.tLexer import tLexer
    from .tptp2tex.tListener import tListener
    from .tptp2tex.tParser import tParser
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
        dir_root = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
        filename = dir_root.joinpath("tptp2tex","tptp_2_latex.json")
        with open(filename) as f:  # tptp_2_latex: represent tptp in latex(e.g. ! is \forall)
            data = json.load(f)
        self.tptp_2_latex = data
        filename = dir_root.joinpath("tptp2tex","template.tex")
        with open(filename, 'r') as latex_template:
            data = latex_template.read()
        self.latex_template = data
#        self.styling = kwargs.get(0,None)
        self.item_header = {"name":"","formula_role":"","fof_formula":""}# will be displayed as item header
        self.styling = {"functor":"red","fof_formula":"blue"}
        self.delete = {"name","formula_role"}
        self.texcommands = {"red":"\\tptpred{", "blue":"\\tptpblue{"}# TODO: latex commands in json
        self.styling_type = kwargs.get(1,None)
        self.current_raw_latex = LatexRaw(self.styling, self.tptp_2_latex)  # Current raw latex code from tptp-input
        self.styled_latex = ""

    """for current tptp_input create a raw_latex objects that holds info about latex code from tree"""
    def enterTptp_input(self, ctx:tParser.Tptp_inputContext):
        self.styled_latex = self.styled_latex + "\n"
        self.current_raw_latex = LatexRaw(self.styling, self.tptp_2_latex)
        self.current_raw_latex.add_tptp_og_input(ctx.getText())
        self.current_raw_latex.add_tex(self.match_style(ctx))  # This is the point where the Tree will be parsed into Latex
        self.current_raw_latex.add_name(self.item_header["name"])
        self.current_raw_latex.add_formula_role(self.item_header["formula_role"])
        self.current_raw_latex.add_tptp_og_formula(self.item_header["fof_formula"])
        self.latex_raw.append(self.current_raw_latex) # collect all raw_latex to create a latex file from template

    """This function is to determine whether it should be parsed with default latex conversion or custom latex commands
    """
    def decide_match(self,ctx):
        custom_tag = ["thf_variable_list"] # TODO:Custom tag seperate json
        if tParser.ruleNames[ctx.getRuleIndex()] in custom_tag:
            need = []
            for child in ctx.getChildren():
                need.append(self.match_custom(child))
            custom_tex = ""
            for n in need:
                custom_tex += " {variable}_{{{atomic_defined_word}{atomic_word}}} ".\
                        format(variable=n.get("variable"),atomic_defined_word=n.get("atomic_defined_word"),atomic_word=n.get("atomic_word")) # TODO: This string in json
        else:
            custom_tex = self.match_style(ctx)

        return custom_tex


    """This function is for parsing the tree into latex with styling and replacement."""
    def match_style(self,ctx):
        ret = ""
        if isinstance(ctx,TerminalNode):
            terminal_latex = self.getLatexCommand(ctx.getText())
            return terminal_latex
        else:
            for child in ctx.getChildren():
                if isinstance(child,TerminalNode):
                    ret += self.match_style(child)
                else:

                    if tParser.ruleNames[child.getRuleIndex()] in self.item_header: # This rules are parsed to be a header
                        self.item_header[tParser.ruleNames[child.getRuleIndex()]] = child.getText() # fill in dictionary with predefined header
                    if tParser.ruleNames[child.getRuleIndex()] in self.styling: # Here are the rules that get a sorunding tex-tag
                        color = self.styling.get(tParser.ruleNames[child.getRuleIndex()]) # what if it has to be styled and is a custom_tag
                        ret += self.texcommands.get(color) + self.decide_match(child) + "}"
                    else:
                        ret += self.decide_match(child)
                    if tParser.ruleNames[child.getRuleIndex()] in self.delete:
                        ret = ""  # just do nothing with it further if its in delete

        return ret

    """
    # \lambda A_{ab}, B_{ab}, X_{a} . ( ( A \; X ) \lor (B \; X) )
        # for every thf_variable get variable(e.g. A) and thf_mapping type get text of children ignore > will be as indize
    """
    def match_custom(self, ctx, custom_parse_data=None):
        custom_parse = ["variable","atomic_defined_word","atomic_word"] # TODO: JSON

        if custom_parse_data is None: # http://blog.thedigitalcatonline.com/blog/2015/02/11/default-arguments-in-python/ end of article
            custom_parse_data = {"variable": "", "atomic_defined_word": "","atomic_word":""}# TODO: JSON

        if isinstance(ctx, TerminalNode):
            # Maybe for future development
            pass
        else:
            for child in ctx.getChildren():
                if isinstance(child, TerminalNode):
                    # Maybe for future development
                    pass
                else:
                    if tParser.ruleNames[child.getRuleIndex()] in custom_parse:
                        custom_parse_data[tParser.ruleNames[child.getRuleIndex()]] += self.getLatexCommand(child.getText()) # append indizes
                        self.match_custom(child, custom_parse_data)
                    else:
                        self.match_custom(child, custom_parse_data)
        return custom_parse_data


    def getLatexCommand(self,text):
        for k in sorted(self.tptp_2_latex.keys(), key=len, reverse=True):  # longest keywords will be matched first
            text = text.replace(k, self.tptp_2_latex.get(k) + " ")
        return text

    def enterName(self, ctx: tParser.NameContext):
        self.current_raw_latex.add_name(ctx.getText())

    def enterFormula_role(self, ctx: tParser.Formula_roleContext):
        self.current_raw_latex.add_formula_role(ctx.getText())

    def enterFof_formula(self, ctx: tParser.Fof_formulaContext):
        self.current_raw_latex.add_tptp_og_formula(ctx.getText())
        self.latex_raw.append(self.current_raw_latex)

    def create_latex_from_raw(self):
        latex = "\\begin{enumerate} \n"
        for raw_latex in self.latex_raw:
            latex = latex + raw_latex.create_raw_latex() + "\n"
        latex = latex + "\\end{enumerate} \n"

        return latex


    def create_latex_file(self,latex_raw):
        #print("creating latex file from template....")
        latex = self.latex_template.replace("___tptp_latex___",latex_raw)
        with open('tptp.tex', 'w') as latex_template:
            latex_template.write(latex)
        return latex


"""LatexRaw contains information about one tptp_input and creates latex from it."""
class LatexRaw:

    def __init__(self, latex_styling, tptp_2_latex):
        self.tptp_2_latex = tptp_2_latex
        self.latex_styling = latex_styling
        self.tptp_input_name = ""
        self.tptp_formula_role = ""
        self.tptp_og_input = ""
        self.tptp_og_formula = ""
        self.tex = ""



    def add_name(self, tptp_input_name):
        self.tptp_input_name = tptp_input_name

    def add_formula_role(self, tptp_formula_role):
        self.tptp_formula_role = tptp_formula_role

    def add_tptp_og_input(self, tptp_og_input):  # og stands for original
        self.tptp_og_input = tptp_og_input

    def add_tptp_og_formula(self,tptp_og_formula):
        self.tptp_og_formula = tptp_og_formula

    def add_tex(self,tex):
        self.tex = tex

    def create_raw_latex(self):
        raw_latex = "\\item {my_name} {my_role} \n".format(my_name=self.tptp_input_name, my_role=self.tptp_formula_role)
        raw_latex = raw_latex.replace("_","\_") # display underscore in latex
        raw_latex = raw_latex + "\\begin{flalign*} \n"
        raw_latex = raw_latex + self.tex + "\n"
        raw_latex = raw_latex + "\\end{flalign*} \n"
        tptp_latex_style = "\\begin{Verbatim}[fontsize=\\tptpfontsize]\n" + self.tptp_og_input + "\n\\end{Verbatim}"
        raw_latex = raw_latex + tptp_latex_style + "\n"

        return raw_latex

def create_latex_file(content_string):
    lexer = tLexer(InputStream(content_string))
    stream = CommonTokenStream(lexer)
    parser = tParser(stream)
    tree = parser.tptp_file()
    printer = TptpListener() # <- Custom-Listener
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    latex_raw = printer.create_latex_from_raw()
    latex = printer.create_latex_file(latex_raw)
    return latex

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
    latex = printer.create_latex_file(latex_raw)
    print(latex)
    #pyperclip.copy(latex) # for debugging

if __name__ == '__main__':
    main(sys.argv)
