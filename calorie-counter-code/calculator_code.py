##import libraries
import caloriecalculator.ocrtools as ocrtools
import caloriecalculator.fooddictionary as fooddict
import caloriecalculator.parseandlabel as pnl
import caloriecalculator.queries

from pathlib import Path
#for file explorer box
import tkinter as tk
from tkinter import filedialog

#ignore search warning
import warnings
import os

import os.path
 
# function to get parent
JSON_File = "processedFood.json" # Add the files in creating-json-file

path = os.getcwd()
d = Path(path).resolve().parents[0]
JSON_File = str(d) + '/creating-json-file/'+JSON_File



def demoPrint(string, isDemo):
    if isDemo:
        print(string)
        input("Enter to continue...")


###Queries and Searching
def main():
    isDemo = False
    #Select picture
    root = tk.Tk()
    root.withdraw()

    document = filedialog.askopenfilename()

    demoPrint("#####BEGIN OCR#####", isDemo)
#### OCR a single image- commented out to save on AWS charges for debugging
    #document = 'recipes/berrymuffins.png'
    text_recipe = ocrtools.process_text_detection_to_string(document, "")
    print(text_recipe)

####NER Model to Extract Ingredients

    demoPrint("#####BERT LABELLING#####", isDemo)
    #BERT labelling, and data cleanup
    comb_tokens, comb_labels = pnl.parseandlabel(text_recipe)
    #Grouping together Quantities/Units/Ingredients into queries
    demoPrint("#####GROUPING LABELS INTO QUERY SETS#####", isDemo)
    queries = caloriecalculator.queries.createQueries(comb_tokens, comb_labels)
    for q in queries:
        print(q)
    #Create food dictionary object with data from JSON. Object has ability to do search
    demoPrint("#####LOAD FOOD DATABASE AND WEIGHTS#####", isDemo)
    fd = fooddict.createFoodDictionary(JSON_File, "models/food2vec.model")
    #Run queries through search
    demoPrint("#####SEARCH AND SUM CALORIES#####", isDemo)
    caloriecount_carb = 0
    caloriecount_protein = 0
    caloriecount_fat = 0
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for q in queries:
            if q.ing != "" and q.qty != "" and q.unit != "":
                print(q)
                cal_ing_carb,cal_ing_protein,cal_ing_fat = fd.calculateIngredient(q.ing, q.qty, q.unit)
                if cal_ing_carb != "No results found":
                    caloriecount_carb += cal_ing_carb
                if cal_ing_protein != "No results found":
                    caloriecount_protein += cal_ing_protein
                if cal_ing_fat != "No results found":
                    caloriecount_fat += cal_ing_fat
    print("Total Carbs: {}".format(caloriecount_carb))
    print("Total protein: {}".format(caloriecount_protein))
    print("Total fat: {}".format(caloriecount_fat))
    servings = int(input("How many servings is this recipe? "))
    print("Carbs per serving: {}".format(caloriecount_carb/servings))
    print("Protein per serving: {}".format(caloriecount_protein/servings))
    print("Fat per serving: {}".format(caloriecount_fat/servings))

##Execute main
if __name__ == "__main__":
    main()
