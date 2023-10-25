from antlr4 import *
from .LogicLexer import LogicLexer
from .LogicParser import LogicParser
from .LogicListener import LogicListener

def isComparison(token) :
    return token in ('<', '>', '<=', '>=', '==', '!=')

def isTerminal(node):
    return node.__class__.__name__.startswith('TerminalNode')

def isCondition(node):
    return node.__class__.__name__ == 'ConditionContext'

def isExpr(node):
    return node.__class__.__name__ == 'ExprContext'

def handle(expr, df=None, df1=None):
    if type(expr) in (int, float):
        value = expr
        return (f'{expr}', value)

    if expr.startswith('d('):
        tag = expr.replace('d(', '').replace(')', '')
        tag_df = df[df._field == tag]
        if tag_df.empty:
            print(f'\tWARNING: Expr={expr}=No data')
            value = 0.0
            return (f'{expr}', value)
        tag_df = tag_df.tail(2)
        if tag_df.shape[0] < 2:
            print(f'\tWARNING: Expr={expr}=insufficient data')
            value = 0.0
            return (f'{expr}', value)
        value = tag_df.iloc[1]['_value'] - tag_df.iloc[0]['_value']
        return (f'{expr}', value)

    if expr.startswith('last('):
        tag = expr.replace('last(', '').replace(')', '')
        tag_df = df1[df1._field == tag]
        if tag_df.empty:
            print(f'\tWARNING: Expr={expr}=No data')
            value = None
            return (f'{expr}', value)
        value = tag_df.tail(1).iloc[0]['_value']
        return (f'{expr}', value)
    else:
        tag = expr
        tag_df = df[df._field == tag]
        if tag_df.empty:
            print(f'\tWARNING: Expr={expr}=No data')
            value = None
            return (f'{expr}', value)
        value = tag_df['_value'].mean()
        return (f'{expr}', value)

def evaluate(stack, df=None, df1=None):
    if df is None and df1 is None:
        return stack
    operands = []
    print("\tDEBUG: ", stack)
    while(len(stack) > 0):
        last = stack.pop()
        if not isComparison(last):
            operands.append(handle(last, df=df, df1=df1))
        else:
            print(f"DEBUG -> {operands[1][0]} ({operands[1][1]}) {last} {operands[0][0]} ({operands[0][1]})")
            if operands[0][1] is None or operands[1][1] is None:
                return True
          
            if last == '<':
                if not operands[1][1] < operands[0][1]:
                    return False
                else:
                    operands.clear()
            elif last == '<=':
                if not operands[1][1] <= operands[0][1]:
                    return False
                else:
                    operands.clear()
            elif last == '>':
                if not operands[1][1] > operands[0][1]:
                    print(operands[1], '>' , operands[0])
                    return False
                else:
                    operands.clear()
            elif last == '>=':
                if not operands[1][1] >= operands[0][1]:
                    return False
                else:
                    operands.clear()
            elif last == '==':
                if not operands[1][1] == operands[0][1]:
                    return False
                else:
                    operands.clear()
            elif last == '!=':
                if not operands[1][1] != operands[0][1]:
                    return False
                else:
                    operands.clear()
    return True

def handleTag(exprCtx):
    return exprCtx.getText()

def handleDerivative(exprCtx):
    return exprCtx.getText()

def handleLast(exprCtx):
    return exprCtx.getText()

def handleExpr(exprCtx, stack):
    if exprCtx.DERIVATIVE():
        stack.append(handleDerivative(exprCtx))
    elif exprCtx.TAG():
        stack.append(handleTag(exprCtx))
    elif exprCtx.LAST():
        stack.append(handleLast(exprCtx))
    else:
        stack.append(float(exprCtx.getText()))

def handleCondition(conditionCtx, stack):
    if conditionCtx.LOGIC():
        for c in conditionCtx.getChildren():
            if isCondition(c):
                handleCondition(c, stack)
    else:
        stack.append(str(conditionCtx.COMP()).strip())
        for c in conditionCtx.getChildren():
            if isExpr(c):
                handleExpr(c, stack)

def handleRootCondition(conditionCtx, df=None, df1=None):
    stack = []
    handleCondition(conditionCtx, stack)
    return evaluate(stack, df=df, df1=df1)

def detect(df, df1, rule_file='input.rules'):
    code = open(rule_file, 'r').read()
    codeStream = InputStream(code)
    lexer = LogicLexer(codeStream)
    tokenStream = CommonTokenStream(lexer)
    parser = LogicParser(tokenStream)
    progCtx = parser.prog()
    idx = 0
    for c in progCtx.getChildren():
        if isCondition(c):
            idx += 1
            print(f"----------- Eval rule {progCtx.RULENUMBER(idx-1)} ------------")
            result = handleRootCondition(c, df=df, df1=df1)
            yield (int(str(progCtx.RULENUMBER(idx-1)).replace(" : ","")), result)

#for event in detect(None):
#    print(event)
