import functools
import mysql.connector
from database.schema import TABLES, TABLE_QUERIES


class Database:
    def __init__(self, credentials):
        self.credentials = credentials  # for OS commands in menu_actions (import/export using mysqldump/mysql)
        self.connection = mysql.connector.connect(**credentials)
        self.cursor = self.connection.cursor(prepared=True)  # to run parameterized queries
        self.update_on_new_book = []
        self.update_on_import = []
        self.update_stats = []
        self.init_schema()

    def init_schema(self):
        """Creates Schema tables unless already created."""
        for query in TABLE_QUERIES:
            self.cursor.execute(query)
        self.connection.commit()

    def reset_db(self, clear_widgets=False):
        """Clears DB's records by dropping the tables and creating them from the schema.
            this process replaces 'delete' operation slow performance due to record logging. """

        # tables are cleared in reversed order due to dependent foreign keys
        for table in list(reversed(TABLES)):
            self.cursor.execute(f"""DROP TABLE {table} """)
        self.connection.commit()
        self.clear_cache()
        self.init_schema()
        if clear_widgets:  # activating import functions from other tabs will clear widgets, since input is now None
            self.notify_import()  # piggybacking on import's functions to clear widgets

    def tune_in_new_book(self, update_func):
        self.update_on_new_book.append(update_func)

    def tune_in_import(self, update_func):
        self.update_on_import.append(update_func)

    def tune_in_stats(self, update_func):
        """stats subscribes to get notified on updates to phrases and groups count"""
        self.update_stats.append(update_func)

    def notify_new_book(self):
        """notifies tabs that an import has occurred, by calling functions that have tuned_in
        called solely by "insert_book" of books_tab"""
        for update_func in self.update_on_new_book:
            update_func()

    def notify_import(self):
        """notifies all (tuned_in) tabs that an import has occurred, by calling their tuned_in functions """
        for update_func in self.update_on_import:
            update_func()

    def notify_stats(self):
        """notify stats_tab's functions that a new group/phrase has been added.
            the rest of the stats in stats_tab are updated from notify_book / notify_import"""
        for update_func in self.update_stats:
            update_func()

    def insert_book(self, args):
        """inserts new book to db. if fails (mostly due to duplicate val) returns False,
            otherwise returns last ID of added book. """
        try:
            if len(args) == 6:  # used when importing existing database.
                self.cursor.execute("INSERT INTO book (book_id,title,author,date,size,path) VALUES "
                                    "(%s,%s,%s,%s,%s,%s)", args)
            else:
                self.cursor.execute("INSERT INTO book (title,author,date,size,path) VALUES "
                                    "(%s,%s,%s,%s,%s)", args)
            self.connection.commit()
        except mysql.connector.Error:  # duplicate entry
            return False
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        return self.cursor.fetchone()  # returns last book_id inserted

    def query_book_table(self, title, author):
        """:returns all columns of table book, filtered by user choice of author and title."""
        query = "select * from book where (%s = 'ALL' or title = %s) and (%s = 'ALL' or author = %s)"
        args = (title, title, author, author)
        self.cursor.execute(query, args)
        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield row

    def get_book_titles_authors(self):
        """returns all titles and authors in DB. """
        self.cursor.execute("SELECT title,author FROM book")
        while True:
            title = self.cursor.fetchone()
            if not title:
                break
            yield title

    def get_book_authors(self, title):
        """returns all authors that matches provided title in DB. """
        self.cursor.execute("SELECT author FROM book where (%s = 'ALL' or title = %s)", (title, title))
        while True:
            title = self.cursor.fetchone()
            if not title:
                break
            yield title

    def get_book_path(self, title, author):
        """:returns file location of a book."""
        self.cursor.execute("""select path 
                               from book
                               where title = %s and author = %s """, (title, author))
        return self.cursor.fetchone()[0]

    def get_book_id(self, title, author):
        """:returns the id of a book using uniquely identifying attributes: title, author.
            used by "get_filters" in words_tab to identify user choice of a book. """
        self.cursor.execute("SELECT book_id FROM book "
                            "WHERE title = %s and author = %s", (title, author))
        return self.cursor.fetchone()

    def get_last_book(self):
        """ :returns book id of latest book inserted"""
        self.cursor.execute("""select max(book_id) FROM book""")
        return self.cursor.fetchone()[0]

    def del_book(self, title, author):
        """removes selected book including all rows related to said book within foreign tables """
        book_id = self.get_book_id(title, author)[0]

        # delete all words unique to given book
        self.cursor.execute("""DELETE 
                                FROM word 
                                WHERE word_id in (SELECT DISTINCT word_id
                                                    FROM word_instance
                                                    WHERE word_id in (SELECT word_id 
                                                                      FROM word_instance
                                                                      WHERE book_id = %s)
                                                    GROUP BY word_id
                                                    HAVING COUNT(DISTINCT book_id) = 1)""", (book_id,))

        # remove book alongside with every word_instance by utilizing on delete cascade within the schema
        self.cursor.execute("""DELETE FROM book
                             WHERE book_id = %s  """, (book_id,))
        self.connection.commit()
        self.clear_cache()

    @functools.lru_cache(maxsize=pow(2, 13))
    def get_word_id(self, word):
        """:returns word_id of given word in the DB.
            Using a built-in cache to expedite retrieval of word_ids."""

        self.cursor.execute("SELECT word_id FROM word WHERE word_txt = %s", (word,))
        return self.cursor.fetchone()

    def clear_cache(self):
        self.get_word_id.cache_clear()

    def insert_word(self, word, word_id=None):
        """ used in tabs: group and phrase to insert words foreign to the DB"""
        try:
            if word_id:
                self.cursor.execute("INSERT INTO word (word_id,word_txt) VALUE (%s,%s)", (word_id, word))
            else:
                self.cursor.execute("INSERT INTO word (word_txt) VALUE (%s)", (word,))
            self.connection.commit()
            self.cursor.execute("SELECT LAST_INSERT_ID()")
        except mysql.connector.Error as error:
            """ show error massage to user"""
            print("parameterized query failed {}".format(error))
            return False
        return self.cursor.fetchone()  # returns id of inserted word.

    def insert_mult_word_instance(self, instances):
        """Inserts a list of words' occurrences in the same commit instruction to improve performance """
        values = ', '.join(map(str, instances))
        self.cursor.execute(f"INSERT INTO word_instance VALUES {values}")
        self.connection.commit()

    def insert_mult_word(self, words, importing=False):
        """Inserts a list of words in the same commit instruction to improve performance """
        if importing:
            word_list = ', '.join(map(str, words))
            # INSERT IGNORE would be redundant since before initiating import, DB is cleared.
            self.cursor.execute(f"INSERT INTO word VALUES {word_list}")
        else:
            word_list = ', '.join(words)
            self.cursor.execute(f"INSERT IGNORE INTO word (word_txt) VALUES {word_list}")
        self.connection.commit()

    def get_wrd_res(self, filters):
        """:returns a generator of words in accordance to user's chosen filters.
            called by words_tab, after user pressed "Search" button."""
        if not filters:
            return

        query = """SELECT word_txt, count(word_instance.word_serial) as cnt
                   FROM word,word_instance """
        words_to_search, where_in = (), 'word_txt'

        if filters[2] != "None":  # user searches for words within selected group
            words_to_search = []
            for word_in_group in self.get_group_words(filters[2]):
                words_to_search.append(word_in_group[0])
            if words_to_search:  # if group isn't empty
                where_in = ','.join(['%s'] * len(words_to_search))
                query += ",word_in_group"
                filters[1] = ''  # if user chose to search a group, disregard input of word
            else:
                return  # if group is empty, so will the result set that will be displayed to user.

        if filters[1] is None and filters[2] == 'None':  # if user chose no group and chose a non-existing word
            return

        query += " WHERE word.word_id = word_instance.word_id "
        query, params = self.build_query_filter(query, filters)

        if filters[2] != 'None':
            query += f""" and (word.word_id = word_in_group.word_id)
                          and (word_txt in ({where_in})) """
            params += tuple(words_to_search)

        query += """ GROUP by word_txt 
                    ORDER BY cnt DESC"""
        self.cursor.execute(query, params)

        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield row

    def remove_word_if_redundant(self, word_id):
        """removes given word if it doesn't server a role in the database """
        # checks whether word has another role in the database
        self.cursor.execute("""select word_id  
                                from word_in_group                              
                                where word_id = %s
                                UNION 
                                select word_id  
                                from word_instance                              
                                where word_id = %s
                                UNION 
                                select word_id  
                                from word_in_phrase                              
                                where word_id = %s
                                LIMIT 1""", (word_id, word_id, word_id))
        # if the word doesn't show up in the database (aside from word table) remove it
        if not self.cursor.fetchone():
            self.cursor.execute("""delete from word
                                    where word_id = %s 
                                    """, (word_id,))
            self.connection.commit()

    def get_wrd_instances(self, filters=None):
        """:returns a generator of occurrences of a word selected by user, in accordance with
           filters chosen by user at time of search (clicked the button 'search' in words_tab). """
        if not filters:
            filters = ['All Books', '', '', '', '', '']

        query = """select title,author,paragraph_serial, sentence_serial, line_serial, line_offset  
        from word, word_instance, book                                   
        where word.word_id = word_instance.word_id and word_instance.book_id=book.book_id """

        query, params = self.build_query_filter(query, filters)
        query += " ORDER BY book.book_id"
        self.cursor.execute(query, params)

        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield row

    def build_query_filter(self, query, filters):
        """Auxiliary function that builds an SQL query in accordance to user's filters
          and keeps track of relevant parameters. Used by get_wrd_instances and get_wrd_res."""
        params = ()
        if filters[0] != 'All Books':
            query += " and word_instance.book_id = %s"
            params += (filters[0],)
        if filters[1]:
            query += " and word.word_id = %s"
            params += (filters[1],)
        if filters[3]:
            query += " and paragraph_serial = %s"
            params += (filters[3],)
        if filters[4]:
            query += " and line_serial = %s"
            params += (filters[4],)
            # if not filters[5].isspace() and not filters[5].isnumeric():  # Mysql will turn non numeric values to 0 which is a valid input
            #     return
        if filters[5]:
            query += " and line_offset = %s"
            params += (filters[5],)
        if filters[6]:
            query += " and sentence_serial = %s"
            params += (filters[6],)

        return query, params

    def get_wrd_freq(self):
        """:returns a generator of 100 most words frequent used words
           and the number of times they've appeared within the DB.
           Called by Stats_tab."""
        self.cursor.execute("""select word_txt, count(word_serial) as cnt
                                from word inner join word_instance on word.word_id = word_instance.word_id
                                group by word_txt
                                ORDER BY cnt DESC
                                LIMIT 100""")
        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield row

    def insert_group(self, group_name, group_id=None):
        """"Insert group into group_of_words in the DB.
            If user imports, groups will be supplied with a group_id, and thus will be inserted accordingly."""
        try:
            if group_id:
                self.cursor.execute("INSERT INTO group_of_words (group_id,group_name) VALUE (%s,%s)",
                                    (group_id, group_name))
            else:
                self.cursor.execute("INSERT INTO group_of_words (group_name) VALUE (%s)", (group_name,))
            self.connection.commit()
        except mysql.connector.Error as error:
            return False
        return True

    def get_groups(self):
        """:returns names of groups within the DB.
        called by words_tab to populate group selection box and by group_tab when importing/adding new book."""

        self.cursor.execute("SELECT group_name FROM group_of_words")
        while True:
            title = self.cursor.fetchone()
            if not title:
                break
            yield title

    def get_group_id(self, group_name):
        """:returns group_id of group in the DB.
        Used to identify group when user selects a group from group_tab (to later add words to it).  """

        self.cursor.execute("""select group_id from group_of_words where group_name = %s""", (group_name,))
        return self.cursor.fetchone()[0]

    def insert_word_in_group(self, word_id, group_id):
        """Inserts a word chosen by user to selected group."""
        try:
            self.cursor.execute("INSERT INTO word_in_group (word_id,group_id) VALUE (%s,%s)",
                                (word_id, group_id))
            self.connection.commit()
        except mysql.connector.Error as error:
            # display_msg(msg_icon.WARNING,"Warning","Duplicate entry: word already exists in group")
            return False
        return True

    def del_wrd_in_grp(self, group, word, id_input=False):
        """removes selected word from selected group.
           if the word doesn't serve any other purpose in the database, it will be removed entirely.
        @:param id_input determines whether the input contains the i.d's of the other parameters. """
        if id_input:
            word_id = word
            group_id = group
        else:
            word_id = self.get_word_id.__wrapped__(self, word)[0]  # bypassing cache
            group_id = self.get_group_id(group)

        # remove word from the group it used to belong to
        self.cursor.execute("""delete from word_in_group
                                where group_id = %s 
                                and word_id = %s""", (group_id, word_id))
        self.connection.commit()

        self.remove_word_if_redundant(word_id)

    def del_group(self, group):
        """removes the selected group and all words that belongs to it. """
        group_id = self.get_group_id(group)

        # get all words belonging to given group
        self.cursor.execute("""select word_id  
                                from  word_in_group                          
                                where group_id = %s""", (group_id,))
        group_words = self.cursor.fetchall()

        # disconnect words that used to belong to the selected group, from said group
        if group_words:
            for word_id in group_words:
                self.del_wrd_in_grp(group_id, word_id[0], id_input=True)

        # removes the group from the database
        self.cursor.execute("""delete from group_of_words
                                where group_id = %s """, (group_id,))
        self.connection.commit()

    def get_group_words(self, group_name):
        """:returns a generator of words that belongs to a selected group.
           Used in Group_tab to display user words within selected group. """
        self.cursor.execute("""select word_txt
                from word,word_in_group,group_of_words
                where word.word_id = word_in_group.word_id and word_in_group.group_id = group_of_words.group_id 
                and group_name = %s """, (group_name,))
        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield row

    def insert_phrase(self, phrase_txt, phrase_id=None):
        """Inserts a phrase chosen by user to the DB and returns id of inserted phrase.
         If user imports, phrase will be supplied with a phrase_id, and thus will be inserted accordingly."""
        try:
            if phrase_id:  # an option added to support import functionality
                self.cursor.execute("INSERT INTO phrase (phrase_id,phrase_txt) VALUE (%s,%s)"
                                    , (phrase_id, phrase_txt))
            else:
                self.cursor.execute("INSERT INTO phrase (phrase_txt) VALUE (%s)", (phrase_txt,))
            self.connection.commit()
        except mysql.connector.Error as error:  # most likely triggered if user already entered that phrase
            # print("parameterized query failed {}".format(error))
            return False

        self.cursor.execute("SELECT LAST_INSERT_ID()")  # returns id of phrase added
        return self.cursor.fetchone()[0]

    def insert_word_in_phrase(self, word_id, phrase_id, offset):
        """Inserts word that's belongs to a phrase newly added by user to the DB.
           The offset (zero based index) parameter indicates the word's index within the phrase.
           """
        self.cursor.execute("INSERT INTO word_in_phrase (word_id,phrase_id,offset) VALUE (%s,%s,%s)",
                            (word_id, phrase_id, offset))
        self.connection.commit()

    def get_phrase_appear(self, phrase_txt):
        """:returns generator of occurrences (within available books) of a phrase selected by user.
           Query below searches for words that are sequential in book (word_serial) and in phrase(offset),
           within the same sentence (sentence_serial), which constitute the same phrase(phrase_id)."""

        self.cursor.execute("SELECT phrase_id from phrase where phrase_txt = %s", (phrase_txt,))
        phrase_id = self.cursor.fetchone()[0]
        try:
            self.cursor.execute("""with selPhrase (word_id , phrase_id , offset) AS
                                 (SELECT *
                                 FROM word_in_phrase
                                 WHERE phrase_id = %s
                                ) 
                                  select title, author, wi1.paragraph_serial, wi1.sentence_serial,
                                                wi1.line_serial, wi1.line_offset
                                  FROM word_instance as wi1 
                                  INNER JOIN word_instance as wi2 on wi2.book_id = wi1.book_id 
                                        and wi2.sentence_serial = wi1.sentence_serial
                                  INNER JOIN selPhrase on wi2.word_id = selPhrase.word_id 
                                  INNER JOIN book on wi1.book_id = book.book_id
                                  WHERE wi2.word_serial = wi1.word_serial + selPhrase.offset
                                  GROUP BY wi1.book_id, wi1.word_serial, wi1.sentence_serial
                                  HAVING COUNT(*) = (SELECT COUNT(*) FROM selPhrase) 
                                  ORDER BY title""", (phrase_id,))
        except mysql.connector.Error as error:
            print("parameterized query failed {}".format(error))
        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield row

    def get_phrases(self):
        """:returns generator of phrases currently in DB. Used when user imports DB."""
        self.cursor.execute("SELECT phrase_txt FROM phrase")
        while True:
            phrase = self.cursor.fetchone()
            if not phrase:
                break
            yield phrase

    def del_phrase(self, phrase):
        """removes the selected group and all words that belongs to it. """

        # retrieve phrase_id of given phrase
        self.cursor.execute(""" select phrase_id
                                from phrase
                                where phrase_txt = %s
                                limit 1""", (phrase,))
        phrase_id = self.cursor.fetchone()

        # get all words belonging to given phrase
        self.cursor.execute("""select word_id
                                from word_in_phrase
                                where phrase_id =  %s""", (phrase_id[0],))
        phrase_words = self.cursor.fetchall()

        # delete words that used to belong to the selected phrase, from said phrase
        for word_id in phrase_words:
            self.cursor.execute("""delete 
                    from word_in_phrase 
                    where phrase_id = %s 
                    and word_id = %s""", (phrase_id[0], word_id[0]))
            self.connection.commit()

        # remove words that used to belong to given phrase from the database, unless they serve another purpose
        if phrase_words:
            for word_id in phrase_words:
                self.remove_word_if_redundant(word_id[0])

        # finally removes the phrase from the database
        self.cursor.execute("""delete from phrase
                                where phrase_id = %s """, (phrase_id[0],))
        self.connection.commit()

    def table_to_json(self, table):
        """Export helper function - generator that return rows of table given in json format """
        self.cursor.execute(f"SELECT * from {table}")
        row_headers = [x[0] for x in self.cursor.description]
        while True:
            row = self.cursor.fetchone()
            if not row:
                break
            yield dict(zip(row_headers, row))  # Converting iterator to dictionary

    def export_to_csv(self, table, folder_path):
        self.cursor.execute(f"SHOW columns FROM {table}")
        headers = ''
        for column in self.cursor.fetchall():
            headers += '\'' + column[0].upper() + '\','
        headers = headers.rstrip(',')
        new_line = '\n'
        self.cursor.execute(f"""SELECT {headers}
                            UNION all
                            SELECT *
                            FROM {table} 
                            INTO OUTFILE '{folder_path}/{table}.csv'   
                            FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
                            LINES TERMINATED BY {repr(new_line)}; """)

    """ Stats functions: """

    def get_sum_books(self):
        """ :returns number of books in the database"""
        self.cursor.execute("select count(*) from book")
        return self.cursor.fetchone()[0]

    def get_sum_size(self):
        """ :returns total size of files read into the database"""
        self.cursor.execute("select sum(size) from book")
        res = self.cursor.fetchone()[0]
        return res if res else 0

    def get_sum_phrases(self):
        """ :returns number of phrases in the database"""
        self.cursor.execute("select count(*) from phrase")
        return self.cursor.fetchone()[0]

    def get_sum_groups(self):
        """ :returns number of word_groups in the database"""
        self.cursor.execute("select count(*) from group_of_words")
        return self.cursor.fetchone()[0]

    def get_sum_par(self, book_id):
        """ :returns number of paragraphs within all books in the database if book_id is None.
            else, result corresponds to specific book provided"""
        if not book_id:  # user cleared DB
            return 0

        params = ()
        if book_id == 'All':  # importing, i.e calculating from scratch
            query = """select sum(total_pars_in_book)
                    from (select max(paragraph_serial) as total_pars_in_book
                            from word_instance
                            group by book_id)as tmp"""
        else:  # user added a new book to the database
            query = """select max(paragraph_serial) 
                               from word_instance
                               where book_id  = %s"""
            params += (book_id,)

        self.cursor.execute(query, params)
        res = self.cursor.fetchone()[0]
        return res if res else 0  # implemented this way for clear method

    def get_sum_line(self, book_id):
        """ :returns number of lines within all books in the database if book_id is None.
            else, result corresponds to specific book provided"""
        if not book_id:  # user cleared DB
            return 0
        params = ()
        if book_id == 'All':  # importing, i.e calculating from scratch
            query = """select sum(total_lines_in_book)
                       from (select max(line_serial) as total_lines_in_book
                                from word_instance
                                group by book_id)as tmp"""
        else:  # user added a new book to the database
            query = """select max(line_serial) 
                        from word_instance
                        where book_id  = %s"""
            params += (book_id,)

        self.cursor.execute(query, params)
        res = self.cursor.fetchone()[0]
        return res if res else 0

    def get_sum_sent(self, book_id):
        """ :returns number of sentences within all books in the database if book_id is None.
            else, result corresponds to specific book provided"""
        if not book_id:  # user cleared DB
            return 0

        params = ()
        if book_id == 'All':  # importing, i.e calculating from scratch
            query = """select sum(total_sents_in_book)
                       from (select max(sentence_serial) as total_sents_in_book
                                from word_instance
                                group by book_id)as tmp"""
        else:  # user added a new book to the database
            query = """select max(sentence_serial) 
                        from word_instance
                        where book_id  = %s"""
            params += (book_id,)

        self.cursor.execute(query, params)
        res = self.cursor.fetchone()[0]
        return res if res else 0

    def get_overall_words(self, book_id):  # using count(*) on large tables isn't optimized well on innoDB driver
        """ :returns number of words within all books in the database if book_id is None.
            else, result corresponds to specific book provided"""
        if not book_id:  # user cleared DB
            return 0
        # logically word_id below could have been replaced with *,
        # but it would have negative impact on performance
        query = """SELECT COUNT(word_id)  
                           FROM word_instance"""
        params = ()
        if book_id != 'All':
            query += " where book_id = %s "
            params += (book_id,)
        self.cursor.execute(query, params)
        return self.cursor.fetchone()[0]

    def get_unique_words(self):
        """ :returns number of unique words within all books in the database."""
        self.cursor.execute("""select count(word_id) as unique_words
                                from word""")
        return self.cursor.fetchone()[0]

    def get_sum_char(self, book_id):
        """ :returns number of characters within all books in the database if book_id is None.
            else, result corresponds to specific book provided"""
        if not book_id:  # user cleared DB
            return 0
        query = """select sum(char_length(word_txt)) as num_of_char
                                         from word,word_instance
                                         where word.word_id = word_instance.word_id """
        params = ()
        if book_id != 'All':
            query += " and book_id = %s "
            params += (book_id,)
        self.cursor.execute(query, params)
        res = self.cursor.fetchone()[0]  # intended to deal with clear
        if res:
            return res
        return 0
