#################################################
This is the readme file for Project 1 of CSE 601 
By--- Suramrit Singh and Vaibhav Sinha
UbIds: 50169918				50169669	
#################################################



##################### OVERVIEW ########################

The Submission consisists of 3 Parts:

1. BioStar.sql--contains the entire schema designed and implemented in this projected 

2. Cherrypy_Interface.py--This is the main interface used for implementing the sample queries as well as querying the schema for new results. 

3. Report.pdf-- Report for the sample queries results and time complexity analysis of their running times with additional background information. 


#######################LOADING THE DATA#####################

The entire data schema along with the data enteries can be loaded to any standard database server using the 'BioStar.sql' file. Once this has been done, we are ready to implement the cherrypy interface for the project.

########################Python Libraries####################

In order for the cherrypy interface to work. We need to make sure that certain standard python libraries are installed. These are::

1. cherrypy         ---	for the web interface
2. mysql.connector  --- connecting to the database 
3. pandas           --- extracting and handling the tables
4. numpy            --- for standard mathematical operations
5. scipy.stats      --- for statistical analysis like ANOVA, T-Stats, F-Stats
6. sys              --- standard
7. pandasql         --- for SQL like querying on the pandas dataframe


############### Running the Cherrypy_Interace.py Interface ############

0. Please ensure that all the dependant libraries are installed in the system

1. In line 27, change password = '' to your DataBase servers password and host = '' to your DataBase server host location. (127.0.0.1 by default) 

2. On the terminal enter 'python3 Cherrypy_Interface.py' to start the cherrypy instance

3.Once the server is running. Go to you host as specified in '1' to start using the interface

##################### Using the Interface ################

The interface is designed in an intuitive way.
For the project description sample queries, Buttons 1 through 7 list the various results with the option of choosing additional parameters as per the query requirements

We have also added additional feature of doing SQL queries on the results of the sample queries. 

If the result consist of a single table, queries should be of the form: 

Select --- from `data`

else they need to be of form Select --- from `data1`,`data2` depending on the index of the table being queried. 

The custom queries are also self explanatory with the option of doing any valid SQL query over the schema or using the intrface to build custom queires for T-Statistics, F-Statistics, Correlation and Classifications. 