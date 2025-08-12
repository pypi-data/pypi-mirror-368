# cube = [[[0,0,0],[0,0,0],[0,0,0]],
#         [[1,1,1],[1,1,1],[1,1,1]],
#         [[2,2,2],[2,2,2],[2,2,2]],
#         [[3,3,3],[3,3,3],[3,3,3]],
#         [[4,4,4],[4,4,4],[4,4,4]],
#         [[5,5,5],[5,5,5],[5,5,5]]]
import numpy as np
C_FACES = "ULFRBD"
C_NUMBERS = "012345"
C_COLORS = "WOGRBY"
def double_move_method(method):
    def wrapper(self):
        method(self)
        method(self)
    return wrapper

class Cube:
    def __init__(self,state):
        self.state = state

    @classmethod
    def solved(cls,colors=C_FACES):
        return cls([[[c for _ in range(3)] for _ in range(3)] for c in colors])
    
    def apply(self, alg):
        alg = norm_alg(alg)
        for move in alg:
            move = move.strip().replace("'", "i")  # Replace ' with i for inverse moves
            if hasattr(self, move):
                getattr(self, move)()
            else:
                raise ValueError(f"Invalid move: {move}")
            
    def __repr__(self):
        return f"""\
    {self._row(0,0)}
    {self._row(0,1)}
    {self._row(0,2)}
{self._row(1,0)} {self._row(2,0)} {self._row(3,0)} {self._row(4,0)}
{self._row(1,1)} {self._row(2,1)} {self._row(3,1)} {self._row(4,1)}
{self._row(1,2)} {self._row(2,2)} {self._row(3,2)} {self._row(4,2)}
    {self._row(5,0)}
    {self._row(5,1)}
    {self._row(5,2)}
        """
        #return f"    {self._row(0,0)}\n    {self._row(0,1)}\n    {self._row(0,2)}"
    def _row(self,face,row):
        return "".join(self.state[face][row])
        return "\n".join([" ".join([str(cell) for cell in row]) for face in self.state for row in face])
    def U(self):
        self._y(0)
        self._cw(0)

    def Ui(self):
        self._yi(0)
        self._ccw(0)

    def L(self):
        self._xi(0)
        self._cw(1)
    
    def Li(self):
        self._x(0)
        self._ccw(1)

    def F(self):
        self._z(0)
        self._cw(2)

    def Fi(self):
        self._zi(0)
        self._ccw(2)

    def R(self):
        self._x(2)
        self._cw(3)

    def Ri(self):
        self._xi(2)
        self._ccw(3)

    def B(self):
        self._zi(2)
        self._cw(4)

    def Bi(self):
        self._z(2)
        self._ccw(4)

    def D(self):
        self._yi(2)
        self._cw(5)

    def Di(self):
        self._y(2)
        self._ccw(5)

    def M(self):
        self._xi(1)

    def Mi(self):
        self._x(1)

    def E(self):
        self._yi(1)
    
    def Ei(self):
        self._y(1)

    def S(self):
        self._z(1)

    def Si(self):
        self._zi(1)

    def x(self):
        self._x(0)
        self._x(1)
        self._x(2)
        self._ccw(1)
        self._cw(3)

    def xi(self):
        self._xi(0)
        self._xi(1)
        self._xi(2)
        self._cw(1)
        self._ccw(3)

    def y(self):
        self._y(0)
        self._y(1)
        self._y(2)
        self._cw(0)
        self._ccw(5)

    def yi(self):
        self._yi(0)
        self._yi(1)
        self._yi(2)
        self._ccw(0)
        self._cw(5)

    def z(self):
        self._z(0)
        self._z(1)
        self._z(2)
        self._cw(2)
        self._ccw(4)

    def zi(self):
        self._zi(0)
        self._zi(1)
        self._zi(2)
        self._ccw(2)
        self._cw(4)

    U2 = double_move_method(U)
    Ui2 = double_move_method(Ui)
    L2 = double_move_method(L)
    Li2 = double_move_method(Li)
    F2 = double_move_method(F)
    Fi2 = double_move_method(Fi)
    R2 = double_move_method(R)
    R2i = double_move_method(Ri)
    B2 = double_move_method(B)
    B2i = double_move_method(Bi)
    D2 = double_move_method(D)
    D2i = double_move_method(Di)
    M2 = double_move_method(M)
    M2i = double_move_method(Mi)
    E2 = double_move_method(E)
    E2i = double_move_method(Ei)
    S2 = double_move_method(S)
    S2i = double_move_method(Si)
    x2 = double_move_method(x)
    x2i = double_move_method(xi)
    y2 = double_move_method(y)
    y2i = double_move_method(yi)
    z2 = double_move_method(z)
    z2i = double_move_method(zi)
    
    def _y(self,row):

        self.state[1][row],self.state[2][row],self.state[3][row],self.state[4][row] = \
        self.state[2][row],self.state[3][row],self.state[4][row],self.state[1][row]
        
    def _yi(self,row):
        # self.cube[1][row],self.cube[2][row],self.cube[3][row],self.cube[4][row] = \
        # self.cube[4][row],self.cube[1][row],self.cube[2][row],self.cube[3][row]
        self.state[1][row],self.state[4][row],self.state[3][row],self.state[2][row] = \
        self.state[4][row],self.state[3][row],self.state[2][row],self.state[1][row]

    def _x(self,col):
        for i in range(3):
            self.state[0][i][col],     self.state[2][i][col],   self.state[5][i][col], self.state[4][2-i][2-col] = \
            self.state[2][i][col],   self.state[5][i][col],     self.state[4][2-i][2-col], self.state[0][i][col]

    def _xi(self,col):
        for i in range(3):
            self.state[0][i][col],     self.state[4][2-i][2-col],   self.state[5][i][col], self.state[2][i][col] = \
            self.state[4][2-i][2-col],   self.state[5][i][col],     self.state[2][i][col], self.state[0][i][col]

    def _x2(self,col):
        for i in range(3):
            self.state[0][i][col],     self.state[2][i][col],   self.state[5][i][col], self.state[4][2-i][2-col] = \
            self.state[5][i][col],   self.state[4][2-i][2-col],     self.state[0][i][col], self.state[2][i][col]
            
    def _z(self,layer):
        for i in range(3):
            self.state[0][2-layer][i],     self.state[1][2-i][2-layer],  self.state[5][layer][2-i],   self.state[3][i][layer] = \
            self.state[1][2-i][2-layer],  self.state[5][layer][2-i],   self.state[3][i][layer],     self.state[0][2-layer][i]

    def _zi(self,layer):
        for i in range(3):
            self.state[0][2-layer][i],     self.state[3][i][layer],  self.state[5][layer][2-i],   self.state[1][2-i][2-layer] = \
            self.state[3][i][layer],  self.state[5][layer][2-i],   self.state[1][2-i][2-layer],     self.state[0][2-layer][i]

    # def _clockwise2(self,face):
    #     cface = self.cube[face]
    #     # Rotate the face clockwise by reversing rows and then transposing
    #     self.cube[face] = [[cface[2-j][i] for j in range(3)] for i in range(3)]

    def _cw(self,face):
        #cface = self.cube[face]
        # Rotate the face clockwise by reversing rows and then transposing
        self.state[face] = [list(row) for row in zip(*self.state[face][::-1])]

    def _ccw(self,face):
        #cface = self.cube[face]
        # Rotate the face counterclockwise by transposing and then reversing rows
        self.state[face] = [list(row) for row in zip(*self.state[face])][::-1]
def norm_alg(alg):
    if isinstance(alg,str):
        alg = alg.split()
    assert isinstance(alg, (list,tuple,set))
    return [move.strip() for move in alg]

def reverse_alg(alg):
    return [move[0] if "'" in move else move+"'" for move in norm_alg(alg)[::-1]]


