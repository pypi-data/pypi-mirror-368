"""
wordfinder.py

This module contains all the logic of the wordfinder_lib library, It is
completely self-contained and encapsulated, and has its own internal tests.

Behavior:
- If run directly from the console *without arguments*, internal tests are executed.
- If run with 2 arguments (desired word length and a string of source letters),
  it generates an output with the found words.
- If imported as a module, it exposes a method in the `WordFinder` class
  that accepts the same 2 arguments and returns a tuple: (bool, str),
  where:
    - bool: indicates whether the input was valid.
    - str: contains the found words (or an error message if input was invalid).

Dependencies (used only within function/method scope):
- `collections` (stdlib) - used in `_extract_transform_load()` method of the `WordFinder` class.
- `itertools` (stdlib) - used in `_data_analysis()` method of the `WordFinder` class.
- `pathlib` (stdlib) - used in `word_finder()` method of the `WordFinder` class and `_wordfinder_test()` function.
- `sys` (stdlib) - used in `_wordfinder_test()` function.
- `doctest` (stdlib) - used in `_wordfinder_test()` function.
- `io` (stdlib) - used in `_wordfinder_test()` function.

Note:
This design of placing Dependencies within each method or function that uses
it was chosen because, except for Path for typing, everything else was used
locally. Above all, it was done to keep the module's namespace clean.
"""


from pathlib import Path


__all__: list[str] = ["WordFinder"]


class WordFinder:
    @staticmethod
    def _data_check(word_length: str, available_letters: str)-> tuple[bool, int, str]:
        """
        Check user input data.

        This method cleans the user's input, then checks that it is correct,
        and returns a boolean value to indicate whether it is correct or,
        incorrect and a string. If it is correct, the clean input is sent,
        and if it is incorrect, the original input is sent.

        Arguments:
            word_length (str): Integer value indicating the length of the word to
                search for.
            available_letters (str): String of the set of letters that will be
                taken to build all possible words.
        
        Returns:
            tuple
                bool: True Indicates whether the entry meets the necessary
                    requirements, otherwise False.
                int: Whole number
                str:Depending on whether it is True, a clean string of letters,
                    if it is False, the original input string.

        Examples.
            >>> WordFinder._data_check("5", "Hello")
            (True, 5, 'hello')
            >>> WordFinder._data_check("2", "ABCDE FG")
            (True, 2, 'abcdefg')
            >>> WordFinder._data_check("", "")
            (False, 0, 'Both entries are incorrect, please read the help.')
            >>> WordFinder._data_check("15.5", "Abc qq")
            (False, 0, 'The length entered is incorrect, please read the help.')
            >>> WordFinder._data_check("-5", "a b Z")
            (False, 0, 'The length entered is incorrect, please read the help.')
            >>> WordFinder._data_check("0", "a b Z")
            (False, 0, 'The length entered is incorrect, please read the help.')
            >>> WordFinder._data_check("1", "a b Z")
            (False, 0, 'The length entered is incorrect, please read the help.')
            >>> WordFinder._data_check("5", "abc$")
            (False, 0, 'the letter set is incorrect, please read the help.')
        """
        parsing_word_length: str
        status_length: bool
        parsing_word_length, status_length = WordFinder._parsing_numbers(word_length)

        parsing_available_letters: str
        status_letters: bool
        parsing_available_letters, status_letters = WordFinder._parsing_string(available_letters)

        status: list[bool] = [status_length, status_letters]
        matches: str
        if sum(status) == 2:
            int_word_length = int(parsing_word_length)
            return (True, int_word_length, parsing_available_letters) 
        else:
            incorrect_entries: str = "Both entries are incorrect, please read the help."
            incorrect_length: str = "The length entered is incorrect, please read the help."
            incorrect_letters: str = "the letter set is incorrect, please read the help."
            matches = f"{incorrect_entries if (sum(status)==0) else(incorrect_length) if(status[0]==0) else(incorrect_letters)}"
            return (False, 0, matches)
        
    @staticmethod
    def _parsing_numbers(number: str)-> tuple[str, bool]:
        """
        Clean and check the input integer

        Args:
            number (int): Integer in str format to be cleaned and checked.

        Returns:
            tuple
                str: Entry cleared if True, and if False the original entry.
                bool: Its value indicates whether it is a valid entry after
                    cleaning.

        Examples.
            >>> WordFinder._parsing_numbers("5    ")
            ('5', True)
            >>> WordFinder._parsing_numbers("  5")
            ('5', True)
            >>> WordFinder._parsing_numbers("   2    ")
            ('2', True)
            >>> WordFinder._parsing_numbers("")
            ('', False)
            >>> WordFinder._parsing_numbers("$")
            ('$', False)
            >>> WordFinder._parsing_numbers("5.0")
            ('5.0', False)
            >>> WordFinder._parsing_numbers("-5")
            ('-5', False)
            >>> WordFinder._parsing_numbers("5 5")
            ('5 5', False)
            >>> WordFinder._parsing_numbers("0")
            ('0', False)
            >>> WordFinder._parsing_numbers("1")
            ('1', False)
        """
        cache: str = number.strip(" \n")
        if len(cache) == 0:
             return (number, False)
        for digit in cache:
            if not digit.isdigit():
                return (number, False)
        if int(cache) == 0 or int(cache) == 1:
            return (number, False)
        return (cache, True)
    
    @staticmethod
    def _parsing_string(string: str)-> tuple[str, bool]:
        """
        Clean and check if the input is correct.

        Args:
            string (str): Original input chain, to be cleaned and checked.
        
        Returns:
            tuple
                str: Entry cleared if True, and if False the original entry.
                bool: Its value indicates whether it is a valid entry after
                    cleaning.

        Examples.
            >>> WordFinder._parsing_string("ABC")
            ('abc', True)
            >>> WordFinder._parsing_string("ABc  ")
            ('abc', True)
            >>> WordFinder._parsing_string("  aBC")
            ('abc', True)
            >>> WordFinder._parsing_string("  AbC  ")
            ('abc', True)
            >>> WordFinder._parsing_string(" ABC fa  z")
            ('abcfaz', True)
            >>> WordFinder._parsing_string("abc1")
            ('abc1', False)
            >>> WordFinder._parsing_string("abc$")
            ('abc$', False)
            >>> WordFinder._parsing_string("")
            ('', False)
        """
        cache: str = ''.join(string.strip(" \n").split()).lower()
        size = len(cache)
        if size == 0 or size == 1:
            return (string, False)
        for char in cache:
            if not char.isalpha():
                return (string, False)
        return (cache, True)
        
    @staticmethod
    def _extract_transform_load(filename: Path, permision: str)-> dict[str, list[str]]:
        """
        Read, clean, transform and save.

        Read the data from a file, clean line by line, removing all line
        breaks and spaces on all sides of the line, transform each line
        by sorting it, store them in a dict according to their key and
        in their key all the words that match that key.

        Args:
            filename (Path): Path to the file containing the English words.
            permision (str): Permissions of the file to be opened.

        Returns:
            filewords (dict[str, list[str]]): Dict where all the prepared
                information will be stored, in the key will be all the unique
                anagrams of the file with English words, and in the value
                a list with all the words that match those anagrams of
                the key.

        Dependencies:
            - collections (stdlib)

        Examples:
        """
        import collections

        filewords: dict[str, list[str]] = collections.defaultdict(list)
        with open(filename, permision) as file:
            for line in file:
                cache: str = ''.join(sorted(line.strip(" \n")))
                word: str = line.strip(" \n")
                filewords[cache].append(word)
        return filewords

    @staticmethod
    def _data_analysis(file: dict[str, list[str]], data: tuple[int, str])-> str:
        """
        Find all possible words.

        Search for all possible words, according to the input data and
        the values stored in the dict, all words that have the indicated
        length and that are formed only by the letters that contain part
        or all of the indicated string of letters will be searched for.
        For this, the anagram technique of ordering the input letters
        will be used, and then all possible combinations will be generated
        according to the desired length, and then each combination will
        be searched for in the key of the dict that contains the ordered
        word in the key and in its value a list of matching words for
        that anagram of the key.

        Args:
            file (dict[str, list[str]]): A dictionary prepared with all
            the information necessary to perform the required searches.
            Depending on the input conditions, each key is a word sorted
            alphabetically, and its value is a list containing the original
            word that formed the keyword. If there are other words that are
            anagrams of the key, they are stored in their original versions
            in the same word list as the value of that key.
            tuple
                n (int): Integer of the length of words to search for.
                word (str): string of letters that must contain the words 
                    to search for, the words to search can only contain these
                    letters, but they do not have to be all the letters but 
                    combinations of them.

        Returns:
            result (str): All the words found, if it is empty it is because no
                matches were found.

        Dependencies:
            - itertools (stdlib)

        Examples.
        """
        import itertools

        combinations: set[str] = set()
        n: int
        word: str
        n, word = data
        for combination in itertools.combinations(word, n):
            combinations.add(''.join(sorted(combination)))
        words_list: list[list[str]] = []
        for combination_str in combinations:
            if file[combination_str]:
                words: list[str] = file[combination_str]
                words_list.append(words)

        cache: list[str] = [' '.join(words) for words in words_list]
        result:str = ' '.join(sorted(set(cache)))
        return result

    @staticmethod
    def word_finder(word_length: str, available_letters: str)-> tuple[bool, str]:
        """
        Data pipelines.

        Controls all data flow, checks, ETL, Analysis, result, connecting
        all parts of this class.

        Args:
            word_length (str): User input representing the length of words to 
                find.
            available_letters (str): User input representing the string of 
                letters that will be used to find the words.

        Returns:
            tuple
                bool: Represents whether the entries were correct or not. 
                str: Depending on whether the inputs were correct or not, the
                    result is generated, which may be no words found, one or
                    more words found, or information about why the input(s)
                    were incorrect.

        Dependencies:
            - pathlib (stdlib)

        Examples.
            >>> WordFinder.word_finder("5", "Hello")
            (True, 'hello')
            >>> WordFinder.word_finder("5", "fetgioba")
            (True, 'befit befog begot bigot bogie fagot togae')
            >>> WordFinder.word_finder("", "")
            (False, 'Both entries are incorrect, please read the help.')
            >>> WordFinder.word_finder("5", "")
            (False, 'the letter set is incorrect, please read the help.')
            >>> WordFinder.word_finder("", "gjhskx")
            (False, 'The length entered is incorrect, please read the help.')
            >>> WordFinder.word_finder("5", "$/*-.!@#$%^&*()")
            (False, 'the letter set is incorrect, please read the help.')
        """
        import pathlib

        status: bool
        n: int
        letters: str
        status, n, letters = WordFinder._data_check(word_length, available_letters)
        if status:
            word_files_path: Path = pathlib.Path(__file__).resolve().parent / "word_files" / "english_words.txt"
            etl: dict[str, list[str]] = WordFinder._extract_transform_load(word_files_path, "r")
            result: str = WordFinder._data_analysis(etl, (n, letters))
            return (True, result)
        else:
            return (False, letters)
        

def _wordfinder_test()-> None:
    """
    When this module is called directly or called as an imported module but
    you want to test the tests.

    case 1:
    In this case, if the module is called with two arguments, it is understood
    that you want to directly test the module's functionality and its response,
    even if both or one of the two arguments are invalid. The output is a tuple
    with a True or False value followed by a string. If True, it is the list of
    words found or empty; if False, the string will contain the error message
    in the arguments.
    The output is displayed on the console and saved in a text file.

    case 2:
    If there are no arguments, or if they are different than two, the doctest
    tests are called in verbose mode so that all the test information is
    displayed on the console, and the result is also saved in a text file.

    Args:
        None

    Returns:
        None

    Dependencies:
            - pathlib (stdlib)
            - sys (stdlib)
            - doctest (stdlib)
            - io (stdlib)
            - typing (TextIO) (stdlib)
    """
    import pathlib
    import sys

    args: list[str] = sys.argv[1:]
    test_logs_path: Path = pathlib.Path(__file__).resolve().parent / "test_logs"
    if len(args) == 2:
        functionality: tuple[bool, str] = WordFinder.word_finder(args[0], args[1])
        print(functionality)
        with open(test_logs_path / "wordfinder_func.txt", "a") as file:
            file.write(str(functionality) + "\n")
    else:
        import doctest
        import io
        from typing import TextIO

        output: io.StringIO = io.StringIO()
        with open(test_logs_path /"wordfinder_test.txt", "w") as file:
            original_stdout: TextIO = sys.stdout
            sys.stdout = output
            doctest.testmod(sys.modules[__name__], verbose=True)
            result: str = output.getvalue()
            sys.stdout = original_stdout  
            print(result)
            file.write(result + "\n")


if __name__ == "__main__":
    _wordfinder_test()