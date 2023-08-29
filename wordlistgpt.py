from memory_profiler import profile
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse
import random
import requests
from itertools import product
import sys
import re
import os

@profile
def main():
    set_logger()
    load_env()
    args = parse_arguments()
    openai_key = args.key or os.getenv("API_KEY")
    if not validate_args(args, openai_key):
        return
    wordlist_generator = WordlistGenerator(args, openai_key)
    wordlist_generator.orchestrate_threads()
    wordlist_generator.save_wordlist(wordlist_generator.wordlist, args.output)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate wordlists')
    parser.add_argument('-w', '--words', nargs='+', help='Words to generate wordlist for')
    parser.add_argument('-n', '--number', type=int, default=30, help='Number of words to generate in ChatGPT for each word')
    parser.add_argument('-m', '--max-words', type=int, default=40000000, help='Maximum number of words in the wordlist')
    parser.add_argument('-min', '--min-size', type=int, default=6, help='Minimum amount of characters for each word')
    parser.add_argument('-max', '--max-size', type=int, default=20, help='Maximum amount of characters for each word')
    parser.add_argument('-k', '--key', type=str, help='OpenAI API Key')
    parser.add_argument('-o', '--output', type=str, default='wordlist.txt', help='Output file for the generated wordlist')
    parser.add_argument('-u', '--uppercase', type=int, default=2, help='Maximum number of characters to convert to uppercase in each word')
    parser.add_argument('-l', '--leet', type=int, default=2, help='Maximum number of leet characters to replace in each word')
    parser.add_argument('-r', '--random-chars', type=int, default=2, help='Maximum range of random characters to be added')
    parser.add_argument('-rc', '--random-charset', type=str, default=r'''0123456789!@$&+_-.?/+;#''',
                        help='Charset of characters to be randomly added')
    parser.add_argument('-rl', '--random-level', type=int, default=1, help='Number of iterations of random characters to be added')
    return parser.parse_args()

def validate_args(args, openai_key):
    if not openai_key:
        logging.error("API_KEY is not set in the environment variables. Set it in the .env file with API_KEY=(YOUR API KEY) or enter as argument -k")
        return False
    if not args.words:
        logging.error("No words provided, use -w or --words argument followed by one or more words.")
        return False
    return True

def load_env(env_file=".env"):
    if os.path.exists(env_file):
        with open(env_file, 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def set_logger():
    logger = logging.getLogger()
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
        return f"{level} {record.getMessage()}"

class WordlistGenerator:
    
    def __init__(self, args, openai_key):
        self.args = args
        self.openai_key = openai_key
        self.gpt_endpoint =  "https://api.openai.com/v1/chat/completions"
        self.leet_mapping = {
            'o': '0',
            'i': '1',
            'l': '1',
            'z': '2',
            'e': '3',
            'a': '4',
            's': '5',
            'g': '6',
            't': '7',
            'b': '8',
            'g': '9',
        }
        self._wordlist = set()

    @property
    def wordlist(self):
        return sorted(list(self._wordlist))

    @wordlist.setter        
    def wordlist(self, words):
        if not isinstance(words, (set, list, tuple)): 
            words = {words}
        self._wordlist.update(words)
        print(len(self._wordlist))

    @wordlist.deleter
    def wordlist(self):
        self._wordlist.clear()

    def apply_to_wordlist(self, func, *args, **kwargs):
        self.wordlist = {func(word, *args, **kwargs) for word in self._wordlist}

    def force_len(self, min_len, max_len):
        self._wordlist -= {word for word in self._wordlist if not min_len <= len(word) <= max_len}

    def add_words_from_string(self, words):
        self.wordlist = {word.strip().rstrip('.').lower() for word in re.findall(r'''[\d\r\n-]*\.?\s?([\w \-\.'"]+)''', words)}
    
    def split_subwords(self):
        self.wordlist = {subword for word in self._wordlist for subword in re.split(r'\W+', word)}
    
    def remove_non_words(self):
        cleaned_wordlist = {re.sub(r'\W', '', word) for word in self._wordlist}
        del self.wordlist
        self.wordlist = cleaned_wordlist
    
    def setter_stop(self, word):
        if len(word) > self.args_max_size:
            return True
        if len(self._wordlist) > self.args.max_words:
            return True
        return False

    def orchestrate_threads(self):
        start = perf_counter()
        with ThreadPoolExecutor() as executor:
            logging.info(f"Generating wordlist for {self.args.words}")
            executor.map(self.generate_wordlist, self.args.words, [self.args.number]*len(self.args.words))
        print(perf_counter()-start)


    def generate_wordlist(self, word, num_words):
        try:
            self.wordlist = word
            if num_words > 1:
                content = f"You are a word generator tool that generates {num_words} words related to the theme {word}. Each word must have a minimum of {self.args.min_size} and a maximum of {self.args.max_size} characters."
                message = {"role": "system", "content": content}
                conversation = [message]
                headers = {
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": conversation,
                    "max_tokens": 4096 - len(content)
                }
                response = requests.post(self.gpt_endpoint, headers=headers, json=data)
                response_data = response.json()
                self.add_words_from_string(response_data['choices'][0]['message']['content'])
            logging.info(self.wordlist)
            self.split_subwords()
            self.force_len(3, self.args.max_size)
            self.remove_non_words()
            logging.info(self.wordlist)
            self.add_uppercase_and_leet_variations()
            #logging.info(self.wordlist)
        except Exception as e:
            logging.error(e, exc_info=True)

    def _add_combinations(self, option_list):
        #new_words = set()
            #for combination in product(*option_list):
            #new_words.add(''.join(combination))
            if len(self._wordlist) > self.args.max_words:
                return
            self.wordlist = {''.join(combination) for combination in product(*option_list)}

    def _add_leet_variations(self, word):
        char_options_list = []
        for ch in word:
            options = [ch]
            leet_equiv = self.leet_mapping.get(ch)
            if leet_equiv:
                options.append(leet_equiv)
            char_options_list.append(options)
        self._add_combinations(char_options_list)
    
    def add_uppercase_and_leet_variations(self):
        self.wordlist = {''.join(combination) for word in self._wordlist for combination in product(*[(ch.lower(), ch.upper()) for ch in word])}
        with ThreadPoolExecutor() as executor:
            executor.map(self._add_leet_variations, self.wordlist)

    def insert_chars(self, wordlist, charset, input_min, input_max):
        set_wordlist = set(wordlist)
        for word in wordlist:
            for _ in range(self.args.random_level):
                new_word = word
                num_chars = random.randint(input_min, input_max)
                if len(new_word) + num_chars > self.args.max_size or len(new_word) < 2:
                    continue
                for _ in range(num_chars):
                    char = random.choice(charset)
                    position = random.choices(
                        [0, len(new_word), random.randint(1, len(new_word)-1)], 
                        weights=[0.45, 0.45, 0.1]
                    )[0]
                    new_word = new_word[:position] + char + new_word[position:]
                    set_wordlist.add(new_word)
                    if len(set_wordlist) >= self.args.max_words:
                        logging.warning(f"Wordlist has reached the limit of {self.args.max_words} words. Stopping the word insertion.")
                        return sorted(list(set_wordlist))
        return sorted(list(set_wordlist))

    @staticmethod
    def save_wordlist(wordlist, filename):
        with open(filename, 'w') as file:
            for word in wordlist:
                file.write(word + '\n')
            logging.info(f"A total of {len(wordlist)} words have been saved in {filename}")

if __name__ == '__main__':
    main()