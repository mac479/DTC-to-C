import pandas as pd
import math
from sklearn.tree import DecisionTreeClassifier # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split # Import train_test_split function
from sklearn import metrics #Import scikit-learn metrics module for accuracy calculation

from pickle import load
import os
import numpy as np


def DTCTC(model, scaler, features, name = "PDTCTC", path = ""):
    """Basic generation function taking in related information on the model and 
    transforming it into if and goto statements for C to use. Raises exception if 
    arguments are not the correct type.
     
    Parameters
    ----------
    model : SKLearn.tree.DecisionTreeClassifier
        SKLearn DTC model to be converted to C.
        
    scaler: List
        List of scaling data that data is transformed according to at runtime.

    features: List
        List of features that the model is trained on, these are passed in as 
        arguments for the C file.

    name: str, default = "PDTCTC"
        Name of the generated C and header files created through the function. If none
        is provided will default to PDTCTC.

    path: str, default = ""
        File path for C and header files to be generated in. If none is provided will 
        generate code in current directory.
    """

    if not type(model) is DecisionTreeClassifier:
        raise TypeError("Invalid DTC model passed as argument.")
    if not type(name) is str:
        raise TypeError("name must be a String.")
    if not type(path) is str:
        raise TypeError("path must be a String.")

    if path != "":
        if not os.path.exists(path):
            os.makedirs(path)
    
    # Load models 
    clf = model
    scale = scaler

    # Assign variables
    n_nodes = clf.tree_.node_count
    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    feature = clf.tree_.feature
    threshold = clf.tree_.threshold
    value = clf.tree_.value
    
    # Parse through the Decision Tree
    node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
    is_leaves = np.zeros(shape=n_nodes, dtype=bool)
    stack = [(0, -1)]  # seed is the root node id and its parent depth
    while len(stack) > 0:
        node_id, parent_depth = stack.pop()
        node_depth[node_id] = parent_depth + 1

        # If we have a test node
        if (children_left[node_id] != children_right[node_id]):
            stack.append((children_left[node_id], parent_depth + 1))
            stack.append((children_right[node_id], parent_depth + 1))
        else:
           is_leaves[node_id] = True

    # Create header file first.
    header = """#ifndef """+name+"""_H
#define """+name+"""_H

//Sclaes data and makes a prediction based off a DTC model using if and goto statements.
int DTC_Predict("""
    arguments = ""
    for i in range(len(features)):
        arguments += "double "+features[i]
        if i != (len(features) - 1):
            arguments += ", "
    header += arguments + """);

#endif"""
    header_file = None
    if path != "":
        header_file = open(path + "/"+name+".h", "w")
    else:
        header_file = open(name+".h", "w")
    header_file.write(header)
    header_file.close()

    # Setup string to write to c file
    c_output = """#include \""""+name+""".h"

//Sclaes data and makes a prediction based off a DTC model using if and goto statements.
int DTC_Predict("""+arguments+"""){

    //Scale the arguments acording to preset mean and standard deviation 
"""

    for i in range(len(features)):
        c_output+= "%s%s%s%s%s%s%s%s%s" % ("\t", features[i], " = (", features[i], " - ",scale.mean_[i], ") / ", scale.scale_[i], ";\n")
    
    c_output+= """

    //Actual DTC converted into if and goto statements. Will return predicted value based on scaled arguments.
"""

    # Generate GOTO statements
    for i in range(n_nodes):
        if is_leaves[i]:
            the_value = value[i]
            the_label = clf.classes_[np.argmax(the_value)]
            c_output += "\tNODE_"+str(i)+":\n"
            # c_output += "\treturn "+"\""+the_label+"\";\n"
            c_output += "%s%s%s" % ("\treturn ",the_label, ";\n")

        else:
            feat_name = str(features[feature[i]])
            c_output += "\tNODE_"+str(i)+":\n"
            # c_output += "\tif ("+feat_name+" <= "+math.floor(threshold[i])+") {\n"
            c_output += "%s%s%s%s%s" % ("\tif (", feat_name, " <= (double)(", threshold[i], ")) {\n")
            c_output += "\t\tgoto NODE_"+str(children_left[i])+";\n"
            c_output += "\t} else {\n"
            c_output += "\t\t goto NODE_"+str(children_right[i])+";\n"
            c_output += "\t}\n"
        
    c_output += "}"
    
    c_file = None
    if path != "":
        c_file = open(path +"/"+name+".c", "w")
    else:
        c_file = open(name+".c", "w")
    c_file.write(c_output)
    c_file.close()

#Will import data from a PKL file and then run the above function to convert it into a DTC
def DTCTC_FromPKL(model, scaler, features, name = "PDTCTC", path = ""):
    """
    Identical to `DTCTC` but model and scaler are passed in as PKL files. Taking in 
    related information on the model and transforming it into if and goto statements 
    for C to use. Raises an exception if files containing DTC model and scaling data 
    cannot be found or if arguments are not the correct type.
     
    Parameters
    ----------
    model : str
        Location of PKL file containing SKLearn DTC model to be converted to C.

    scaler: str
        Location of PKL file containing list of scaling data that data is transformed
        according to at runtime.

    features: List
        List of features that the model is trained on, these are passed in as 
        arguments for the C file.

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
    if not os.path.exists(model):
        raise OSError("Model PKL could not be found.")
    if not os.path.exists(scaler):
        raise OSError("Model scaler could not be found.")

    # Load models 
    clf = load(open(model, "rb"))
    scale = load(open(scaler, "rb"))
    #Run generation function
    DTCTC(clf, scale, features, name, path)
