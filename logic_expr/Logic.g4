grammar Logic;
prog: (RULENUMBER condition NEWLINE)* ;
expr: TAG
    | LAST
    | DERIVATIVE
    | NUMBER
    ;
DERIVATIVE: DERIVATIVE_START TAG BLOCK_END ;

DERIVATIVE_START: 'd(' ;

BLOCK_END: ')' ;

COMP: ' == '|' >= '|' <= '|' != '|' < '|' > ' ;

condition: expr COMP expr
        | condition LOGIC condition
        ;

LOGIC: ' AND ' ;

LAST_START : 'last(' ;

LAST: LAST_START TAG BLOCK_END ;

TAG: [a-zA-Z] [0-9a-zA-Z_\u002E]+ ;
NUMBER: DIGIT | DIGIT '.' DIGIT
      ;
DIGIT: [0-9]+ ;
RULENUMBER: DIGIT COLON ;
COLON: ' : ' ;
NEWLINE: [\n\r]+ ;
