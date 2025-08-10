def calculate(weight, height):
    """Calculate BMI: weight in kg, height in meters"""
    return weight / (height ** 2)

def category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"
