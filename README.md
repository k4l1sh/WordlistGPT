
# WordlistGPT

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Make custom wordlists using ChatGPT to generate more words related to words you provide.

<div align="center">
  <img src="https://i.imgur.com/pzOzcUY.png" />
</div>


WordlistGPT is a versatile tool designed to generate wordlists using the ChatGPT API. It provides a wide range of customization options.

## Prerequisites
1. Python 3.x
2. OpenAI API key for accessing the ChatGPT API.

## Usage
Create a .env file with `API_KEY=your_openai_api_key_here` or run the script with the key in the arguments `--key your_openai_api_key_here`
```
python wordlistgpt.py [OPTIONS]
```

### Command Line Arguments
- `-w, --words`: Words to generate wordlist for.
- `-k, --key`: OpenAI API Key.
- `-n, --number`: Number of words to generate in ChatGPT for each word (default: 30).
- `-m, --max-words`: Maximum number of words in the wordlist (default: 5000000).
- `-min, --min-size`: Minimum amount of characters for each word (default: 6).
- `-max, --max-size`: Maximum amount of characters for each word (default: 20).
- `-o, --output`: Output file for the generated wordlist (default: `output.txt`).
- `-u, --uppercase`: Maximum number of characters to convert to uppercase in each word (default: 2).
- `-l, --leet`: Maximum number of leet characters to replace in each word (default: 2).
- `-r, --random-chars`: Maximum range of random characters to be added (default: 2).
- `-rc, --random-charset`: Charset of characters to be randomly added (default: `0123456789!@$&+_-.?/+;#`).

## Features
- Generates wordlists based on user-provided seed words.
- Provides leet speak transformations.
- Offers uppercase transformations for generated words.
- Allows random character insertions with a customizable character set.
- Wordlist size constraints to control the output size.

## More Examples

Customize the maximum number of uppercase, leet and random characters variations
```
$ python wordlistgpt.py -w love -n 10 -u 99 -l 99 -r 16
[+] Generating wordlist for ['love']
[+] Total tokens spent for the word love: 91
[+] Unique words generated from GPT for the word love: 11 [love, infatuation, affectionate, romance, intimacy...]
[+] Wordlist of love extended from 11 to 11 words after adding splitted words
[+] Wordlist of love extended from 11 to 10384 words after adding uppercase variations
[+] Wordlist of love extended from 10384 to 193266 words after adding l33t alphabet combinations
[+] Wordlist of love extended from 193266 to 726866 words after adding 1 to 16 random characters
[+] Wordlist of love shortened from 726866 to 726758 after forcing the wordlist to have the minimum of 6 and a maximum of 20 characters per word
[+] A total of 726758 words have been saved in output.txt
```

Use words generated only from GPT and save it in a custom file
```
$ python wordlistgpt.py -w "artificial intelligence" "large language models" "neural networks" -n 200 -u 0 -l 0 -r 0 -o ai_wordlist.txt
[+] Generating wordlist for ['artificial intelligence', 'large language models', 'neural networks']
[+] Total tokens spent for the word neural networks: 961
[+] Unique words generated from GPT for the word neural networks: 155 [neural networks, von neumann, pattern, deep, active...]
[+] Wordlist of neural networks extended from 155 to 176 words after adding splitted words
[+] Wordlist of neural networks shortened from 176 to 134 after forcing the wordlist to have the minimum of 6 and a maximum of 20 characters per word
[+] Total tokens spent for the word artificial intelligence: 1065
[+] Unique words generated from GPT for the word artificial intelligence: 183 [artificial intelligence, robotic, generative adversarial networks, knowledgeable, information retrieval...]
[+] Wordlist of artificial intelligence extended from 183 to 302 words after adding splitted words
[+] Wordlist of artificial intelligence shortened from 302 to 236 after forcing the wordlist to have the minimum of 6 and a maximum of 20 characters per word
[+] Total tokens spent for the word large language models: 1363
[+] Unique words generated from GPT for the word large language models: 205 [large language models, reinforcement learning for dialogue systems, generative adversarial networks, grammatical error correction, word embeddings...]
[+] Wordlist of large language models extended from 205 to 452 words after adding splitted words
[+] Wordlist of large language models shortened from 452 to 276 after forcing the wordlist to have the minimum of 6 and a maximum of 20 characters per word
[+] A total of 519 words have been saved in ai_wordlist.txt
```

Generate a wordlist without GPT and with a custom random charset
```
$ python wordlistgpt.py -w 123456789 -n 0 -r 10 -rc '!@#$%' -rl 9999
[+] Generating wordlist for ['123456789']
[+] Wordlist of 123456789 extended from 1 to 1 words after adding splitted words
[+] Wordlist of 123456789 extended from 1 to 1 words after adding uppercase variations
[+] Wordlist of 123456789 extended from 1 to 1 words after adding l33t alphabet combinations
[+] Wordlist of 123456789 extended from 1 to 27110 words after adding 1 to 10 random characters
[+] Wordlist of 123456789 shortened from 27110 to 27110 after forcing the wordlist to have the minimum of 6 and a maximum of 20 characters per word
[+] A total of 27110 words have been saved in output.txt
```



## Contributing
Contributions are welcome! Please feel free to submit pull requests or raise issues.

## License
MIT License
