import os
import json
import numpy as np

class FileMatrix:
    def __init__(self, name, shape):
        self.name = name
        self.shape = shape
        self.path = f"temp/{name}"
        os.makedirs(self.path, exist_ok=True)
        with open(f"{self.path}/config.json", "w") as f:
            json.dump({"shape": shape}, f)

    def set_element(self, x, y, value):
        with open(f"{self.path}/{x}_{y}.data", "w") as f:
            f.write(str(value))

    def get_element(self, x, y):
        with open(f"{self.path}/{x}_{y}.data", "r") as f:
            return float(f.read())

    @staticmethod
    def multiply(matrix1, matrix2):
        shape1 = matrix1.shape
        shape2 = matrix2.shape
        result_shape = (shape1[0], shape2[1])
        result = FileMatrix(f"result_{matrix1.name}_{matrix2.name}", result_shape)

        for i in range(result_shape[0]):
            for j in range(result_shape[1]):
                value = 0
                for k in range(shape1[1]):
                    value += matrix1.get_element(i, k) * matrix2.get_element(k, j)
                result.set_element(i, j, value)
        return result

    @staticmethod
    def eval(matrix1):
        shape1 = matrix1.shape
        return f'WanlyArray(shape={shape1})'
        tmp = np.zeros(shape=shape1)

        for i in range(shape1[0]):
            for j in range(shape1[1]):
                tmp[i][j] = matrix1.get_element(i, j)
        return tmp

def convert_numpy_to_filematrix(numpy_array, name):
    rows, cols = numpy_array.shape
    file_matrix = FileMatrix(name, (rows, cols))
    for i in range(rows):
        for j in range(cols):
            file_matrix.set_element(i, j, numpy_array[i, j])
    return file_matrix

def convert_filematrix_to_numpy(file_matrix):
    rows, cols = file_matrix.shape
    numpy_array = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            numpy_array[i, j] = file_matrix.get_element(i, j)
    return numpy_array

class MatrixInterpreter:
    def __init__(self):
        self.matrices = {}

    def execute(self, code):
        lines = code.split('\n')
        current_matrix = None
        current_data = []
        current_python_code = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('create'):
                _, name, rows, cols = line.split()
                self.matrices[name] = FileMatrix(name, (int(rows), int(cols)))

            elif line.startswith('set'):
                _, name, row, col, value = line.split()
                matrix = self.matrices[name]
                matrix.set_element(int(row), int(col), float(value))

            elif line.startswith('multiply'):
                _, name1, name2 = line.split()
                matrix1 = self.matrices[name1]
                matrix2 = self.matrices[name2]
                result_name = f"result_{name1}_{name2}"
                self.matrices[result_name] = FileMatrix.multiply(matrix1, matrix2)

            elif line.startswith('eval'):
                _, name = line.split()
                matrix = self.matrices[name]
                result = FileMatrix.eval(matrix)
                print(np.array(result))

            elif line.startswith('from_list'):
                parts = line.split()
                name = parts[1].strip('{}')
                current_matrix = name
                current_data = []
                continue

            elif current_matrix and line.endswith('}'):
                # End of from_list block
                rows = len(current_data)
                cols = len(current_data[0]) if current_data else 0
                self.matrices[current_matrix] = FileMatrix(current_matrix, (rows, cols))
                for i, row in enumerate(current_data):
                    for j, value in enumerate(row):
                        self.matrices[current_matrix].set_element(i, j, float(value))
                current_matrix = None
                current_data = []

            elif current_matrix:
                # Inside from_list block
                row_values = list(map(float, line.split()))
                current_data.append(row_values)

            elif line.startswith('run_python'):
                current_python_code = []
                continue

            elif current_python_code and line.endswith('}'):
                # Execute the Python code block
                local_vars = {'np': np, 'matrices': self.matrices}
                exec('\n'.join(current_python_code), globals(), local_vars)
                self.matrices.update(local_vars['matrices'])
                current_python_code = []

            elif current_python_code:
                # Inside run_python block
                current_python_code.append(line)

def band_array(interpreter,array,name):
    # 示例代码
     #= MatrixInterpreter()

    file_matrix1 = convert_numpy_to_filematrix(array, name)
    interpreter.matrices[name] = file_matrix1
    #return 

def to_array(interpreter ,matrix):
    # 示例代码
    #= MatrixInterpreter()
    #print(interpreter ,name)
    #result_matrix = interpreter.matrices[name]
    return convert_filematrix_to_numpy(matrix)

def get_matrix(interpreter ,name):
    # 示例代码
    #= MatrixInterpreter()
    #print(interpreter ,name)
    result_matrix = interpreter.matrices[name]
    return result_matrix#convert_filematrix_to_numpy(result_matrix)

def mult_array(interpreter,arr1,arr2):
    # 示例代码
    # = MatrixInterpreter()

    band_array(arr1,'tmp_arr1')
    band_array(arr2,'tmp_arr2')
    code = """

    multiply tmp_arr1 tmp_arr2
    
    """

    interpreter.execute(code)
    return get_array(f'result_tmp_arr1_tmp_arr2')

def mult(interpreter,arr1,arr2):

    #interpreter = MatrixInterpreter()

    code = f"""

    multiply {arr1.name} {arr2.name}
    
    """

    interpreter.execute(code)
    return get_matrix(interpreter,f'result_{arr1.name}_{arr2.name}')






