import subprocess
import sys
import re
import shutil
import random
import os

USAGE_FILE = os.path.expanduser("~/.tldr_usage")

def detect_python_cmd():
    for cmd in ["python3", "python"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
            if result.returncode == 0 and "Python 3" in result.stdout + result.stderr:
                return cmd
        except FileNotFoundError:
            continue
    print("Could not find a working Python 3 interpreter. Run 'tldr --help' for quick docs")
    sys.exit(1)

python_cmd = detect_python_cmd()

milestones = [1, 10, 50, 100, 200, 300, 400, 500, 1000]
def increment_usage(reset=False):
    count = 0
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            try:
                count = int(f.read().strip())
            except:
                count = 0
    count += 1
    if (reset):
        count = 0
    with open(USAGE_FILE, "w") as f:
        f.write(str(count))
    return count


def ask(error = "say No Error Passed and tell a joke", codeLine = "no code"):
    from ollama import chat
    from ollama import ChatResponse
    import textwrap


    if shutil.which("ollama") is None:
        ollamaHelp()
    else:

        # job = "Explain Python errors simply: Explain error and suggest fix. No made-up code. Beginner. Be fast. 2-3 sentence max"
        job = "Explain and suggest code fix for Python error in short 1-2 sentences. No formatting, no intro. Infer intention and fix given code"
        
        print(random.choice(["Thinking...", "Working...", "Analyzing...", "Processing...", "Loading...", "Waiting...", "Fetching...", "Reading..."]))
        response: ChatResponse = chat(model='llama3:8b', messages=[
        {
            'role': 'user',
            'content': (job + error + codeLine),
        },
        ])

        wrapped = textwrap.fill(response['message']['content'], width=100)

        print("\n" + "─" * 110)
        print("🧠 TL;DR:")
        print(wrapped)
        print("─" * 110)



def ollamaHelp():
    print("─" * 90)
    print("""Ollama might not installed or configured properly on your device. To use \033[92mtldr\033[0m for more 
complex problems, follow the instructions below

\033[91mPrivacy Note:\033[0m
\033[92mtldr\033[0m will only use Ollama if it cannot solve the current problem on its own
Your data will not be sent to the Cloud or be stored externally in any circumstance
          
\033[93mInstallation:\033[0m
    1. In your terminal, run \033[94mpip install ollama\033[0m
    2. Visit \033[94mhttps://ollama.com/\033[0m and download the installer
    3. Run the installer and follow the setup instructions
    4. Once installed, open a terminal and run \033[94mollama run llama3:8b\033[0m
          
    You can check if your setup was successful by running \033[94mtldr -c\033[0m
          
    \033[91mNote:\033[0m \033[92mtldr\033[0m may take up to a minute to run when Ollama is in use. Don't close out
    """)

    print("─" * 90)

def checkOllama():
    if shutil.which("ollama") is None:  
        message = "Ollama was not installed or configured properly"
        print("\n" + "─" * (len(message) + 3))
        print(message)
        print("─" * (len(message) + 3))
    else:
        message = "Your setup was successful, you're ready to go!"
        print("\n" + "─" * (len(message) + 3))
        print(message)
        print("─" * (len(message) + 3))

def printVersion(path="setup.py"):
    with open(path) as f:
        content = f.read()
    match = re.search(r'version\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    print("v" + match.group(1))
    return 



def autofix(errorType = "other", lineNum = 0):
    increment_usage()

    if (errorType == "expectedIndent"):
        file_path = sys.argv[1]
        with open(file_path, "r") as file:
            code = file.readlines()

        lineNum = int(lineNum) - 1
        aboveLine = lineNum - 1

        while (len(code[aboveLine]) == 1):
            aboveLine = aboveLine - 1

        aboveIndent = len(code[aboveLine]) - len(code[aboveLine].lstrip(' '))
        # print(f"working in line: {(lineNum)}")
        # print(f"Total length above: {len(code[aboveLine])}")
        # print(f"Excluding Spaces: {len(code[aboveLine].lstrip(' '))}")
        # print(f"Num Spaces Above: {aboveIndent}")
        code[lineNum] = (" " * (aboveIndent + 4)) + code[lineNum].lstrip()

        with open(file_path, "w") as file:
            file.writelines(code)

        print("\n" + "─" * 40)
        print(f"Expected indent error in line {lineNum + 1} \033[92mfixed!\033[0m")
        print("─" * 40)
        return

    elif (errorType == "unexpectedIndent"):
        file_path = sys.argv[1]
        with open(file_path, "r") as file:
            code = file.readlines()

        lineNum = int(lineNum) - 1
        aboveLine = lineNum - 1

        while (len(code[aboveLine]) == 1):
            aboveLine = aboveLine - 1

        aboveIndent = len(code[aboveLine]) - len(code[aboveLine].lstrip(' '))
        # print(f"working in line: {(lineNum)}")
        # print(f"Total length above: {len(code[aboveLine])}")
        # print(f"Excluding Spaces: {len(code[aboveLine].lstrip(' '))}")
        print(f"Num Spaces Above: {aboveIndent}")

        if (aboveIndent == 0):
            code[lineNum] = code[lineNum].lstrip(' ')
        else:
            code[lineNum] = code[lineNum][aboveIndent:]

        with open(file_path, "w") as file:
            file.writelines(code)

        print("\n" + "─" * 44)
        print(f"Unexpected indent error in line {lineNum + 1} \033[92mfixed!\033[0m")
        print("─" * 44)
        return

    elif errorType == "IndexError":
        file_path = sys.argv[1]
        with open(file_path, "r") as file:
            code = file.readlines()

        lineNum = int(lineNum) - 1
        
        match = re.search(r"\[(.*?)\]", code[lineNum])
        if match:
            if int(match.group(1)) < 0 and int(match.group(1)) != -1:
                code[lineNum] = code[lineNum].replace(f"{match.group(1)}", "0")
                with open(file_path, "w") as file:
                    file.writelines(code)
                print("\n" + "─" * 63)
                print(f"Out of bounds index in line {lineNum + 1} \033[92mfixed!\033[0m Updated to first index")
                print("─" * 63)
                return
            else:
                code[lineNum] = code[lineNum].replace(f"{match.group(1)}", "-1")
                with open(file_path, "w") as file:
                    file.writelines(code)
                print("\n" + "─" * 62)
                print(f"Out of bounds index in line {lineNum + 1} \033[92mfixed!\033[0m Updated to last index")
                print("─" * 62)
                return

    # get code line and send it as well
    file_path = sys.argv[1]
    with open(file_path, "r") as file:
        code = file.readlines()

    lineNum = int(lineNum)

    context = code[lineNum - 2] + code[lineNum - 1] + code[lineNum]
    print(context)
    ask(errorType, context)
    
def printStats():
    count = 0
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            try:
                count = int(f.read().strip())
            except:
                count = 0
    if (count == 1):
        print(f"You have used \033[92mtldr\033[0m {count} time!")
    elif (count != 0):
        print(f"You have used \033[92mtldr\033[0m {count} times!")
    if (count == 0):
        print("Looks like you have't used \033[92mtldr\033[0m yet")
        print("Get started with \033[94mtldr --help\033[0m")

def getTypeName(type):
    if type == "int":
        return "integer"
    elif type == "str":
        return "string"
    elif type == "float":
        return "float"
    elif type == "bool":
        return "boolean"
    else:
        return "not-so-basic-type"

#cooked
def simple_tldr(error_text):
    # Get line number of error
    line_number = None
    line_match = re.search(r'File ".*?", line (\d+)', error_text)
    if line_match:
        line_number = line_match.group(1)

    if "NameError" in error_text:
        match = re.search(r"NameError: name '(.+?)' is not defined", error_text)
        if match:
            # return f"The variable '{match.group(1)}' is used but not defined. Try assigning it first."
            return (random.choice([
                f"Looks like '{match.group(1)}' isn't defined. Did you forget to declare it before using it in line {line_number}?",
                f"The variable '{match.group(1)}' is used in line {line_number}, but it was never defined. Try assigning it first",
                f"In line {line_number} you used '{match.group(1)}', but you never told the computer what '{match.group(1)}' is!",
                f"Double check '{match.group(1)} before line {line_number} to see if it was initialized properly",
                f"You should double check line {line_number} to see if '{match.group(1)}' was assigned a value before using it",
                f"Before line {line_number}, did you remember to declare '{match.group(1)}'?"
            ]), "NameError", line_number)

    elif "SyntaxError" in error_text:
        line_number = None
        line_match = re.search(r'File ".*?", line (\d+)', error_text)
        if line_match:
            line_number = line_match.group(1)

        return ("Classic, there's a syntax error in your code. Check for missing colons, parentheses, or indentation.", "SyntaxError", line_number)

    elif "TypeError" in error_text:
        match = re.search(r"TypeError: unsupported operand type\(s\) for (\+|\-|\*|\/): '(.+?)' and '(.+?)'", error_text)

        if match:
            operator = match.group(1)
            type1 = getTypeName(match.group(2))
            type2 = getTypeName(match.group(3))

        else:
            match = re.search(r'TypeError: can only concatenate (\w+) \(not "(.+?)"\) to (\w+)', error_text)
            if match:
                operator = '+'
                type1 = getTypeName(match.group(1)) 
                type2 = getTypeName(match.group(2)) 

        if match:
            line_match = re.search(r'File ".*?", line (\d+)', error_text)
            line_number = line_match.group(1) if line_match else "unknown"

            return (random.choice([
                f"You're using incompatible types in line {line_number} (in this case, a {type1} and {type2}). Check your types",
                f"In line {line_number}, you're trying to use the '{operator}' operator for a {type1} and a {type2}, but that's not allowed right now",
                f"Check your types in line {line_number}. You are trying to use '{operator}' on a {type1} and a {type2}",
                f"In line {line_number}, the '{operator}' operation can't be done between a {type1} and a {type2}",
                f"Line {line_number} is trying to do '{operator}' between a {type1} and a {type2}, which usually isn't supported. You might need a type cast",
                f"The '{operator}' operation in line {line_number} doesn't work with a {type1} and a {type2}. Check your variable types or logic"
            ]), "TypeError", line_number)

    elif "IndentationError" in error_text:
        line_number = None
        line_match = re.search(r'File ".*?", line (\d+)', error_text)
        if line_match:
            line_number = line_match.group(1)

        if "expected an indented block" in error_text:
            errorType = "expectedIndent"
        elif "unexpected indent" in error_text:
            errorType = "unexpectedIndent"
        else:
            errorType = "other"

        return ((random.choice([
            f"Your code has an incorrect indentation on line {line_number}",
            f"In line {line_number}, your code isn't properly indented",
            f"Fix your indentation in line {line_number} and try again",
            f"Line {line_number} has an indentation issue. Check your spaces/tabs!",
            f"There is an indentation issue in line {line_number}",
            f"Try fixing the indentation error in line {line_number} and see if it works",
            f"Seems like you didn't indent properly in line {line_number}"
        ])+ f"\nTry \033[94mtldr {sys.argv[1]} --autofix\033[m"), errorType, line_number)
    
    elif "IndexError" in error_text:
        line_number = None
        line_match = re.search(r'File ".*?", line (\d+)', error_text)
        if line_match:
            line_number = line_match.group(1)

        return ((random.choice([
            f"Your code is trying to access an object that doesn't exist on line {line_number}",
            f"Looks like you're going out of bounds on a list in line {line_number}",
            f"Line {line_number} might be using an index that’s bigger than the list size",
            f"In line {line_number}, make sure your index isn't bigger than your list size",
            f"Your code in line {line_number} assumes the list is longer than it actually is",
            f"Try fixing your accessed index in line {line_number} and see if it works",
            f"The index in line {line_number} is outside the list’s range, causing an error"
        ])+ f"\nTry \033[94mtldr {sys.argv[1]} --autofix\033[m"), "IndexError", line_number)

    elif "ZeroDivisionError" in error_text:
        return (random.choice([
            f"You're trying to divide by zero in line {line_number}. For now, this is impossible",
            f"Check your math in line {line_number}. It looks like you are trying to divide by zero"
        ]), "ZeroDivisionError", line_number)
    
    elif "RecursionError" in error_text:
        return (random.choice([
            f"You've hit the recursion limit in line {line_number}. Did you forget a base case?",
            f"Your recursion went deeper than what Python can handle in line {line_number}. Double check that you are exiting out out it!",
            f"In line {line_number}, you might be missing a base case. Your function tries to go on forever",
            f"Too much recursion in line {line_number}. Check if your function calls itself without a stopping condition",
            f"In line {line_number}, the recursive loop goes unchecked. Make sure there is an exit path!",
            f"The recursive stack is beyond Python's capabilities right now. Check line {line_number} for any forever calls",
            f"Line {line_number} looks to add to the recursive stack without stopping. Make sure there is a base case for Python to exit"
        ]), "RecursionError", line_number)
    
    elif "AttributeError" in error_text:
        match = re.search(r"AttributeError: '(.+?)' object has no attribute '(.+?)'", error_text)
        if match:
            obj_type, attr = match.groups()
            obj_type = getTypeName(obj_type)

        return (random.choice([
            f"Line {line_number} has attribute error. A {obj_type} can't do '{attr}'",
            f"In line {line_number}, you're trying to use '{attr}' on a {obj_type}, which isn't allowed",
            f"The '{attr}' attribute does not exist for the {obj_type} type. Make sure you are calling valid attributes",
            f"The '{attr}' attribute you are trying to call for the {obj_type} on line {line_number} does not exist. Check for typos or mismatched type",
            f"The {obj_type} type does not have a '{attr}' attribute. Check line {line_number} to see if there are typos or a incorrect call",
            f"You are trying to use '{attr}' attribute in line {line_number}, but it doesn't exist for a {obj_type} type",
            f"For the {obj_type} in line {line_number}, there is no valid '{attr}' attribute. You might have misspelled something"
        ]), "AttributeError", line_number)
    
    elif "ModuleNotFoundError" in error_text:
        match = re.search(r"No module named '(.+?)'", error_text)
        if match:
            missing_module = match.group(1)

        return ((random.choice([
            f"Your code is trying to import a module in line {line_number} that hasn't been installed",
            f"The module '{missing_module}' is not installed",
            f"The module '{missing_module}' in line {line_number} is not recognized",
            f"Double check line {line_number} and make sure the module name is correct",
            f"Line {line_number} is trying to use '{missing_module}'. Make sure it is installed",
            f"Make sure that the module '{missing_module}' jn line {line_number} is not a typo",
            f"Python does not recognize '{missing_module}' as being installed correctly"
        ])+ f"\nIf the module name is correct, try \033[94mpip install {missing_module}\033[m"), "ModuleNotFoundError", line_number)

    return (f"Hmmm, maybe \033[94mtldr {sys.argv[1]} --autofix\033[m might help", error_text, 0)

def printHelp():
    print("""
        \033[92mtldr\033[0m: Your CLI helper for understanding errors faster and easier

        \033[92mBasics\033[0m:
            \033[94mtldr <filename>.py\033[0m                 # Run code and explain error 
            \033[94mtldr --help (-h)\033[0m                   # Show quick docs
            \033[94mtldr --version (-v)\033[0m                # Show current version
            \033[94mtldr --reset (-r)\033[0m                  # Reset and clear all data
          
        \033[91mNote\033[0m:
            tldr is able to handle a majority of errors on its own without outside support
            However, there are always some errors that we cannot predict
            Be sure to install Ollama locally so that tldr can give you the best support 
          
        \033[93mExperimental\033[0m:
            \033[94mtldr <filename>.py --autofix\033[m       # An experimental flag that solves faulty lines of code by itself
                                                 \033[91mUse with caution\033[0m: while --autofix is powerful, only use it for 
                                                 simple errors. Larger LLMs might be better for complex errors. Remember, these 
                                                 are just tools to help you and they should not serve as a replacement
            \033[94mtldr --ol (-o)\033[0m                     # Setup instructions and help for --autofix
            \033[94mtldr --oc (-c)\033[0m                     # Verify if setup was done correctly
            \033[94mtldr --stats (-s)\033[m                  # See how many times you have used tldr, what your most common errors are, and more!
        
    """)

    # \033[91m red text\033[0m
    # \033[92m green text\033[0m
    # \033[93m yellow text\033[0m
    # \033[94m blue text\033[0m

def printIntro():
    print("\n" + "─" * 36)
    print("Welcome to \033[92mtldr\033[0m!")
    print("For quick docs, run \"\033[92mtldr\033[0m \033[91m--help\033[0m\"")
    print(random.choice(["Good Luck!", "Happy Coding!"]))
    print("─" * 36)
    sys.exit(1)

def main():
    # change 2 to 1 when doing tldr example.py 
    # in "tldr example.py", the tldr is counted so the sys.argv is 2
    # however, if you are doing "python example.py", python is ignored so the length is 1
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        # print("Usage: python tldrpython.py your_script.py") //was old version without packaging
        printIntro()

    if len(sys.argv) == 2:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            printHelp()
            return
        elif sys.argv[1] == "--version" or sys.argv[1] == "-v":
            printVersion()
            return
        elif sys.argv[1] == "--ol" or sys.argv[1] == "-o":
            ollamaHelp()
            return
        elif sys.argv[1] == "-c":
            checkOllama()
            return
        # for testing
        elif sys.argv[1] == "-p":
            ask()
            return
        elif sys.argv[1] == "--reset" or sys.argv[1] == "-r":
            response = input("Reset? [y/N]: ").strip().lower()
            if response == "y":
                increment_usage(True)
                print("\033[91mReset complete\033[0m")
            else:
                print("Reset aborted")
            return
        elif sys.argv[1] == "--stats" or sys.argv[1] == "-s":
            printStats()
            return
    # else:
    #     print("\n" + "─" * 36)
    #     print("Welcome to \033[92mtldr\033[0m!")
    #     print("For quick docs, run \"\033[92mtldr\033[0m \033[91m--help\033[0m\"")
    #     print(random.choice(["Good Luck!", "Happy Coding!"]))
    #     print("─" * 36)
    #     sys.exit(1)        

    script_name = sys.argv[1]

    result = subprocess.run(
        [python_cmd, script_name],
        capture_output=True,
        text=True
    )

    # Show standard output if any
    if result.stdout:
        print(result.stdout)

    # Show error and TL;DR if there's an error
    if result.stderr:
        tldredString, errorType, lineNum = simple_tldr(result.stderr)
        overhang = 3

        # if len(sys.argv) == 3:
        #     if sys.argv[2] == "--autofix":
        #         autofix(True)
        #         return
        if len(sys.argv) == 3:
            if sys.argv[2] == "--autofix":
                autofix(errorType, lineNum)
                return

        print("❌ Hold up, there's an error: ❌\n")
        print(result.stderr)
        print("\n" + "─" * (len(tldredString) + overhang))
        print("🧠 TL;DR:")
        print(tldredString)
        print("─" * (len(tldredString) + overhang))
        
        #if milestone
        usedCount = increment_usage()
        if (usedCount in milestones):
            if (usedCount == 1):
                print(f"🎉 \033[92mMilestone!\033[0m This is your first time using tldr, thanks! 🎉")
            else:
                print(f"🎉 \033[92mMilestone!\033[0m You've used TLDR {usedCount} times!")

if __name__ == "__main__":
    main()
