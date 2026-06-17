import cvc5
from cvc5 import Kind

class Modulo_FF:
    def __init__(self, ast, API, terms, primes, utility):
        self.ast = ast
        self.API = API
        self.terms = terms
        self.primes = primes
        self.utility = utility
    
    def compute_mod(self):
        # Reset ff dictionaires for current prime
        self.terms.ff_mod_vars.clear()
        self.terms.ff_elems.clear()

        # Create Finite Field sort for current prime
        self.primes.ff_sort = self.API.tm.mkFiniteFieldSort(str(self.primes.prime))

        self.create_ff_mod_constants()
        self.process_ff_mod()

    def create_ff_mod_constants(self):
        for  name in self.terms.vars:
            # Create constant and add to dictionary
            mod_name = f"{name}_mod_{self.primes.prime}"
            mod_const = self.API.tm.mkConst(self.primes.ff_sort, mod_name)
            self.terms.ff_mod_vars[mod_name] = mod_const
            
    def process_ff_mod(self):
        # assertions are not reset - new modulo p assertions added each time
        for subtree in self.ast:
            # Process each assert command within context of modulo prime
            if subtree[0] == "assert":
                constraint = self.process_ff_mod_constraint(subtree[1])
                self.API.mod_solver.assertFormula(constraint)
    
    def process_ff_mod_constraint(self, subtree):
        # leaf node = string
        # subtree = list
        if (isinstance(subtree, str)):
            if subtree in self.terms.vars:
                return self.utility.handle_ff_const(subtree) # return FF constant
            else:
                return self.utility.handle_ff_element(subtree) # return FF element
        else:
            # call process_ff_mod_constraint  for all operands (depth-first traversal)
            operator = subtree[0]
            operands = [self.process_ff_mod_constraint (operand) for operand in subtree[1:]]

            ## FF substraction case (rewrite x - y to x + ff.neg(y))
            if operator == "-":
                neg = self.API.mod_solver.mkTerm(Kind.FINITE_FIELD_NEG, operands[1])
                return self.API.mod_solver.mkTerm(Kind.FINITE_FIELD_ADD, operands[0], neg)
            return self.utility.create_ff_mod_term(operator, operands)