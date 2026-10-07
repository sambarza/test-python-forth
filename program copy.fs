\ --------------------------------- Precursor ----------------------------------

\ All programming in Forth is done by manipulating the parameter stack (more
\ commonly just referred to as "the stack").
5 4 .s
+ \\ 9
.   \ print
22 +
.
: square dup * ;
5 4 .s