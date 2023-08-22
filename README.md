
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
Create a .env file with `API_KEY=your_openai_api_key_here` or run the script with openai api key in the arguments `--key your_openai_api_key_here`
```
python wordlistgpt.py [OPTIONS]
```
or generate a wordlist directly from url
```
curl -sSL https://raw.githubusercontent.com/k4l1sh/WordlistGPT/main/wordlistgpt.py | python - [OPTIONS]
```

### Command Line Arguments
- `-w, --words`: Words to generate wordlist for.
- `-k, --key`: OpenAI API Key.
- `-n, --number`: Number of words to generate in ChatGPT for each word (default: 30).
- `-m, --max-words`: Maximum number of words in the wordlist (default: 5000000).
- `-min, --min-size`: Minimum amount of characters for each word (default: 6).
- `-max, --max-size`: Maximum amount of characters for each word (default: 20).
- `-o, --output`: Output file for the generated wordlist (default: output.txt).
- `-u, --uppercase`: Maximum number of characters to convert to uppercase in each word (default: 2).
- `-l, --leet`: Maximum number of leet characters to replace in each word (default: 2).
- `-r, --random-chars`: Maximum range of random characters to be added (default: 2).
- `-rc, --random-charset`: Charset of characters to be randomly added (default: 0123456789!@$&+_-.?/+;#).

## Features
- Generates wordlists based on user-provided seed words.
- Provides leet speak transformations.
- Offers uppercase transformations for generated words.
- Allows random character insertions with a customizable character set.
- Wordlist size constraints to control the output size.

## More Examples

Customize the maximum number of uppercase, leet and random characters variations
```
python wordlistgpt.py -w love -n 10 -u 99 -l 99 -r 16
```

Use words generated only from GPT and save it in a custom file
```
python wordlistgpt.py -w 'artificial intelligence' 'large language models' 'neural networks' -n 200 -u 0 -l 0 -r 0 -o ai_wordlist.txt
```

Generate a wordlist without GPT and with a custom random charset
```
python wordlistgpt.py -w 123456789 -n 0 -r 10 -rc '!@#$%' -rl 9999
```

Run wordlistgpt.py directly from url
```
curl -sSL https://raw.githubusercontent.com/k4l1sh/WordlistGPT/main/wordlistgpt.py | python3 - -w marvel -k your_openai_api_key_here
```


## Contributing
Contributions are welcome! Please feel free to submit pull requests or raise issues.

## License
MIT License
