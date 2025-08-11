def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        return "Error: Division by zero"
    return x / y

def calculator():
    print("Simple Calculator")
    print("Operations: +, -, *, /")
    
    while True:
        try:
            # Get user input
            num1 = float(input("Enter first number: "))
            operator = input("Enter operator (+, -, *, /) or 'quit' to exit: ")
            
            if operator.lower() == 'quit':
                print("Goodbye!")
                break
                
            num2 = float(input("Enter second number: "))
            
            # Perform calculation
            if operator == '+':
                result = add(num1, num2)
            elif operator == '-':
                result = subtract(num1, num2)
            elif operator == '*':
                result = multiply(num1, num2)
            elif operator == '/':
                result = divide(num1, num2)
            else:
                print("Invalid operator")
                continue
                
            print(f"Result: {result}")
            
        except ValueError:
            print("Invalid input. Please enter numbers only.")

if __name__ == "__main__":
    calculator()