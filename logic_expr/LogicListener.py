# Generated from Logic.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .LogicParser import LogicParser
else:
    from LogicParser import LogicParser

# This class defines a complete listener for a parse tree produced by LogicParser.
class LogicListener(ParseTreeListener):

    # Enter a parse tree produced by LogicParser#prog.
    def enterProg(self, ctx:LogicParser.ProgContext):
        pass

    # Exit a parse tree produced by LogicParser#prog.
    def exitProg(self, ctx:LogicParser.ProgContext):
        pass


    # Enter a parse tree produced by LogicParser#expr.
    def enterExpr(self, ctx:LogicParser.ExprContext):
        pass

    # Exit a parse tree produced by LogicParser#expr.
    def exitExpr(self, ctx:LogicParser.ExprContext):
        pass


    # Enter a parse tree produced by LogicParser#condition.
    def enterCondition(self, ctx:LogicParser.ConditionContext):
        pass

    # Exit a parse tree produced by LogicParser#condition.
    def exitCondition(self, ctx:LogicParser.ConditionContext):
        pass



del LogicParser