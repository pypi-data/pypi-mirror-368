import sys

def celsius_to_fahrenheit(c):
    return (c * 9 / 5) + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9

def celsius_to_kelvin(c):
    return c + 273.15

def kelvin_to_celsius(k):
    return k - 273.15

def fahrenheit_to_kelvin(f):
    return celsius_to_kelvin(fahrenheit_to_celsius(f))

def kelvin_to_fahrenheit(k):
    return celsius_to_fahrenheit(kelvin_to_celsius(k))

def main():
    if len(sys.argv) != 4:
        print("Usage: tempconv <value> <from_unit> <to_unit>")
        print("Units: C, F, K")
        sys.exit(1)

    try:
        value = round(float(sys.argv[1]), 2)
    except ValueError:
        print("Error: <value> must be a number")
        sys.exit(1)

    from_unit = sys.argv[2].strip().upper()
    to_unit = sys.argv[3].strip().upper()

    valid_units = {"C", "F", "K"}
    if from_unit not in valid_units or to_unit not in valid_units:
        print(f"Error: Units must be one of {', '.join(valid_units)}")
        sys.exit(1)

    if from_unit == to_unit:
        print(f"{value}°{from_unit} = {value}°{to_unit}")
        sys.exit(0)

    conversions = {
        ("C", "F"): celsius_to_fahrenheit,
        ("F", "C"): fahrenheit_to_celsius,
        ("C", "K"): celsius_to_kelvin,
        ("K", "C"): kelvin_to_celsius,
        ("F", "K"): fahrenheit_to_kelvin,
        ("K", "F"): kelvin_to_fahrenheit,
    }

    result = conversions[(from_unit, to_unit)](value)
    print(f"{value}°{from_unit} = {result:.2f}°{to_unit}")

if __name__ == "__main__":
    main()
