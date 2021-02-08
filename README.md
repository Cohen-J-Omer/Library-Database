# Library-Database
University Project on the topic of Databases    

### Dependencies and Requirements:
1. MySQL - SQL queries are written in MySQL syntax.
2. Add MySQL path to environment variable "PATH" (by default bin folder is installed at "C:\Program Files\MySQL\MySQL Shell 8.0\bin\") - to utilize built in commands: "mysqldump" and "mysql" through cmd seamlessly. 
3. Create a new MySQL database, which the project's schema will populate.
4. Currently supporting books from the "Gutenberg Project" exclusively (https://www.gutenberg.org/ebooks/bookshelf/) - bountiful resource for copy-rights expired e-books. 

### Project Description:
A desktop application that allows users to manage a database, using books from the "Gutenberg Project".

### Topics Covered:
1. Python.
2. PyQt5 GUI library. 
3. MySQL integration & communication using MySQL Python connector. 

### Emphases & Priorities:
* Utilizing database as efficiently as possible by: 
  * Using cache to retrive word_id's - primary key of an entity located at the core of the database (described below).  
  * Aggregating queries to be carried out by the database once a (predetermined size) buffer is filled, rather then individually. 
* Adhere to possible RAM volume limitations - to read (see import functionallity below) possibly large JSON files into the database, a spcialized library is used to parse the file iteratively.    


### Functionality: 

1. Maintains a consistant database that grows/shrinks efficiently as the user adds/removes books to/from the database. 
2. Scans efficiently for custom built groups of words / phrases throughout books in the database. 
3. Enables user to use multiple filters to research patterns, e.g. scanning the database for all the occurences of pre-selected group of ominous words within the the 10th paragraph, at the beggining of lines, from all detective books within the database. 
4. Export database to either an SQL,JSON or Excel format. 
5. Import database previously saved using the aforementioned utility. 

### Database Structure:
<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/Entity%E2%80%93relationship%20model.png" width="600" height="500" />

### Preview Of The App's Tabs:

#### Login Screen to connect to the user's MySQL database:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/login.png" width="500" height="400" />

#### Book Tab - loads and removes books from the database:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/books_tab.png" width="700" height="500" />

#### Menu - exports/imports/clears the database:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/menu.png" width="700" height="500" />

#### Word Tab - runs queries on selected word / group of words, while and displayes their context:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/word_tab.png" width="700" height="500" />

#### Group Tab - creates groups of words for later look-ups in the "Word Tab":

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/group_tab.png" width="700" height="500" />

#### Phrase Tab - creates phrases to look up in the database:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/phrase_tab.png" width="700" height="500" />

#### Statistics Tab - displayes simple statistics regarding the current books in the database:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/stats_tab.png" width="700" height="500" />

