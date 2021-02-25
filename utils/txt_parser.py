from msg_box import MsgIcon, display_msg
import re, os


def get_book_details(path):
    """ returns book's title, author, release date, size and absolute file path """
    size = str(round((os.stat(path).st_size / pow(2, 20)), 2)) + "MB"
    title, author, date = [None for _ in range(3)]
    author_pattern = re.compile(r'(Author: )([^\n]+)')
    title_pattern = re.compile(r'(Title: )([^\n]+)')  # second group represents max occurrences of not (^) '\n'
    date_pattern = re.compile(r'(Release Date: )(\w+ \d\d?, \d{4})')

    try:
        with open(path, 'r') as file:
            for line in file:
                if not author:
                    author = author_pattern.search(line)
                if not title:
                    title = title_pattern.search(line)
                if not date:
                    date = date_pattern.search(line)
                if title and author and date:  # and date and size:
                    # return title, author, size
                    return title.group(2), author.group(2), date_format(date.group(2)), size, path

    except IOError:
        display_msg(MsgIcon.WARNING, "Warning", "failed to open book. could not find / open file")
        return


def months_to_num(month):
    """helper function of date_format. translate months' names to numbers."""
    return {'January': '1',
            'February': '2',
            'March': '3',
            'April': '4',
            'May': '5',
            'June': '6',
            'July': '7',
            'August': '8',
            'September': '9',
            'October': '10',
            'November': '11',
            'December': '12'}.get(month)


def date_format(date):
    """transforms date in the following format: month_name day_number, year to day/month/year format"""
    li = date.split(" ")
    li[0] = months_to_num(li[0])
    li[1] = li[1].replace(",", "")
    return '/'.join(li)


def get_next_word(path):
    """a word generator that returns a word with the following parameters analysed:
        word = the actual word.
        wrd_cnt, sent_cnt, line_cnt, par_cnt = word/sentence/line/paragraph number in relation to beginning of text.
        line_offset = word index since the beginning of the line. only parameter that is zero based.
        char_cnt = number of characters in a word.
        """
    try:
        line_with_txt = - 1  # marks the last non empty line encountered
        wrd_cnt = 0
        par_cnt = 1
        sent_cnt = 1
        with open(path, 'r') as file:
            for line_cnt, line in enumerate(file, start=1):
                line_offset = -1  # initial val = -1 so index of word within line will be zero based
                if line != '\n':
                    line_with_txt = line_cnt
                elif line_cnt == line_with_txt + 1:  # current line == '\n' and last line wasn't
                    par_cnt += 1
                sentences = list(filter(None, re.split(r'[!?.]', line)))  # filter removes empty elements
                for i in range(len(sentences)):
                    if i > 0:  # if text appears after [!?.] it is considered a new sentence.
                        sent_cnt += 1
                    words_in_sent = re.findall(r'\w+', sentences[i])
                    for word in words_in_sent:
                        if word:
                            line_offset += 1
                            wrd_cnt += 1
                            yield word.lower(), wrd_cnt, sent_cnt, line_cnt, line_offset, par_cnt

    except IOError:
        display_msg(MsgIcon.WARNING, "Warning", "failed to open book. could not find / open file")
        return
