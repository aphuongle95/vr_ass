import math

# exercise 1.1
class TMatrix:
    def __init__(self, matrix=None):
        self.num_row = 4
        self.num_col = 4
        self.matrix = []
        
        for i in range(self.num_row):                   # store 4x4 transformation matrix
            new_row = []
            for j in range(self.num_col):
                if not matrix:                          # if the matrix is null create an identity matrix
                    if i==j:
                        new_row.append(1)
                    else:
                        new_row.append(0)
                else:
                    new_row.append(matrix[i][j])
            self.matrix.append(new_row)

    def mult(self, other_matrix):
        result = []
        if len(other_matrix) == self.num_col:           # check if dimension match
            for i in range(self.num_row):               # iterate through rows of self matrix
                new_row = []
                for j in range(len(other_matrix[0])):   # iterate through columns of 'other' matrix
                    value = 0                           # init value                                    
                    for q in range(self.num_col):       # iterate through columns of self matrix and rows of other matrix
                        value += self.matrix[i][q] * other_matrix[q][j]
                    new_row.append(round(value, 2)) 
                result.append(new_row)
        return result

    def set_element(self, m, n, v):
        if m is not None and n is not None and v is not None:
            if m<self.num_row and m>=0 and n<self.num_col and n>=0:
                self.matrix[m][n] = v
            else:
                print ("invalid row/column value")


    # EXERCISE 1.4
    def mult_vec(self, vector4):
        vector_mat = []
        for i in range(vector4.dimension):
            vector_mat.append([vector4.vector[i]])
        return self.mult(vector_mat)



# EXERCISE 1.2

def make_trans_mat(x, y, z):                          
    trans_mat = TMatrix()
    trans_mat.set_element(m=0,n=3,v=x)
    trans_mat.set_element(m=1,n=3,v=y)
    trans_mat.set_element(m=2,n=3,v=z)
    return trans_mat

def make_rot_mat(degree, axis):
    rot_mat = TMatrix()
    rad_deg = math.radians(degree)
    if axis == 'x':
        rot_mat.set_element(m=1,n=1,v= math.cos(rad_deg))
        rot_mat.set_element(m=1,n=2,v= -math.sin(rad_deg))
        rot_mat.set_element(m=2,n=1,v= math.sin(rad_deg))
        rot_mat.set_element(m=2,n=2,v= math.cos(rad_deg))
    elif axis == 'y':
        rot_mat.set_element(m=0,n=0,v= math.cos(rad_deg))
        rot_mat.set_element(m=0,n=2,v= math.sin(rad_deg))
        rot_mat.set_element(m=2,n=0,v= -math.sin(rad_deg))
        rot_mat.set_element(m=2,n=2,v= math.cos(rad_deg))
    elif axis == 'z':
        rot_mat.set_element(m=0,n=0,v= math.cos(rad_deg))
        rot_mat.set_element(m=0,n=1,v= -math.sin(rad_deg))
        rot_mat.set_element(m=1,n=0,v= math.sin(rad_deg))
        rot_mat.set_element(m=1,n=1,v= math.cos(rad_deg))

    return rot_mat

def make_scale_mat(x, y, z):
    scale_mat = TMatrix()
    scale_mat.set_element(m=0,n=0,v=x)
    scale_mat.set_element(m=1,n=1,v=y)
    scale_mat.set_element(m=2,n=2,v=z)
    return scale_mat




# EXERCISE 1.3
class Vector4:
    def __init__(self,x,y,z,w):
        self.dimension = 4
        self.vector = []
        if(w!=0):
            self.vector.append(x/w)
            self.vector.append(y/w)
            self.vector.append(z/w)
            self.vector.append(1)

def euclidean_distance(point1, point2):
    distance_square = 0
    dimension_3D = 3
    for i in range(dimension_3D):
        sub_distance_square = math.pow(point1.vector[i],2) + math.pow(point2.vector[i],2)
        distance_square += sub_distance_square
        print(point1.vector[i], point2.vector[i], distance_square)
    return math.sqrt(distance_square)







# TESTING 1.1
identity_mat = TMatrix() 
# print("identity_mat = " + str(identity_mat.matrix))

A = TMatrix(matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]])
B = [[1,3,5,7],[9,11,13,15],[2,4,6,8],[10,12,14,16]]
# print("A = " + str(A.matrix))
# print("B = " + str(B))
# print("A.B = " + str(A.mult(B)))



# TESTING 1.2

trans_mat = make_trans_mat(1,2,3)
# print(trans_mat.matrix)

rot_mat_x = make_rot_mat(45,'x')
rot_mat_y = make_rot_mat(90,'y')
rot_mat_z = make_rot_mat(120,'z')

#print(rot_mat_x.matrix)
#print(rot_mat_y.matrix)
#print(rot_mat_z.matrix)

scale_mat = make_scale_mat(1,2,3)
#print(scale_mat.matrix)



# TESTING 1.3
vector1 = Vector4(2,4,6,2)
vector2 = Vector4(0,0,0,1)
#print(euclidean_distance(vector1,vector2))

# TESTING 1.4
vector4 = Vector4(1,2,3,1)
#print(A.mult_vec(vector4))


# TESTING 1.5
rot_mat_ex5 = make_rot_mat(90,'x')
# print(rot_mat_ex5.mult(make_rot_mat(30,'z').matrix))
# print(make_rot_mat(-30,'y').mult(rot_mat_ex5.matrix))


# print(trans_mat.mult([[1],[2],[3],[1]]))
# print(rot_mat_z.mult([[1],[0],[0],[1]]))
# print(scale_mat.mult([[1],[2],[3],[1]]))
# print(A.mult_vec(vector4))
# alpha = -beta


# Calculating TMatrix for 1.6
# print(make_trans_mat(5,0,-2).mult(make_rot_mat(90,'y').matrix))
print(make_rot_mat(90,'y').mult(make_trans_mat(5,0,-2).matrix))
print(make_trans_mat(-4,0,2).mult(make_scale_mat(0.5,0.5,0.5).matrix))
print(make_scale_mat(0.5,0.5,0.5).mult(make_trans_mat(-4,0,2).matrix))
print(make_trans_mat(-2,0,4).mult(make_scale_mat(0.5,0.5,0.5).mult(make_rot_mat(180,'y').matrix)))


