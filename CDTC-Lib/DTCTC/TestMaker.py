import pandas as pd
import math

import os

def MakeTest(features, compile = False, name = "PDTCTC", path = ""):
    """Creates a test program linked with a provided C DTC model and header. 
    Raises an exception if related C and header files representing the DTC model 
    cannot be found or if arguments are not the correct type.
     
    Parameters
    ----------
    features: List
        List of features that the model is trained on, these are passed in as 
        arguments for the C file.

    compile: bool
        A boolean to set if you want the function to try and compile using GCC once 
        code is generated.

    name: str, default = "PDTCTC"
        Name of the generated C and header files created through the function. If none
        is provided will default to PDTCTC.

    path: str, default = ""
        File path for C and header files to be generated in. If none is provided will 
        generate code in current directory.
    """

    if not type(path) is str:
        raise TypeError("path must be a String.")
    if not type(name) is str:
        raise TypeError("name must be a String.")
    if not type(compile) is bool:
        raise TypeError("compile must be a boolean.")
    if path != "":
        if not os.path.exists(path +"/"+name+".c"):
            raise OSError("Related C file cannot be found.")
        if not os.path.exists(path +"/"+name+".h"):
            raise OSError("Related header file cannot be found.")
    else:
        if not os.path.exists(name+".c"):
            raise OSError("Related C file cannot be found.")
        if not os.path.exists(name+".h"):
            raise OSError("Related header file cannot be found.")

    #Very long string that is the entire C test file with the appropriate data for the model.
    #Places while mostly static varies areas need to be adjusted to include the model generated alongside this code.
    c_output = """#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include \""""+ name +""".h\"

//Takes in a line and a double array. Populates array with values in line.
void parseCsvLine(char* line, double* data){
    int i = 0;
    char* buffer;
    while(strcmp(line, "") != 0){
        data[i] = strtod(line, &buffer);
        line = buffer;
        if(strcmp(line, "") != 0)
            line++;
        i++;
    }

}

double testModel(FILE* dataset){
    char chunk[128];
    double lineData[""" + str(len(features) + 1) + """];
    int actual, predict;
    long correct = 0, wrong = 0;
    long total = 0;
    double acc;
    double avgAc =0.0;
    double avgTime = 0.0;

    fgets(chunk, sizeof(chunk), dataset);   //Skips first line with labels.

    while(fgets(chunk, sizeof(chunk), dataset) != NULL){
        parseCsvLine(chunk, &lineData);
        actual = lineData[""" + str(len(features)) + """];
        
        //Apply scaling to data and then run prediction.
        predict = DTC_Predict("""

    #Sets up args for predict function for how many features there are.
    for i in range(len(features)):
        c_output += "lineData[" + str(i) + "]"
        if i != len(features) - 1:
            c_output +=", "
    
    c_output +=""");
        
        if(predict == actual){
            correct++;
        }

        total++;
    }
    avgAc += (double)(correct) / (double)(total);
    return avgAc;
}

double testModelLimited(FILE* dataset, long num_lines){
    char chunk[128];
    double lineData[""" + str(len(features) + 1) + """];
    int actual, predict;
    long correct = 0, wrong = 0;
    long total = 0;
    double acc;
    double avgAc =0.0;
    double avgTime = 0.0;

    while(fgets(chunk, sizeof(chunk), dataset) != NULL && total < num_lines){
        parseCsvLine(chunk, &lineData);
        actual = lineData[""" + str(len(features)) + """];
        
        //Apply scaling to data and then run prediction.
        predict = DTC_Predict("""
    
    #Sets up args for predict function for how many features there are.
    for i in range(len(features)):
        c_output += "lineData[" + str(i) + "]"
        if i != len(features) - 1:
            c_output +=", "

    c_output +=""");
        
        if(predict == actual){
            correct++;
        }

        total++;
    }
    avgAc += (double)(correct) / (double)(total);
    return avgAc;
}

int main(int argc, char* argv[]){

    //Display ussage information if not enough args were specified.
    if(argc < 2 || argc > 3){
        printf("Ussage: ./Model_Tester [dataset] (num_lines)\\n[] - mandatory () - optional\\n* dataset    - CSV file containing metrics to test model on.\\n* num_lines  - Number of lines in the dataset to iterate over as a long. If greater than total length will stop at end of file.\\nNOTE - Tester assumes following format for data in the CSV, if not in this format will not behave as expected:\\n\\t"""
    
    #Display features in order they should appear in csv for help menu.
    for i in range(len(features)):
        c_output += "["+features[i] +"] "

    c_output += """[actual_value]\\n");
        return 1;
    }
    char* location = argv[1];
    FILE *dataset = fopen(location, "r");
    if(dataset == NULL){
        printf("ERROR: FILE CAN NOT BE ACCESSED!\\n");
        return -1;
    }

    double acc;
    if(argc == 2){
        acc = testModel(dataset);
    }
    else{
        char *ptr;
        long num_lines = strtol(argv[2], &ptr, 10);
        acc = testModelLimited(dataset, num_lines);
    }


    fclose(dataset);

    printf("Total accuracy:  %lf\\n", acc);

    return 0;
}"""
    c_file = None
    #Check if a path for the file to be created was specified and then create file in appropriate location.
    if path != "":
        if not os.path.exists(path):
            os.makedirs(path)
        c_file = open(path +"/"+name+"_Tester.c", "w")
    else:
        c_file = open(name+"_Tester.c", "w")
    c_file.write(c_output)
    c_file.close()

    #Check if the user wants to compile the program or not.
    if compile:
        #Compile tester from generated code. Source for tester will remain if gcc is not installed.
        if path != "":
            os.system("gcc -o "+path +"/"+name+"_Tester "+path +"/"+name+"_Tester.c "+path +"/"+name+".c -w -std=c99")
        else:
            os.system("gcc -o "+name+"_Tester "+name+"_Tester.c "+name+".c -w -std=c99")
