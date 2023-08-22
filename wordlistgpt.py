import concurrent.futures
import logging
import argparse
import random
import requests
import re
import os

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
    parser.add_argument('-m', '--max-words', type=int, default=5000000, help='Maximum number of words in the wordlist')
    parser.add_argument('-min', '--min-size', type=int, default=6, help='Minimum amount of characters for each word')
    parser.add_argument('-max', '--max-size', type=int, default=20, help='Maximum amount of characters for each word')
    parser.add_argument('-k', '--key', type=str, help='OpenAI API Key')
    parser.add_argument('-o', '--output', type=str, default='output.txt', help='Output file for the generated wordlist')
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
        self.wordlist = []
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

    def orchestrate_threads(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            logging.info(f"Generating wordlist for {self.args.words}")
            futures = {executor.submit(self.generate_wordlist, word, self.args.number): word for word in self.args.words}
            for future in concurrent.futures.as_completed(futures):
                if len(self.wordlist) >= self.args.max_words:
                    logging.warning(f"Wordlist has reached the limit of {self.args.max_words} words. Stopping the generation.")
                    break
                word = futures[future]
                try:
                    self.wordlist.extend(future.result())
                except Exception as e:
                    logging.error(f"Error generating wordlist for '{word}': {e}", exc_info=True)
            self.wordlist = sorted(list(set(self.wordlist)))

    def generate_wordlist(self, word, num_words):
        wordlist = [word]
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
            logging.info(f"Total tokens spent for the word {word}: {response_data['usage']['total_tokens']}")
            wordlist.extend(self.make_list_from_words_string(response_data['choices'][0]['message']['content']))
            logging.info(f"Unique words generated from GPT for the word {word}: {len(wordlist)} [{', '.join(wordlist[:5])}...]")
        old_len = len(wordlist)
        wordlist = self.split_subwords(wordlist)
        wordlist = self.remove_non_words_characters(wordlist)
        logging.info(f"Wordlist of {word} extended from {old_len} to {len(wordlist)} words after adding splitted words")
        if self.args.uppercase > 0:
            old_len = len(wordlist)
            wordlist = self.words_to_uppercase(wordlist)
            logging.info(f"Wordlist of {word} extended from {old_len} to {len(wordlist)} words after adding uppercase variations")
        if len(wordlist) >= self.args.max_words:
            return wordlist[:self.args.max_words]
        if self.args.leet > 0:
            old_len = len(wordlist)
            wordlist = self.words_to_leet(wordlist)
            logging.info(f"Wordlist of {word} extended from {old_len} to {len(wordlist)} words after adding l33t alphabet combinations")
        if len(wordlist) >= self.args.max_words:
            return wordlist[:self.args.max_words]
        if self.args.random_chars > 0:
            old_len = len(wordlist)
            wordlist = self.insert_chars(wordlist, self.args.random_charset, 1, self.args.random_chars)
            logging.info(f"Wordlist of {word} extended from {old_len} to {len(wordlist)} words after adding 1 to {self.args.random_chars} random characters")
        old_len = len(wordlist)
        wordlist = self.force_min_len(wordlist, self.args.min_size)
        wordlist = self.force_max_len(wordlist, self.args.max_size)
        logging.info(f"Wordlist of {word} shortened from {old_len} to {len(wordlist)} after forcing the wordlist to have the minimum of {self.args.min_size} and a maximum of {self.args.max_size} characters per word")
        return wordlist
    
    @staticmethod
    def make_list_from_words_string(words):
        return list(set(word.strip().rstrip('.').lower() for word in re.findall(r'''[\d\r\n-]*\.?\s?([\w \-\.'"]+)''', words)))
    
    @staticmethod
    def split_subwords(wordlist):
        return list(set(wordlist+[subword for word in wordlist for subword in re.split(r'\W+', word)]))
    
    @staticmethod
    def force_min_len(wordlist, word_len):
        return [word for word in wordlist if len(word) >= word_len]
    
    @staticmethod
    def force_max_len(wordlist, word_len):
        return [word for word in wordlist if len(word) <= word_len]
    
    @staticmethod
    def remove_non_words_characters(wordlist):
        return list(set(re.sub(r'\W', '', word) for word in wordlist))

    def generate_leet_combinations(self, word, leet_count=0):
        if leet_count > self.args.leet:
            return [word]
        if not word:
            return ['']
        rest = self.generate_leet_combinations(word[1:], leet_count)  
        if word[0].lower() in self.leet_mapping:
            leet_sub = self.generate_leet_combinations(word[1:], leet_count + 1)
            leet_list = [word[0] + combination for combination in rest] + [self.leet_mapping[word[0].lower()] + combination for combination in leet_sub]
            return leet_list[:self.args.max_words]
        else:
            return [word[0] + combination for combination in rest]
            
    def generate_uppercase_combinations(self, word, uppercase_count=0):
        if uppercase_count > self.args.uppercase:
            return [word]
        if not word:
            return [''] 
        rest = self.generate_uppercase_combinations(word[1:], uppercase_count)  
        if word[0].islower():
            upper_sub = self.generate_uppercase_combinations(word[1:], uppercase_count + 1)
            upper_list = [word[0] + combination for combination in rest] + [word[0].upper() + combination for combination in upper_sub]
            return upper_list[:self.args.max_words]
        else:
            return [word[0] + combination for combination in rest]

    def words_to_leet(self, wordlist):
        leet_wordlist = []
        for word in wordlist:
            leet_wordlist.extend(self.generate_leet_combinations(word, 0))
        return list(set(leet_wordlist))[:self.args.max_words]
    
    def words_to_uppercase(self, wordlist):
        uppercase_wordlist = []
        for word in wordlist:
            uppercase_wordlist.extend(self.generate_uppercase_combinations(word, 0))
        return list(set(uppercase_wordlist))[:self.args.max_words]

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