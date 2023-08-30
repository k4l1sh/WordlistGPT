from concurrent.futures import ThreadPoolExecutor
from itertools import product
from time import perf_counter
from functools import reduce
import argparse
import requests
import logging
import random
import json
import re
import os

def main():
    load_env()
    args = parse_arguments()
    set_logger(args)
    openai_key = args.key or os.getenv("API_KEY")
    if not validate_args(args, openai_key):
        return
    args_dict = vars(args).copy()
    if openai_key:
        args_dict['key'] = f"{openai_key[:3]}...{openai_key[-4:]}"
    logging.debug(f"Arguments parsed: {args_dict}")
    logging.info("Starting WordlistGPT...")
    wordlist_generator = WordlistGenerator(args, openai_key)
    wordlist_generator.orchestrate_threads()
    wordlist_generator.save_wordlist()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='''Generate wordlists using a variety of options. 
        Customize the output using arguments such as length, casing, leet speak, and more.
        ''',
        epilog='''Examples:
        python wordlistgpt.py -w "harry potter"
        python wordlistgpt.py -w cybersecurity -n 50 -min 5 -max 15 -u 2 -l 3 -r 2
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    word_options = parser.add_argument_group('Word Options', 'Control the basic word parameters.')
    word_options.add_argument('-w', '--words', nargs='+', help='Words to generate wordlist for.')
    word_options.add_argument('-n', '--number', type=int, default=20, help='Number of words to generate in ChatGPT for each word. (default: %(default)s)')
    size_options = parser.add_argument_group('Size Options', 'Control the size of the words and the wordlist.')
    size_options.add_argument('-min', '--min-size', type=int, default=6, help='Minimum amount of characters for each word. (default: %(default)s)')
    size_options.add_argument('-max', '--max-size', type=int, default=14, help='Maximum amount of characters for each word. (default: %(default)s)')
    size_options.add_argument('-m', '--max-words', type=int, default=10000000, help='Maximum number of words in the wordlist. (default: %(default)s)')
    special_options = parser.add_argument_group('Special Options', 'Control the special characters and casing in words.')
    special_options.add_argument('-u', '--uppercase', type=int, default=float('inf'), help='Maximum number of characters to convert to uppercase in each word. (default: %(default)s)')
    special_options.add_argument('-l', '--leet', type=int, default=float('inf'), help='Maximum number of leet characters to replace in each word. (default: %(default)s)')
    special_options.add_argument('-lm', '--leet-mapping', type=str, default=json.dumps({'o': '0', 'i': '1', 'l': '1', 'z': '2', 'e': '3', 'a': '4', 's': '5', 'g': '6', 't': '7', 'b': '8', 'g': '9'}),
                                 help='JSON-formatted leet mapping dictionary. (default: %(default)s)')
    special_options.add_argument('-r', '--random-chars', type=int, default=6, help='Maximum range of random characters to be added. (default: %(default)s)')
    special_options.add_argument('-rc', '--random-charset', type=str, default=r'''0123456789!@$&+_-.?/+;#''', help='Charset of characters to be randomly added. (default: %(default)s)')
    special_options.add_argument('-rl', '--random-level', type=int, default=3, help='Number of iterations of random characters to be added. (default: %(default)s)')
    special_options.add_argument('-rw', '--random-weights', nargs=3, type=float, default=[0.47, 0.47, 0.06],
                                 help='''Weights for determining position of random character insertion. 
                                 First value: Probability for inserting at the beginning.
                                 Second value: Probability for inserting at the end.
                                 Third value: Probability for inserting at a random position. (default: %(default)s)''')
    other_options = parser.add_argument_group('Other Options')
    other_options.add_argument('-k', '--key', type=str, help='OpenAI API Key. (default: %(default)s)', default=None)
    other_options.add_argument('-o', '--output', type=str, default='wordlist.txt',help='Output file for the generated wordlist. (default: %(default)s)')
    other_options.add_argument('-d', '--debug', action='store_true', default=False, help='If True, enable debug logging. (default: %(default)s)')
    other_options.add_argument('-s', '--silent', action='store_true', default=False, help='If True, disable logging. (default: %(default)s)')
    return parser.parse_args()

def validate_args(args, openai_key):
    if not openai_key:
        logging.warning("API_KEY is not set in the environment variables. To generate more related words with GPT, set it in the .env file with API_KEY=YOUR API KEY or enter as an argument --key.")
    if not args.words:
        logging.error(
            "No words provided. Use -w or --words argument followed by one or more words.")
        return False
    return True

def load_env(env_file=".env"):
    if os.path.exists(env_file):
        with open(env_file, 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def set_logger(args):
    logger = logging.getLogger()
    if args.silent:
        logger.setLevel(logging.CRITICAL)
    elif args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)


class CustomFormatter(logging.Formatter):
    GREEN = '\033[1;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[1;31m'
    WHITE = '\033[1;37m'
    RESET = '\033[0m'
    LEVELS = {
        logging.DEBUG: f"{WHITE}[~]{RESET}",
        logging.INFO: f"{GREEN}[+]{RESET}",
        logging.WARNING: f"{YELLOW}[!]{RESET}",
        logging.ERROR: f"{RED}[x]{RESET}",
        logging.CRITICAL: f"{RED}[X]{RESET}",
    }

    def format(self, record):
        level = self.LEVELS.get(record.levelno, "")
        message = f"{level} {record.getMessage()}"
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            message += f"\n{exc_text}"
        return message


class WordlistGenerator:

    def __init__(self, args, openai_key):
        self.args = args
        self.openai_key = openai_key
        self.gpt_endpoint = "https://api.openai.com/v1/chat/completions"
        self.leet_mapping = json.loads(args.leet_mapping)
        self._wordlist = set()
        self.estimated_words_number = len(args.words)*(args.number+1)

    @property
    def wordlist(self):
        return sorted(list(self._wordlist))

    @wordlist.setter
    def wordlist(self, words):
        if not isinstance(words, (set, list, tuple)):
            words = {words}
        self._wordlist.update(words)
        if not self.args.silent and len(self._wordlist)%1000 == 0:
            self.print_progress_bar(len(self._wordlist), self.estimated_words_number)

    @wordlist.deleter
    def wordlist(self):
        self._wordlist.clear()

    def force_len(self, min_len, max_len):
        self._wordlist -= {word for word in self._wordlist if not min_len <= len(word) <= max_len}

    def words_from_string(self, words):
        return {word.strip().rstrip('.').lower() for word in re.findall(r'''[\d\r\n-]*\.?\s?([\w \-\.'"]+)''', words)}

    def split_subwords(self):
        self.wordlist = {subword for word in self._wordlist for subword in re.split(r'\W+', word)}

    def remove_non_words(self):
        cleaned_wordlist = {re.sub(r'\W', '', word) for word in self._wordlist}
        del self.wordlist
        self.wordlist = cleaned_wordlist

    def word_over_max_chars(self, word_len):
        if word_len > self.args.max_size:
            return True
        return False

    def wordlist_over_max_limit(self):
        if len(self._wordlist) > self.args.max_words:
            logging.warning(
                f"Wordlist has reached the limit of {self.args.max_words} words. Stopping the word insertion.")
            return True
        return False

    def orchestrate_threads(self):
        start = perf_counter()
        with ThreadPoolExecutor() as executor:
            logging.info(f"Generating wordlist for {self.args.words}")
            executor.map(self.words_from_gpt, self.args.words, [self.args.number]*len(self.args.words))
        self.generate_wordlist()
        if not self.args.silent:
            self.print_progress_bar(len(self._wordlist), len(self._wordlist))
            print("")
        logging.info(f"Elapsed time: {round(perf_counter()-start, 2)} seconds.")

    def words_from_gpt(self, word, num_words):
        self.wordlist = word
        if num_words > 1 and self.openai_key:
            content = f"You are a word generator tool that generates {num_words} words related to the theme {word}. Each word must have a minimum of {self.args.min_size} and a maximum of {self.args.max_size} characters."
            message = [{"role": "system", "content": content}]
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-3.5-turbo",
                "messages": message,
                "max_tokens": 4096 - len(content)
            }
            response = requests.post(self.gpt_endpoint, headers=headers, json=data)
            if response.ok:
                response_data = response.json()
                generated_words_from_gpt = self.words_from_string(response_data['choices'][0]['message']['content'])
                self.wordlist = generated_words_from_gpt
                logging.info(f"Words generated from GPT based on the word {word}: {generated_words_from_gpt}")
            else:
                logging.error(f"API call failed with status code {response.status_code}, Error: {response.text}")

    def generate_wordlist(self):
        try:
            self.split_subwords()
            self.force_len(3, self.args.max_size)
            self.remove_non_words()
            self.estimate_words()
            if not self.wordlist_over_max_limit() and self.args.uppercase > 0:
                self.add_uppercase_variations()
            if not self.wordlist_over_max_limit() and self.args.leet > 0:
                self.add_leet_variations()
            if not self.wordlist_over_max_limit() and self.args.random_chars > 0:
                self.insert_chars()
            self.force_len(self.args.min_size, self.args.max_size)
        except Exception:
            logging.error("An error occurred during wordlist generation", exc_info=True)

    def add_uppercase_variations(self):
        limited_uppercase_wordlist = set()
        for word in self.wordlist:
            if self.wordlist_over_max_limit():
                return
            for combination in product(*[(ch.lower(), ch.upper()) for ch in word]):
                if sum(1 for c in combination if c.isupper()) <= self.args.uppercase:
                    limited_uppercase_wordlist.add(''.join(combination))
        self.wordlist = limited_uppercase_wordlist

    def add_leet_variations(self):
        for word in self.wordlist:
            if self.wordlist_over_max_limit():
                return
            char_options_list = []
            leet_count = 0
            for ch in word:
                options = [ch]
                leet_equiv = self.leet_mapping.get(ch)
                if leet_equiv and leet_count < self.args.leet:
                    options.append(leet_equiv)
                    leet_count += 1
                char_options_list.append(options)
            self.wordlist = {''.join(combination) for combination in product(*char_options_list)}

    def insert_chars(self):
        for word in self.wordlist:
            if self.wordlist_over_max_limit():
                return
            new_words = set()
            for _ in range(self.args.random_level):
                new_word = word
                num_chars = random.randint(0, self.args.random_chars)
                if self.word_over_max_chars(len(new_word) + num_chars):
                    continue
                for _ in range(num_chars):
                    char = random.choice(self.args.random_charset)
                    position = random.choices(
                        [0, len(new_word), random.randint(1, len(new_word)-1)],
                        weights=self.args.random_weights
                    )[0]
                    new_word = new_word[:position] + char + new_word[position:]
                new_words.add(new_word)
            self.wordlist = new_words

    def estimate_words(self):
        total = 0
        for word in self._wordlist:
            possibilities_for_each_char = []
            for ch in word:
                possibilities = {ch.lower(), ch.upper()}
                leet_equiv = self.leet_mapping.get(ch.lower())
                if leet_equiv:
                    possibilities.add(leet_equiv)    
                possibilities_for_each_char.append(len(possibilities))  
            total += reduce(lambda x, y: x * y, possibilities_for_each_char)
        if self.args.random_chars:
            total *= 1 + self.args.random_level*0.9
        self.estimated_words_number = int(total)

    @staticmethod
    def print_progress_bar(iteration, total, bar_length=20):
        max_total = max(iteration, total)
        percentage = (iteration / max_total) * 100
        block = int(round(bar_length * iteration / max_total))
        text = f"\033[1;32m[+]\033[0m Progress: [{'#' * block}{'-' * (bar_length - block)}] {round(percentage, 2)}% ({iteration}/{max_total})\033[K"
        print(text, end='\r' , flush=True)

    def save_wordlist(self):
        with open(self.args.output, 'w') as file:
            file.write('\n'.join(self.wordlist))
        logging.info(f"A total of {len(self._wordlist)} words have been saved in {self.args.output}")


if __name__ == '__main__':
    main()
