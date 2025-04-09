# House Splitter
The purpose of this project is to aid decision-making required to split a group into houses.

----
## How to use
Gather data using Google Forms in the layout below:
\
![Image1.png](Image1.png)
**Make sure to use required questions and use a checkbox to allow multiple options to be picked**
\
\
Once all results have been collected, extract the data from the ***Responses*** tab, and click on ***View in Sheets***.
Export this Google Sheet into a **.csv** file, you do not need to change anything in the table. \
Move this **.csv** file into the same folder as this code. Replace the example **.csv** file, and make sure the **.csv** file is labelled **House Split (Responses).csv**. If you do not want this name, or you wish to keep the file elsewhere you will need to go into the **house-picker.py** file and change this line
`run = HousePicker(csv_filepath="House Split (Responses).csv")` to the appropriate filepath.
Then run **house-picker.py**. This will generate the network graph (a.k.a. the sociogram). 


#### Example output
![Image2.png](Image2.png)
