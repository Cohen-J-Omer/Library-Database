# Library-Database
University Project on the topic of Databases    

### Dependencies and Requirements:
1. MySQL - SQL queries are written in MySQL syntax.
2. Add MySQL path to environment variable "PATH" (by default bin folder is installed at "C:\Program Files\MySQL\MySQL Shell 8.0\bin\") - to utilize built in commands: "mysqldump" and "mysql" through cmd seamlessly. 
3. Create a database by the name: "testdatabase", which the project's schema will populate.

### Project Description:
A desktop application that allows users to manage a database, using books from the "Gutenberg Project": https://www.gutenberg.org/ebooks/bookshelf/.

### New Topics Covered:
1. Python.
2. PyQt5 GUI library. 
3. MySQL integration & communication using MySQL Python connector. 

#### Functionality: 

1. Maintains a consistant database that grows/shrinks efficiently as the user adds/removes books to/from the database. 
2. Scans efficiently for custom built groups of words / phrases throughout books in the database. 
3. Enables user to use multiple filters to research patterns, e.g. scanning the database for all the occurences of pre-selected group of ominous words within the the 10th paragraph, at the beggining of lines, from all detective books within the database. 
4. Export database to either an SQL/Json/Excel format. 
5. Import database previously saved using the aforementioned utility. 

#### Database Structure:
<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/Entity%E2%80%93relationship%20model.png" width="600" height="500" />

#### Preview Of The App's Tabs:

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/books_tab.png" width="700" height="500" />

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/menu.png" width="700" height="500" />

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/word_tab.png" width="700" height="500" />

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/group_tab.png" width="700" height="500" />

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/phrase_tab.png" width="700" height="500" />

<img src="https://github.com/Cohen-J-Omer/Library-Database/blob/main/images/Screenshots/stats_tab.png" width="700" height="500" />

