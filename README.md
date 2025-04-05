This code was born from a csv file of ~30,000 URLs needing to be checked for data. Unfortunately, even if the URL does contain data, it still displays a valid web browser and displays the message "The Graded Stakes Profile you were searching for could not be found" (rather than the URL simply not working/loading as is usually the case when there is nothing displayed on a webpage). 

The code iterates through each URL in my master URL csv file, looks for the error message "The Graded Stakes Profile you were searching for could not be found" in the webpage HTML, and then saves the outcome to the corresponding URL in a csv file, with "yes" to indicate there is data on the webpage (in which case we would investigate the URL further to identify the information we are looking for), or "no" to indicate there is no data on the webpage (i.e., the code detected the error message "The Graded Stakes Profile you were searching for could not be found" in the webpage HTML - in which case we discard this URL as it is of no use to us). 



The files: 
Equibase_URLS.csv --> the master csv file containing approx. 30,000 URLs i'd like to check for data 

generate_cookies.py --> generates cookies from a user session 

test_cookies.py --> tests these cookies to ensure the URL checker can use these cookies to pass as a human (rather than detected by the webpages security as a bot and block us) 

url_checker_HEADLESS.py --> iterates through the 30k URL's and returns "yes/no" in the csv file for further analysis. 

The result: 
![image](https://github.com/user-attachments/assets/06ebc592-17df-4e43-8382-d783e558d269)
