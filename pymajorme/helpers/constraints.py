
class Constraints(object):
    ''' Contains all of the primary and foreign key constraint
        names for the given entity as tuples of entities and
        relations which are part of constraints '''

    def __init__(self, pk_constraints, fk_constraints):
        self.pk_constraints = pk_constraints
        self.fk_constraints = fk_constraints

