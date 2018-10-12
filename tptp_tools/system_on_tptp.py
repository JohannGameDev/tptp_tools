from lxml import html 
import requests
import re
"""
This module is intended for parsing the tptp_tools website an retrieve information 
about the problem solvers and theorem finders.
Further the module provides a function, which starts those system on the 
website with a local problem and chosen parameters.
"""

""" Returns a list [(systemname, format, default commands, (understood tptp_tools language dialects)) """
def getSolvers():
    website = requests.get('http://www.tptp.org/cgi-bin/SystemOnTPTP')
    tree = html.fromstring(website.text)
    lsOfElements = tree.xpath('//input')

    solverNames = []
    solverFormats = []
    solverCommands = []
    solverApplications = []

    for elem in lsOfElements:
        if elem.name.startswith('System___'):
            solverNames.append((elem.xpath('@value'))[0])
        if elem.name.startswith('Format___'):
            solverFormats.append((elem.xpath('@value'))[0])
        if elem.name.startswith('Command___'):
            solverCommands.append((elem.xpath('@value'))[0])
        else:
            continue

    solverApplications = tree.xpath('//font[@size="-1"]/text()')
    for i in range(len(solverApplications)):
        solverApplications[i] = re.search('(?:([\w ]+), )?for ([\w ]+)',solverApplications[i] ,re.I).group(2).split()

    solvers = list(zip(solverNames, solverFormats, solverCommands, solverApplications))

    return(solvers)


""" provername is a string equivalent to one of those in the first element
of the 4-tuple of an element in the list of getSolvers """
""" parameters requires the command given to the corresponding solver like
the ones in the third element of the 4-tuple of the list returned by 
getSolvers """
""" problem is a path to a problem file """
""" time is max time-out in seconds, default is 60"""
def request(provername, parameters, problem, time):
    provers = getSolvers()
    for i in range(len(provers)):
        if provername in provers[i][0]:
            solver = provers[i]
    

    payload={'TPTPProblem':'',
            'ProblemSource':'FORMULAE',
            'FORMULAEProblem':problem,
            'QuietFlag':'-q01', #for output mode System
            #'QuietFlag':'-q3', #for output mode Result
            'SubmitButton':'RunSelectedSystems',
            }
    payload.update({'System___'+provername:provername, 'TimeLimit___'+provername:time, 'Command___'+provername:parameters})

    response = requests.post("http://www.tptp.org/cgi-bin/SystemOnTPTPFormReply", data=payload)

    results = re.findall('^% RESULT:.*', response.text,re.M )
    if results == []:
        return("Error on SystemonTPTP-Website")
    stat = re.search('(?:.*says )(.*)(?: - CPU.*)', results[0],  re.I).group(1)
    cpu = float(re.search('(?:.*CPU = )(.*)(?: WC.*)', results[0],  re.I).group(1))
    wc = float(re.search('(?:.*WC = )(\S*)(?: .*)', results[0],  re.I).group(1))
    return({stat:(cpu, wc, response.text)})

'''
testprob = "fof(pel24_1,axiom,\
            ( ~ ( ? [X] :\
            ( big_s(X)\
            & big_q(X) ) ) )).\
        \
        fof(pel24_2,axiom,\
            ( ! [X] :\
            ( big_p(X)\
            => ( big_q(X)\
            | big_r(X) ) ) )).\
        \
        fof(pel24_3,axiom,\
            ( ~ ( ? [X] : big_p(X) )\
            => ? [Y] : big_q(Y) )).\
        \
        fof(pel24_4,axiom,\
            ( ! [X] :\
            ( ( big_q(X)\
            | big_r(X) )\
            => big_s(X) ) )).\
        \
        fof(pel24,conjecture,\
            ( ? [X] :\
            ( big_p(X)\
            & big_r(X) ) )).\
        \
        "

print(getSolvers())
print('\n\n')
bsp = getSolvers()[1]
print(request(bsp[0], bsp[2], testprob, 60))
#'''


import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("function", help="give function name: getSolvers or request")
    parser.add_argument("--solvername", help="solver if request function is chosen")
    parser.add_argument("--parameters", help="parameters of the chosen solver, if request function is chosen")
    parser.add_argument("--problem", help="path to problem file, if request function is chosen")
    parser.add_argument("--time", help="time-out if request function is chosen (default is 60)")
    args = parser.parse_args()
    return(args)

def main():
    args = parse_args()
    if args.function == 'getSolvers':
        print(getSolvers())
    if args.function == 'request':
        probfile = open(args.problem, 'r')
        prob = probfile.read()
        print(request(args.solvername, args.parameters, prob, args.time))

if __name__ == "__main__":
    main()


