import mindscript.ast as ast
from mindscript.objects import MObject, MValue, MFunction, MType
from copy import deepcopy


class TypeError(Exception):
    def __init__(self, message):
        super().__init__(message)

    # def __str__(self):
    #     return super().__str__()



class TypeChecker():

    def __init__(self, ip):
        self.interpreter = ip

    def _checktype_recursion(self, value, target, env):

        # Check if both types are the same primitive type
        if type(target) == ast.TypeTerminal and target.token.literal == "Any":
            return True

        if type(target) == ast.TypeTerminal and target.token.ttype == ast.TokenType.ID:
            name = target.token.literal
            try:
                new_target = env.get(name)
            except KeyError:
                raise TypeError(f"Unknown type '{name}'.")
            if type(new_target) != MType:
                raise TypeError(f"Referencing '{name}', which is not a type.")
            return self._checktype_recursion(value, new_target.definition, new_target.environment)

        if type(value) == MValue:
            v = value.value
            if type(target) == ast.TypeTerminal and target.token.ttype == ast.TokenType.TYPE:
                if v is None and target.token.literal == "Null":
                    return True
                elif type(v) == bool and target.token.literal == "Bool":
                    return True
                elif type(v) == int and target.token.literal == "Int":
                    return True
                elif (type(v) == int or type(v) == float) and target.token.literal == "Num":
                    return True
                elif type(v) == str and target.token.literal == "Str":
                    return True
            elif type(v) == list and type(target) == ast.TypeArray:
                starget = target.expr
                if all(self._checktype_recursion(svalue, starget, env) for svalue in value.value):
                    return True
                return False
            elif type(v) == dict and type(target) == ast.TypeMap:
                required = list(target.required.keys())
                for key in target.map.keys():
                    if key in v:
                        if not self._checktype_recursion(v[key], target.map[key], env):
                            return False
                    elif key not in v and key in required:
                        return False
                    if key in v and key in required:
                        required.remove(key)
                if len(required) > 0:
                    return False
                return True
            elif type(target) == ast.TypeEnum:
                for allowed in target.values.value:
                    if self.interpreter.compare(value, allowed):
                        return True
                return False
            elif type(target) == ast.TypeUnary:
                if v is None:
                    return True
                else:
                    return self._checktype_recursion(value, target.expr, env)
            return False
        elif type(value) == MType and type(target) == ast.TypeTerminal and target.token.literal == "Type":
            return True
        elif isinstance(value, MFunction):
            fdef = value.definition.types
            fenv = value.interpreter.env
            return self._subtype_recursion(t1=fdef, t2=target, env1=fenv, env2=env)
        return False

    def _resolve_type(self, t, env):
        resolving = True
        while resolving:
            if isinstance(t, ast.TypeAnnotation):
                t = t.expr
            elif isinstance(t, ast.TypeGrouping):
                t = t.expr
            elif isinstance(t, ast.TypeTerminal) and t.token.ttype == ast.TokenType.ID:
                key = t.token.literal
                value = env.get(key)
                if type(value) != MType:
                    raise TypeError(
                        f"Referencing '{key}', which is not a type.")
                t = value.definition
                env = value.environment
            else:
                resolving = False
        return [t, env]

    def _subtype_recursion(self, t1, t2, env1, env2, visited=None):
        if visited is None:
            visited = set()

        # Resolve type aliases and annotations.
        [t1, env1] = self._resolve_type(t1, env1)
        [t2, env2] = self._resolve_type(t2, env2)

        # Check for recursion
        if (id(t1), id(t2)) in visited or (id(t2), id(t1)) in visited:
            return True
        visited.add((id(t1), id(t2)))

        type1 = type(t1)
        type2 = type(t2)

        # Check if both types are the same primitive type
        if type2 == ast.TypeTerminal and t2.token.literal == "Any":
            return True

        elif type1 == ast.TypeTerminal and type2 == ast.TypeTerminal:
            if t1.token.literal == t2.token.literal:
                return True

        elif type1 == ast.TypeArray and type2 == ast.TypeArray:
            return self._subtype_recursion(t1.expr, t2.expr, env1, env2, visited)

        elif type1 == ast.TypeMap and type2 == ast.TypeMap:
            if not set(t2.required.keys()).issubset(set(t1.required.keys())):
                return False
            for key in t1.map.keys():
                if key in t2.map.keys() and not self._subtype_recursion(t1.map[key], t2.map[key], env1, env2):
                    return False
            return True

        elif type1 == ast.TypeEnum and type2 != ast.TypeEnum:
            for val in t1.values.value:
                if not self._checktype_recursion(val, t2, env2):
                    return False
            return True
        elif type1 == ast.TypeEnum and type2 == ast.TypeEnum:
            # TODO: Proper comparison of Enums requires comparing their contents,
            # which in the ideal, efficient case would require additional machinery
            # (e.g. recurisve value hashing). We'll brute-force here.
            for val1 in t1.values.value:
                found = False
                for val2 in t2.values.value:
                    if self.interpreter.compare(val1, val2):
                        found = True
                        break
                if not found:
                    return False
            return True

        elif type2 == ast.TypeUnary:
            if type1 == ast.TypeUnary:
                return self._subtype_recursion(t1.expr, t2.expr, env1, env2, visited)
            elif type1 == ast.TypeTerminal and t1.token.literal == "Null":
                return True
            return self._subtype_recursion(t1, t2.expr, env1, env2, visited)

        elif type1 == ast.TypeBinary and type2 == ast.TypeBinary:
            return (self._subtype_recursion(t1.left, t2.left, env1, env2, visited)
                    and self._subtype_recursion(t1.right, t2.right, env1, env2, visited))

        return False

    #
    # UNIFICATION TABLE (lower triangle is the same)
    #
    # |          | Null | Bool  | Int   | Num   | Str   | Any   | Enum[a] | [a]   | {a}   | a?           | Type         | a->b           |
    # |----------|------|-------|-------|-------|-------|-------|---------|-------|-------|--------------|--------------|----------------|
    # |   Null   | Null | Bool? | Int?  | Num?  | Str?  | Any   | *       | [a]?  | {a}?  | a?           | Type?        | (a->b)?        |
    # |   Bool   |   –  | Bool  | Any   | Any   | Any   | Any   | *       | Any   | Any   | Any/(a+Bool)?| Any          | Any            |
    # |   Int    |   –  |   –   | Int   | Num   | Any   | Any   | *       | Any   | Any   | Any/(a+Int)? | Any          | Any            |
    # |   Num    |   –  |   –   |  –    | Num   | Any   | Any   | *       | Any   | Any   | Any/(a+Num)? | Any          | Any            |
    # |   Str    |   –  |   –   |  –    |  –    | Str   | Any   | *       | Any   | Any   | Any/(a+Str)? | Any          | Any            |
    # |   Any    |   –  |   –   |  –    |  –    |  –    | Any   | *       | Any   | Any   | Any          | Any          | Any            |
    # |  Enum[c] |   –  |   –   |  –    |  –    |  –    |  –    | *       | *     | *     | *            | *            | *              |
    # |   [c]    |   –  |   –   |  –    |  –    |  –    |  –    |  –      | [a+b] | Any   | Any/(a+[c])? | Any          | Any            |
    # |   {c}    |   –  |   –   |  –    |  –    |  –    |  –    |  –      |  –    | {a+b} | Any/(a+{c})? | Any          | Any            |
    # |    c?    |   –  |   –   |  –    |  –    |  –    |  –    |  –      |  –    |  –    | Any/(a+c)?   | Any/(a+Type)?| Any/(c+(a->b))?|
    # |   Type   |   –  |   –   |  –    |  –    |  –    |  –    |  –      |  –    |  –    |  –           | Type         | Any            |
    # |   c->d   |   –  |   –   |  –    |  –    |  –    |  –    |  –      |  –    |  –    |  –           | Any          | (a+b)->(c+d)   |
    #
    # *) Enum unification is not handled for now, but it corresponds to the intersection of the elements in the Enum
    #    and the elements of the second type.
    #
    def _unify_recursion(self, t1, t2) -> ast.TypeExpr:

        # We start with the universal types, since they are the easiest to unify.
        if isinstance(t1, ast.TypeTerminal) and t1.token.literal == "Any":
            return t1
        elif isinstance(t2, ast.TypeTerminal) and t2.token.literal == "Any":
            return t2

        # Next we check for Null types, since their handling is simple.
        # There are two special cases: null or nullable. The rest unifies to
        # a nullable type.
        t1_null = False
        t2_null = False
        if isinstance(t1, ast.TypeTerminal) and t1.token.literal == "Null":
            t1_null = True
        if isinstance(t2, ast.TypeTerminal) and t2.token.literal == "Null":
            t2_null = True

        if t1_null and t2_null:
            return t1
        elif t1_null:
            if isinstance(t2, ast.TypeUnary):
                return t2
            return ast.TypeUnary(expr=t2)
        elif t2_null:
            if isinstance(t1, ast.TypeUnary):
                return t1
            return ast.TypeUnary(expr=t1)

        # The remaining primitive types (incl. Type) retain their types if they
        # are equal or promote to Any if different. Exception: Int gets promoted
        # to Num.
        if isinstance(t1, ast.TypeTerminal) and isinstance(t2, ast.TypeTerminal):
            if t1.token.literal == t2.token.literal:
                return t1
            elif t1.token.literal == "Num" and t2.token.literal == "Int":
                return t1
            elif t1.token.literal == "Int" and t2.token.literal == "Num":
                return t2
            return ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Any"))

        # A nullable type a? unifies with b as follows: a? + b = (a+b)?
        # But if (a+b) = Any, then (a+b)? = Any.
        unifier = None
        if isinstance(t1, ast.TypeUnary) and isinstance(t2, ast.TypeUnary):
            unifier = self._unify_recursion(t1.expr, t2.expr)
        elif isinstance(t1, ast.TypeUnary):
            unifier = self._unify_recursion(t1.expr, t2)
        elif isinstance(t2, ast.TypeUnary):
            unifier = self._unify_recursion(t1, t2.expr)
        if unifier:
            if isinstance(unifier, ast.TypeTerminal) and unifier.token.literal == "Any":
                return unifier
            else:
                return ast.TypeUnary(expr=unifier)

        # An array type unification has four cases:
        # 1) [a] + Null = [a]?, which is already covered;
        # 2) [a] + b? = ([a]+b)?, which is covered by the nullable types;
        # 3) [a] + [b] = [a+b];
        # 4) otherwise, [a] + b = Any
        unifier = None
        if isinstance(t1, ast.TypeArray) and isinstance(t2, ast.TypeArray):
            unifier = self._unify_recursion(t1.expr, t2.expr)
            return ast.TypeArray(expr=unifier)
        elif isinstance(t1, ast.TypeArray) or isinstance(t2, ast.TypeArray):
            return ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Any"))

        # Like the array type, an object type unification has four cases:
        # 1) {a} + Null = {a}?, which is already covered;
        # 2) {a} + b? = ({a}+b)?, which is covered by the nullable types;
        # 3) {a} + {b} = {a+b};
        # 4) otherwise, {a} + b = Any
        #
        # Case (3) is the main case. The unification of objects proceeds
        # by unifying all the types pointed by their keys. The required
        # keys are merged.
        unifier = None
        if isinstance(t1, ast.TypeMap) and isinstance(t2, ast.TypeMap):
            unifier = {}
            keys = list(t1.map.keys()) + list(t2.map.keys())
            required = {
                key: True for key in keys if key in t1.required or key in t2.required
            }
            for key in keys:
                if key in t1.map and key in t2.map:
                    unifier[key] = self._unify_recursion(
                        t1.map[key], t2.map[key])
                elif key in t1.map:
                    unifier[key] = t1.map[key]
                elif key in t2.map:
                    unifier[key] = t2.map[key]
            return ast.TypeMap(map=unifier, required=required)
        elif isinstance(t1, ast.TypeMap) or isinstance(t2, ast.TypeMap):
            return ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Any"))

        # Finally, we have function types. A function type resembles a container
        # type, having four unification cases:
        # 1) (a->b) + Null = (a->b)?, which is covered;
        # 2) (a->b) + c? = ((a->b)+c)?, which is covered by the nullably types;
        # 3) (a->b) + (c->d) = (a+b)->(b->d), which is the main case;
        # 4) otherwise, (a->b) + c = Any.
        unifier = None
        if isinstance(t1, ast.TypeBinary) and isinstance(t2, ast.TypeBinary):
            in_unifier = self._unify_recursion(t1.left, t2.left)
            out_unifier = self._unify_recursion(t1.right, t2.right)
            return ast.TypeBinary(left=in_unifier, right=out_unifier, operator=t1.operator)
        elif isinstance(t1, ast.TypeBinary) or isinstance(t2, ast.TypeBinary):
            return ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Any"))

        # If execution makes it until here then it is either an Enum or something
        # bad happened.
        raise TypeError(f"Cannot unify {t1} and {t2}.")

    def _typeof_recursion(self, value) -> ast.TypeExpr:
        valtype = None
        if isinstance(value, MValue):
            v = value.value
            if v is None:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Null"))
            elif type(v) == bool:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Bool"))
            elif type(v) == str:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Str"))
            elif type(v) == int:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Int"))
            elif type(v) == float:
                valtype = ast.TypeTerminal(token=ast.Token(
                    ttype=ast.TokenType.TYPE, literal="Num"))
            elif type(v) == list:
                # Traverse the list and unify.
                if len(v) == 0:
                    valtype = ast.TypeArray(
                        expr=ast.TypeTerminal(token=ast.Token(
                            ttype=ast.TokenType.TYPE, literal="Any")))
                else:
                    unifier = None
                    for item in v:
                        if unifier is None:
                            unifier = self._typeof_recursion(item)
                        else:
                            kind = self._typeof_recursion(item)
                            unifier = self._unify_recursion(unifier, kind)
                    valtype = ast.TypeArray(expr=unifier)
            elif type(v) == dict:
                items = {}
                for key, item in v.items():
                    subtype = self._typeof_recursion(item)
                    items[key] = subtype
                else:
                    valtype = ast.TypeMap(map=items, required={})
        elif isinstance(value, MFunction):
            valtype = value.definition.types
        elif isinstance(value, MType):
            valtype = ast.TypeTerminal(token=ast.Token(
                ttype=ast.TokenType.TYPE, literal="Type"))
        else:
            "print_value: Unknown value type!"
        return valtype

    def typeof(self, value: MObject) -> ast.TypeExpr:
        return self._typeof_recursion(value)

    def checktype(self, value: MObject, target: MType) -> bool:
        if type(target) != MType:
            return False
        return self._checktype_recursion(value, target.definition, target.environment)

    def issubtype(self, subtype: MObject, supertype: MObject) -> bool:
        if type(subtype) != MType or type(supertype) != MType:
            return False
        t1 = subtype.definition
        env1 = subtype.environment
        t2 = supertype.definition
        env2 = supertype.environment
        return self._subtype_recursion(t1=t1, t2=t2, env1=env1, env2=env2)
