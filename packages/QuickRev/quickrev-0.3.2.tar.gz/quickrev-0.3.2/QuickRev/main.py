def rev(a, b):
        """
        rev(a, b)
        Changing a and b bettwen them 
        """
        return b, a
def shift_list(offset: int, list: str):
    """
    shift_list(offset, list)
    Shift given list to given offset
    """
    shifted_list = []
    for i in range(len(list)):
        new_index = (i + offset) % len(list)
        shifted_list.insert(new_index, list[i])
    return shifted_list    
def create_number(lst: str):
    """
    create_number(list)
    make from given list one number
    """
    num = ''
    for ele in lst:
        try:
            a = int(ele)
            num += str(ele)
        except:
            print("one of elements was deleted cause it is not an integer/float")
    
    return num
def sum_number(lst: str):
    """
    create_number(list)
    make from given list one number
    """
    num = 0
    for ele in lst:
        try:
            num += ele
        except:
            print("one of elements was deleted cause it is not an integer/float")
    
    return num
def inputMas(n: int, sc='\n') -> list:
    r'''
    returns an array from given numbers, 
    default splice char is "\n". You can set it using sc=" "
    '''
    mas = []
    if sc=='\n':
        for i in range(n):
            mas.append(input()) 
    else:
        mas = input().split(sc)
    return mas
def is_prime(n: int)-> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
def factorial(n: int)-> int:
    '''
    Count factorial for non negatives numbers
    '''
    if n < 0:
        raise ValueError("Факториал определён только для неотрицательных чисел")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def gcd(a: int, b: int)-> int:
    '''
    Find Greatest common divisior between 2 numbers
    '''
    while b:
        a, b = b, a % b
    return abs(a)

def lcm(a: int, b: int)-> int:
    '''
    find least common multiple between 2 numbers
    '''
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)

def to_binary(n: int) -> int:
    '''
    Converting the given integer n to its binary representation 
    '''
    if n == 0:
        return "0"
    if n < 0:
        return "-" + to_binary(-n)
    bits = []
    while n > 0:
        bits.append(str(n % 2))
        n //=2
    return "".join(reversed(bits))
