""" This file holds information and constants regarding the schema """

TABLES = ['book', 'word', 'word_instance', 'phrase', 'word_in_phrase', 'group_of_words', 'word_in_group']

TBL_WORD = """CREATE TABLE IF NOT EXISTS word
            (word_id int(10) PRIMARY KEY AUTO_INCREMENT ,word_txt VARCHAR(40) NOT NULL UNIQUE)"""

TBL_BOOK = """ CREATE TABLE IF NOT EXISTS book
            (book_id int(10) PRIMARY KEY AUTO_INCREMENT ,title VARCHAR(40), author VARCHAR(40), date VARCHAR(20), 
            size VARCHAR(20), path VARCHAR(150), UNIQUE(title, author)) """

TBL_WORD_INSTANCE = """CREATE TABLE IF NOT EXISTS word_instance 
        (word_id int(10), word_serial int(10), book_id int(10), 
        sentence_serial int(10), line_serial int(10),line_offset int(10), paragraph_serial int(10),
        CONSTRAINT fk_book_id FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE,
        CONSTRAINT fk_word_id FOREIGN KEY (word_id) REFERENCES word(word_id) ON DELETE CASCADE,
        CONSTRAINT PK_word PRIMARY KEY (word_serial,book_id),
        INDEX idx_sentence (sentence_serial)) """  # indexing sentence to accelerate phrase query

TBL_GROUP_OF_WORDS = """ CREATE TABLE IF NOT EXISTS group_of_words 
        (group_id int(10) PRIMARY KEY AUTO_INCREMENT,group_name VARCHAR(30) NOT NULL UNIQUE)"""

TBL_WORD_IN_GROUP = """ CREATE TABLE IF NOT EXISTS word_in_group 
        (word_id int(10), group_id int(10),
        CONSTRAINT fk_word_id2 FOREIGN KEY (word_id) REFERENCES word(word_id) ON DELETE CASCADE,
        CONSTRAINT fk_group_id FOREIGN KEY (group_id) REFERENCES group_of_words(group_id) ON DELETE CASCADE,
        CONSTRAINT PK_group_word PRIMARY KEY (word_id,group_id)
        ) """

TBL_PHRASE = """CREATE TABLE IF NOT EXISTS phrase      
          (phrase_id int(10) PRIMARY KEY AUTO_INCREMENT, phrase_txt VARCHAR(250) NOT NULL UNIQUE)"""

TBL_WORD_IN_PHRASE = """ CREATE TABLE IF NOT EXISTS word_in_phrase
           (word_id int(10), phrase_id int(10), offset int(10),
           CONSTRAINT fk_word_id3 FOREIGN KEY (word_id) REFERENCES word(word_id) ON DELETE CASCADE,
           CONSTRAINT fk_phrase_id FOREIGN KEY (phrase_id) REFERENCES phrase(phrase_id) ON DELETE CASCADE,
           CONSTRAINT PK_phrase_word PRIMARY KEY (word_id,phrase_id,offset) )"""

TABLE_QUERIES = [TBL_WORD, TBL_BOOK, TBL_WORD_INSTANCE, TBL_GROUP_OF_WORDS, TBL_WORD_IN_GROUP, TBL_PHRASE,
                 TBL_WORD_IN_PHRASE]

