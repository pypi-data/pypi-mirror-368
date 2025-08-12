lex_file = """

import sys

#after making tokens the final list had some empty space idk why. So this funtion right hear fix that problem



def clean(empty): 
    
    while "" in empty: 
        blank = empty.index("")
        empty.pop(blank)
    while " " in empty:
        blank2 = empty.index(" ")
        empty.pop(blank2)
    
    
    return empty # it returns the clean list of tokens after removing all space and empty items



# main funtion to make tokens 
def tokeniztion(instrection):
    str = ""
    tokens = []
    for code in instrection:

        
        if code.isalnum(): #read if it's start with alhpa or number

            
            str = str+code # store it in a buffer called str


       
        elif code == " ":  # this block is included to solve an issue of space in string like "hello wrold" not "helloworld" 
            
            str = str + code #keep reading even if it's space



        elif code == '(': # stop reading and append whatever stored in buffer and than empty the buffer for next 

            tokens.append(str)
            str = ""
            tokens.append("(")#this append is for future refreance for code gen part to know if the syntex is right or not


        elif code == "{":
            tokens.append(str)
            str = ""
            tokens.append("{")



        elif code == '"':
            
            tokens.append(str)
            str = ""
            tokens.append('"') #future refreance
            # str = str+code



        elif code == ")":
            tokens.append(str)
            str = ""
            tokens.append(")")#future refreance

        elif code == "}":
            tokens.append(str)
            str = ""
            tokens.append("}")



        elif code == "=":
            tokens.append(str)
            str = ""
            tokens.append("=")# future refreance
        


        elif code == ";": # i was having an problem for tokenizing for variable creation for int like idk why so i added ";" 
             tokens.append(str)
             str = ""

        else:
            print("error:", code)
            exit()

        

    return clean(tokens)



if __name__ == "__main__":
    with open(sys.argv[1],"r") as file:
        data = file.readlines()

    list_of_instraction = []
    for code in data:
        if code.isspace():
            continue
        elif "#" in code:#for adding comments in skylang use "#" same as python 
            continue
        else:
            list_of_instraction.append(code.split("\\n")[0])

    for line in list_of_instraction:
        new_token_list = tokeniztion(line)
        new_token_list[0] = new_token_list[0].strip()
        print(new_token_list)


"""




def hello():
    print("hello my name is prateek and i love python")


def make(file_name):
    if file_name == "lex.py":
        with open("lex.py","w") as file:
            file.write(lex_file)
        




make("lex.py")