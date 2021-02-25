# Ijson is an iterative JSON parser that can process a multi GB json file without
# encountering a memory shortage by processing the file in small chunks.
import ijson, json, os
from PyQt5.QtWidgets import QFileDialog
from msg_box import MsgIcon, display_msg
from database.schema import TABLES
from utils.Exceptions import Abort

MEM_LIMIT = 50000  # memory capacity limit on number of values to be stored in buffer before being read off.


def is_action_confirmed(msg):
    """ :returns True if user confirm its decision. otherwise, if it aborts the process, returns false. """
    try:
        display_msg(MsgIcon.QUESTION, "Confirm Your Action", msg)
    except Abort:  # user chose to abort clearing the DB
        return False
    return True


def clear_db(db):
    """ Clears database. Called by user after pushing 'Clear' in menu """
    if is_action_confirmed("Are you sure you would like to clear the Database?"):
        db.reset_db(True)


def extract_tables(db, json_data):
    """ export_db_json helper function that collects tables rows in json format and saves them in json_data"""
    for table in TABLES:
        rows = []
        for row in db.table_to_json(table):
            rows.append(row)
        json_data[table] = rows


def export_db_json(db, central_widget):
    """Exports database to a local JSON file. Called by user after clicking 'Export Json' in menu """
    json_data = {}
    extract_tables(db, json_data)
    file_name = QFileDialog.getSaveFileName(central_widget, "Choose save location and a file_name", "", "(*.json)")
    if file_name[0]:  # if a file was selected
        with open(file_name[0], 'w+') as file:
            file.write(json.dumps(json_data, indent=2))


def export_db_sql(central_widget, credentials):
    """Exports database to a local SQL file. Called by user after clicking 'Export SQL' in menu"""
    display_msg(MsgIcon.INFORMATION, "Take Notice",
                "Attention: \nUsers aren't allowed to save in the operating system's drive.")
    path = QFileDialog.getSaveFileName(central_widget, "Choose save location and a file_name",
                                       'myBackupFile', "(*.sql)")
    if path[0]:  # if a file was selected
        os.system(f'mysqldump -u {credentials["user"]} -p{credentials["password"]} testdatabase > "{path[0]}"')


def export_db_csv(db, central_widget):
    """Exports database to a series of Excel files within a selected folder"""
    display_msg(MsgIcon.INFORMATION, "Instructions",
                "Attention: Users aren't allowed to save in the operating system's drive.\n"
                "Each table will be exported to a separate csv. file."
                "\nPlease provide a suitable folder location.")

    folder_path = str(QFileDialog.getExistingDirectory(central_widget, "Select Directory"))
    if folder_path:
        # exports each table to a separate file
        for table in TABLES:
            db.export_to_csv(table, folder_path)


def import_to_db_sql(db, central_widget, credentials):
    """Executes a previously created SQL file to rebuild database. """
    if is_action_confirmed("Importing will overwrite current Database state."
                           "\nConsider exporting your progress beforehand.\nAdvance?"):
        path = QFileDialog.getOpenFileName(central_widget, "Choose an SQL file to import from", "", "(*.sql)")
        if path[0]:
            db.reset_db()
            os.system(f'mysql -u {credentials["user"]} -p{credentials["password"]} testdatabase < "{path[0]}"')
        db.notify_import()


def import_to_db_json(db, central_widget):
    """Reads Tables and related content from previously created JSON file into the DB.
     avoids reading the whole file to memory at once by using ijson."""

    if is_action_confirmed("Importing will overwrite current DB state."
                           "\nConsider exporting your progress beforehand. \nAdvance?"):
        import_funcs = ['import_' + table for table in TABLES]
        file_name = QFileDialog.getOpenFileName(central_widget, "Choose a JSON file to import from", "", "(*.json)")
        if file_name[0]:  # if a file was selected
            db.reset_db()
            try:
                with open(file_name[0], 'r') as file:

                    for i in range(len(import_funcs)):
                        # calls every import function below with the following parameters: db
                        # and a value generator that returns each of the table's values one by one.
                        eval(import_funcs[i])(db, ijson.items(file, TABLES[i] + '.item'))
                        file.seek(0)  # reset cursor

                db.notify_import()
            except IOError:
                display_msg(MsgIcon.WARNING, "Warning", "failed to open JSON file."
                                                        "\n could not find / open file")
                return


def import_word(db, word_generator):
    """Reads words from the generator in batches in size equal to a pre-determent limit,
     then inserting them to the DB, thus handling with potentially large volume of values."""
    words = []
    for word in word_generator:
        words.append((word['word_id'], word['word_txt']))
        if len(words) > MEM_LIMIT:
            db.insert_mult_word(words, True)
            words.clear()
    db.insert_mult_word(words, True)


def import_word_instance(db, word_inst_generator):
    """Reads word instances from the generator in batches of size equal to a pre-determent limit,
       then inserting them to the DB, thus handling with potentially large volume of values."""
    instances = []
    for word_inst in word_inst_generator:
        instances.append((word_inst['word_id'], word_inst['word_serial'], word_inst['book_id'],
                          word_inst['sentence_serial'], word_inst['line_serial'], word_inst['line_offset']
                          , word_inst['paragraph_serial']))
        if len(instances) > MEM_LIMIT:
            db.insert_mult_word_instance(instances)
            instances.clear()
    db.insert_mult_word_instance(instances)


# the following import functions are similar to the couple the above, other than they don't require
# memory management, since these values are entered individually by user, one by one. """

def import_book(db, books_generator):
    for book in books_generator:
        db.insert_book((book['book_id'], book['title'], book['author'], book['date'],
                        book['size'], book['path']))


def import_phrase(db, phrase_generator):
    for phrase in phrase_generator:
        db.insert_phrase(phrase['phrase_txt'], phrase['phrase_id'])


def import_word_in_phrase(db, word_phrase_generator):
    for word_phrase in word_phrase_generator:
        db.insert_word_in_phrase(word_phrase['word_id'], word_phrase['phrase_id'], word_phrase['offset'])


def import_group_of_words(db, group_generator):
    for group in group_generator:
        db.insert_group(group['group_name'], group['group_id'])


def import_word_in_group(db, word_group_generator):
    for word_in_group in word_group_generator:
        db.insert_word_in_group(word_in_group['word_id'], word_in_group['group_id'])
