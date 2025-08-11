import sys  # To access command-line arguments

def main():
    # Check if user provided input filename or asked for help
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print("(poetry run gaganfinal [textfile]) use this command to count the word of your text")
        return

    try:
        # Try opening the input file
        f = open(sys.argv[1])
        try:
            # Read the entire file content and split into words
            words = f.read().split()
        finally:
            # Always close the file after reading
            f.close()
    except FileNotFoundError:
        # If file not found, show an error message and exit
        print(f"Error: file '{sys.argv[1]}' not found.")
        return

    # Prepare the output message showing word count
    result = f"Word count: {len(words)}"

    output_file="word_count_output.txt"

    # If an output file is given, write the result to it
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write(result)
        print(f"Output written to {sys.argv[2]}")
    else:
        # Otherwise, just print the result to the console
        print(result)
        
# Run the main function when the script is executed directly
if __name__ == "__main__":
    main()
