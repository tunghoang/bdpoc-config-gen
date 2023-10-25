# Generated from Logic.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,13,31,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,0,1,0,5,0,11,8,0,10,
        0,12,0,14,9,0,1,1,1,1,1,2,1,2,1,2,1,2,1,2,1,2,1,2,1,2,5,2,26,8,2,
        10,2,12,2,29,9,2,1,2,0,1,4,3,0,2,4,0,1,2,0,1,1,7,9,29,0,12,1,0,0,
        0,2,15,1,0,0,0,4,17,1,0,0,0,6,7,5,11,0,0,7,8,3,4,2,0,8,9,5,13,0,
        0,9,11,1,0,0,0,10,6,1,0,0,0,11,14,1,0,0,0,12,10,1,0,0,0,12,13,1,
        0,0,0,13,1,1,0,0,0,14,12,1,0,0,0,15,16,7,0,0,0,16,3,1,0,0,0,17,18,
        6,2,-1,0,18,19,3,2,1,0,19,20,5,4,0,0,20,21,3,2,1,0,21,27,1,0,0,0,
        22,23,10,1,0,0,23,24,5,5,0,0,24,26,3,4,2,2,25,22,1,0,0,0,26,29,1,
        0,0,0,27,25,1,0,0,0,27,28,1,0,0,0,28,5,1,0,0,0,29,27,1,0,0,0,2,12,
        27
    ]

class LogicParser ( Parser ):

    grammarFileName = "Logic.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "'d('", "')'", "<INVALID>", 
                     "' AND '", "'last('", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "' : '" ]

    symbolicNames = [ "<INVALID>", "DERIVATIVE", "DERIVATIVE_START", "BLOCK_END", 
                      "COMP", "LOGIC", "LAST_START", "LAST", "TAG", "NUMBER", 
                      "DIGIT", "RULENUMBER", "COLON", "NEWLINE" ]

    RULE_prog = 0
    RULE_expr = 1
    RULE_condition = 2

    ruleNames =  [ "prog", "expr", "condition" ]

    EOF = Token.EOF
    DERIVATIVE=1
    DERIVATIVE_START=2
    BLOCK_END=3
    COMP=4
    LOGIC=5
    LAST_START=6
    LAST=7
    TAG=8
    NUMBER=9
    DIGIT=10
    RULENUMBER=11
    COLON=12
    NEWLINE=13

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RULENUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(LogicParser.RULENUMBER)
            else:
                return self.getToken(LogicParser.RULENUMBER, i)

        def condition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LogicParser.ConditionContext)
            else:
                return self.getTypedRuleContext(LogicParser.ConditionContext,i)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(LogicParser.NEWLINE)
            else:
                return self.getToken(LogicParser.NEWLINE, i)

        def getRuleIndex(self):
            return LogicParser.RULE_prog

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProg" ):
                listener.enterProg(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProg" ):
                listener.exitProg(self)




    def prog(self):

        localctx = LogicParser.ProgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_prog)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 12
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==11:
                self.state = 6
                self.match(LogicParser.RULENUMBER)
                self.state = 7
                self.condition(0)
                self.state = 8
                self.match(LogicParser.NEWLINE)
                self.state = 14
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TAG(self):
            return self.getToken(LogicParser.TAG, 0)

        def LAST(self):
            return self.getToken(LogicParser.LAST, 0)

        def DERIVATIVE(self):
            return self.getToken(LogicParser.DERIVATIVE, 0)

        def NUMBER(self):
            return self.getToken(LogicParser.NUMBER, 0)

        def getRuleIndex(self):
            return LogicParser.RULE_expr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr" ):
                listener.enterExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr" ):
                listener.exitExpr(self)




    def expr(self):

        localctx = LogicParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_expr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 898) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LogicParser.ExprContext)
            else:
                return self.getTypedRuleContext(LogicParser.ExprContext,i)


        def COMP(self):
            return self.getToken(LogicParser.COMP, 0)

        def condition(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LogicParser.ConditionContext)
            else:
                return self.getTypedRuleContext(LogicParser.ConditionContext,i)


        def LOGIC(self):
            return self.getToken(LogicParser.LOGIC, 0)

        def getRuleIndex(self):
            return LogicParser.RULE_condition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCondition" ):
                listener.enterCondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCondition" ):
                listener.exitCondition(self)



    def condition(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = LogicParser.ConditionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 4
        self.enterRecursionRule(localctx, 4, self.RULE_condition, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 18
            self.expr()
            self.state = 19
            self.match(LogicParser.COMP)
            self.state = 20
            self.expr()
            self._ctx.stop = self._input.LT(-1)
            self.state = 27
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = LogicParser.ConditionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_condition)
                    self.state = 22
                    if not self.precpred(self._ctx, 1):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                    self.state = 23
                    self.match(LogicParser.LOGIC)
                    self.state = 24
                    self.condition(2) 
                self.state = 29
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[2] = self.condition_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def condition_sempred(self, localctx:ConditionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 1)
         




