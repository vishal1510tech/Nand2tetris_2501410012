// Box.asm for K = 12

(LOOP)
    @KBD
    D=M
    @SET_WHITE
    D;JEQ         
    @color
    M=-1
    @DRAW_INIT
    0;JMP

(SET_WHITE)
    @color
    M=0

(DRAW_INIT)
    @16768
    D=A
    @addr
    M=D

    @20
    D=A
    @count
    M=D

(DRAW_LOOP)
    @color
    D=M
    @addr
    A=M
    M=D

    @32
    D=A
    @addr
    M=D+M

    @count
    MD=M-1
    @DRAW_LOOP
    D;JGT

    @LOOP
    0;JMP