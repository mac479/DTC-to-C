# DTC to C

A small library containing functions to convert a python DTC made from SKLearn to executable C code as well as create a small test executable to iterate over the created model. 

To use it first generate a SKLearn DTC model then pass it and the related arguments to the Converter functions. This creates a small C file and header that functions as the DTC model to be imported into other code. From that, by passing in arguments similar to what was passed into the Converter functions, TestMaker can create and compile if set to an executable to test the created C DTC model with data stored in a CSV.

---

## Example Usage

A brief explanation on how to possibly utilize this library.

1. Create a SKLearn DTC model and pass it into `DTCTC` or load a model from a PKL file with `DTCTC_FromPKL` along with the features the model was trained off. This creates C and header files that represent the DTC model to be imported into a C program. For this example, assume that the function was called with `name` set to `"Example_Model"`.
2. From this two new files appear called `"Example_Model.c"` and `"Example_Model.h"`. These represent the model passed into `DTCTC` or `DTCTC_FromPKL` in step 1. Using the same list of features and name as in step 1 call TestMaker. If the name and features do not match the function will either fail to generate code or generate broken code. For the sake of the example assume GCC is installed, and the function was called with `compile` set to `True`.
3. This creates a new C file and executable both called `"Example_Model_Tester"`. Running the program from the command line with no arguments will then show the usage information shown below.
    ```
    Ussage: ./Model_Tester [dataset] (num_lines)
    [] - mandatory. () - optional
    * dataset    - CSV file containing only metrics to test model on.
    * num_lines  - Number of lines in the dataset to iterate over as a long. If greater than total length will stop at end of file.
    NOTE - Tester assumes following format for data in the CSV, if not in this format will not behave as expected:
            [cycles] [instr] [llc_accesses] [llc_misses] [bus_accesses] [actual_value]
    ```
4. Running the program again with the an example dataset called `"Example_test.csv"` will then have the program run iterating over each line in the CSV passing the data in it as arguments to `DTC_Predict` in `"Example_Model.c"` before returning a predicted value. After iterating over every line in the CSV it prints the percentage the model managed to correctly predict. 

---

## Modules

### Converter

Converts python DTC to if and goto statements then writes them to a C file with a matching header file. The DTC C file takes in the DTC features as arguments, applies scaling data, and then returns a prediction. 

##### Functions

-  DTCTC
    > `DTCTC(model, scaler, features, name = "PDTCTC", path = "")`

    Basic generation function taking in related information on the model and transforming it into if and goto statements for C to use. Raises exception if arguments are not the correct type.
    
    | Parameters | Type | Description |
    | --- | --- | --- |
    | model | SKLearn.tree.DecisionTreeClassifier | SKLearn DTC model to be converted to C. |
    | scaler | List | List of scaling data that data is transformed according to at runtime. |
    | features | List | List of features that the model is trained on, these are passed in as arguments for the C file. |
    | name | str | Name of the generated C and header files created through the function. If none is provided will default to PDTCTC. |
    | path | str | File path for C and header files to be generated in. If none is provided will generate code in current directory. |

-  DTCTC_FromPKL
    > `DTCTC_FromPKL(model, scaler, features, name = "PDTCTC", path = "")`

    Identical to `DTCTC` but model and scaler are passed in as PKL files. Taking in related information on the model and transforming it into if and goto statements for C to use. Raises an exception if files containing DTC model and scaling data cannot be found or if arguments are not the correct type.
    
    | Parameters | Type | Description |
    | --- | --- | --- |
    | model | str | Location of PKL file containing SKLearn DTC model to be converted to C. |
    | scaler | str | Location of PKL file containing list of scaling data that data is transformed according to at runtime. |
    | features | List | List of features that the model is trained on, these are passed in as arguments for the C file. |
    | name | str | Name of the generated C and header files created through the function. If none is provided will default to PDTCTC. |
    | path | str | File path for C and header files to be generated in. If none is provided will generate code in current directory. |

### TestMaker

Generates a test program to execute the generated C file. The test program is designed to take in similar data to what the C model was created on and fit it to a template program that will then be created as a C file. Assuming GCC is installed the function can be set to compile the created code as well. The test program only uses standard C libraries. Test program takes in a csv file to iterate over as an argument for testing data, number of lines to iterate over can also be taken as an argument but is not required. If 0 or more than 2 arguments are passed in the program displays usage information.

##### Functions

-  MakeTest
    > ```MakeTest(features, compile = False, name = "PDTCTC", path = "")```

    Creates a test program linked with a provided C DTC model and header. Raises an exception if related C and header files representing the DTC model cannot be found or if arguments are not the correct type.

    | Parameters | Type | Description |
    | --- | --- | --- |
    | features | List | List of features that the model was trained on, these are passed in as arguments for the C file. |
    | compile | bool | A boolean to set if you want the function to try and compile using GCC once code is generated. |
    | name | str | Name of the generated C and header files created through the `DTCTC` function. If none is provided will default to PDTCTC. |
    | path | str | File path for C and header files made using `DTCTC` to be generated in. If none is provided will generate code in current directory. |
    
