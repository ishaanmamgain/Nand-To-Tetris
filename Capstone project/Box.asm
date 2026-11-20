// Box.asm - Ishaan Mamgain, Roll 2501730241, K = 41
// While any key is pressed (KBD != 0): draw black box
//   starting row = 41, height = 20 rows (41..60), width = 2 words = 32 pixels.
// No key: clear the same area to white.
// To change: edit "@41" (start row) and "@20" (height) in (DRAW).
// Row r, word 0 lives at SCREEN + 32*r.

(LOOP)
    @color
    M=0              // assume white
    @KBD
    D=M
    @DRAW
    D;JEQ            // no key -> keep color = 0
    @color
    M=-1             // key pressed -> color = black (all 16 bits = 1)

(DRAW)
    @41              // START ROW (K)
    D=A
    @tmp
    M=D
    D=D+M           // D = D*2  (x2)
    @tmp
    M=D
    D=D+M           // D = D*2  (x4)
    @tmp
    M=D
    D=D+M           // D = D*2  (x8)
    @tmp
    M=D
    D=D+M           // D = D*2  (x16)
    @tmp
    M=D
    D=D+M           // D = D*2  (x32)
    @SCREEN
    D=D+A            // SCREEN + 32*row
    @addr
    M=D
    @20              // HEIGHT in rows
    D=A
    @rows
    M=D

(ROWLOOP)
    @color
    D=M
    @addr
    A=M
    M=D              // word 0 of this row
    A=A+1
    M=D              // word 1 of this row (width = 2 words = 32 px)
    @32
    D=A
    @addr
    M=D+M            // next row: addr += 32
    @rows
    MD=M-1
    @ROWLOOP
    D;JGT            // more rows?
    @LOOP
    0;JMP            // poll keyboard again
