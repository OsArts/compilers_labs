# Import graphviz
import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv

# Import pygraph
from pygraph.classes.digraph import digraph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write


class FA:
    EMPTY = 'empty'
    
    def __init__(self, transition_table, initial_state, final_state):
        self.transition_table = transition_table
        self.initial_state = initial_state
        self.final_state = final_state  

    def draw(self, filename):
        print "transition table:", self.transition_table 
        gr = digraph()
        vertexes = self.transition_table.keys()
        gr.add_nodes([str(vertex) for vertex in vertexes])
        for initial_vertex in vertexes:
            transitions = self.transition_table[initial_vertex]
            for label in transitions.keys():
                final_vertexes = transitions.get(label, None)
                for final_vertex in final_vertexes:
                    gr.add_edge(edge=(str(initial_vertex), str(final_vertex)), label=label)
        dot = write(gr)
        gvv = gv.readstring(dot)
        gv.layout(gvv, 'dot')
        gv.render(gvv, 'png', '%s.png' % filename)


class WrongExpressionError(Exception):
    pass


class TompsonAlgorithm:
    GROUP_START = '('
    GROUP_END = ')'
    ITERATION = '*'
    OR = '|'
    SPECIAL_SYMBOLS = [GROUP_START, GROUP_END, ITERATION, OR]
   
    def __init__(self, regexp):
        self.regexp = regexp
        self.alphabet = self.get_alphabet()
        self.last_vertex = 0
    
    def get_alphabet(self):
        return set(self.regexp) - set(self.SPECIAL_SYMBOLS)

    def buildNFA(self):
        return self._buildNFA(self.regexp)
        
    def _buildNFA(self, regexp):
        stack = []
        idx = 0
        while idx < len(regexp):
            ch = regexp[idx]
            if ch == '(':
                group, idx = self._select_group(regexp, idx)
                stack.append(self._buildNFA(group))
            elif ch == '*':
                stack.append(self._iterationNFA(stack.pop()))
            elif ch == '|':
                left_fa = self._concatenateNFAlist(stack)
                right_fa = self._buildNFA(regexp[idx + 1:])
                return self._orNFA(left_fa, right_fa)
            else:
                stack.append(self._symbolNFA(ch))
            idx += 1
        return self._concatenateNFAlist(stack)            

    def _select_group(self, regexp, sidx):
        level = 0
        idx = sidx + 1
        group = ''
        while idx < len(regexp):
            ch = regexp[idx]
            if ch == ')':
                if level == 0:
                    return group, idx
                level -= 1
            elif ch == '(':
                level += 1
            group += ch
            idx += 1
        raise WrongExpressionError()
            
    def _iterationNFA(self, fa):
        initial_state = self.last_vertex
        final_state = self.last_vertex + 1
        
        transition_table = fa.transition_table
        transition_table[initial_state] = {
            FA.EMPTY: [fa.initial_state, final_state]
        }
        transition_table[fa.final_state] = {
            FA.EMPTY: [fa.initial_state, final_state]
        }
        transition_table[final_state] = {
            FA.EMPTY: []
        }

        self.last_vertex += 2
        return FA(transition_table, initial_state, final_state)

    def _concatenateNFAlist(self, fa_list):
        right_fa = fa_list.pop()
        while fa_list:
            left_fa = fa_list.pop()
            right_fa = self._concatenateNFA(left_fa, right_fa)
        return right_fa        

    def _concatenateNFA(self, fa1, fa2):
        initial_state = fa1.initial_state
        final_state = fa2.final_state

        transition_table = fa1.transition_table
        transition_table.update(fa2.transition_table)
        transition_table[fa1.final_state] = {
            FA.EMPTY: [fa2.initial_state]
        }

        return FA(transition_table, initial_state, final_state)      

    def _orNFA(self, fa1, fa2):
        initial_state = self.last_vertex
        final_state = self.last_vertex + 1

        transition_table = fa1.transition_table
        transition_table.update(fa2.transition_table)
        transition_table.update({
            initial_state: {
                FA.EMPTY: [fa1.initial_state, fa2.initial_state]
            },
            fa1.final_state: {
                FA.EMPTY: [final_state]
            },
            fa2.final_state: {
                FA.EMPTY: [final_state]
            },
            final_state: {},
        })

        self.last_vertex += 2        
        return FA(transition_table, initial_state, final_state)        
              
    def _symbolNFA(self, symbol):
        initial_state = self.last_vertex
        final_state = self.last_vertex + 1

        transition_table = {
            initial_state: {
                symbol: [final_state]
            },
            final_state: {}
        }

        self.last_vertex += 2
        return FA(transition_table, initial_state, final_state)
     
        
#regexp = "a(a(aa|b)*a)b*aa"
#regexp = "a*"
#regexp = "(ab)*"
#regexp = "aa|bb"
#regexp = "a(a|b)*b"
regexp = "aaabbb"
algorithm = TompsonAlgorithm(regexp)
fa = algorithm.buildNFA()
fa.draw('graph')

