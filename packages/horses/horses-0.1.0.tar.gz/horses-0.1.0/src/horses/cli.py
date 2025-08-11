import sys
import random

def help_message():
    return """Usage: race <horses> [options]

<horses> is a set of horses to race

Options:
    -h, --help:     Display this help message (all other options are ignored if this is present)
    Only one of the following may be set:
    --horse:    Display the horses presentation
    --horses:   Display the horses presentation
    --race:     Start the race and shows the final winner
    --run:      Start the race and shows the final winner

Examples:

    $ horse/horses
    Hello, my name is Lone Lightning the talking horse 
    I'm faster than 48.46% of horses

    $ race/run/go horse
    (horse's name) is in the lead
    (horse's name) is the winner!"""

def parse_args(args):
    """Parse the command line arguments. 
    If there is an error, print an error message and exit.
    args must be a list of strings, each string being one argument.
    See print_help for the expected format of the arguments
    Returns a tuple of two values:
    - Name of all the horses compeating on the race. 
    - A String with a summary of which horse won on the race."""
    if len(args) == 0 or ("-h" in args) or ("--help" in args):
        print(help_message())
        sys.exit(1)  # Exiting with a non-zero status is a convention to indicate an error

    valid_commands = ["horse", "horses", "race" , "run"]
    commands_found = [arg.lstrip('-') for arg in args if arg.lstrip('-') in valid_commands] # Get valid commands without leading dashes

    if len(commands_found) == 0: # If the argument is not a valid command, prints error message.
        print(f"Error: You must provide one of {valid_commands}")
        sys.exit(1)
    if len(commands_found) > 1: # If the argument is more than one valid command, prints error message.
        print(f"Error: Only one command allowed at a time: {valid_commands}")
        sys.exit(1)
    return commands_found[0]

try:
    with open("./horses.csv", 'r') as file_handle:
        lines = [item.strip().split(',') for item in file_handle.readlines()]
except ValueError:
        print("Error: Horse data contains invalid speed or luck values. They must be numbers.")
        sys.exit(1)
        
header = lines[0]
rows = lines[1:]
mapped_rows = [dict(zip(header,row)) for row in rows] # Combines each element in the header, with every element on the rest of the rows

for horse in mapped_rows: # Convert string element (luck) into float
    horse["luck"] = float(horse["luck"])

horses = mapped_rows
random.shuffle(horses)

def speak(horse):
    """Return all the horses' names on file as a string"""
    return f"Hello, my name is {horse['name']} the talking horse "
        
def lucky_day(horse):
    """Read the horse's luck, compares it to a random float between 0 and 1.
    if the horse's luck is greater than this random number, then it increases
    its speed two times."""
    luck = horse["luck"]> random.uniform(0,1) 
    if luck: 
        horse ["speed"]*=2 
        
def run(horse):
    """Return all the horses' speed as a string"""
    return f"I'm faster than {horse['speed']}% of horses " 
        
def race(horses):
    """Takes the first horse in the randomized list and makes it the leading horse.
    After that, it iterates through every other horse, if the speed of the current
    horse is greater than the one that was leading, then the current one becomes the
    leading horse. Returns the last horse in the lead position as a winner."""
    winning_horse = horses[0] 
    print(f"{winning_horse['name']} is in the lead") 
    for horse in horses[1:]:
        if horse["speed"] > winning_horse["speed"]: 
            winning_horse = horse 
            print(f"{horse['name']} is in the lead") 
    return f"{winning_horse['name']} is the winner!" 

def main():
    """Takes the arguments and pass them through the parse_args funtions.
    If the arguments are equal to "horse" or "horses", then it prints the 
    horses' introduction. If the arguments are equal to "race" or "run",
    it will print which horses are leading and the final winner."""
    args = sys.argv[1:]
    command = parse_args(args)
    if command in ["horse", "horses"]:
        for horse in mapped_rows:
            print(speak(horse))
            lucky_day(horse) 
            print(run(horse))
    elif command in ["race", "run"]:
        for horse in mapped_rows:
            lucky_day(horse) 
        print(race(horses))

if __name__ == "__main__":
    main()