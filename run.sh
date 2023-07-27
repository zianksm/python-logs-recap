#!/bin/bash

# Function to check if a Python package is installed
check_package() {
    python -c "import $1" 2> /dev/null
}

# Check the operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    # macOS (Mac OS X)
    if ! check_package "numpy"; then
        echo "numpy not found. Installing numpy..."
        python3 -m pip install numpy
    fi

    if ! check_package "pandas"; then
        echo "pandas not found. Installing pandas..."
        python3 -m pip install pandas
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows"
    # Windows
    if ! check_package "numpy"; then
        echo "numpy not found. Installing numpy..."
        python -m pip install numpy
    fi

    if ! check_package "pandas"; then
        echo "pandas not found. Installing pandas..."
        python -m pip install pandas
    fi
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

# Your Python script code goes here
python3 rekap.py