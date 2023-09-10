
# WordlistGPT

[![Releases](https://img.shields.io/github/release/k4l1sh/WordlistGPT.svg)](https://github.com/k4l1sh/WordlistGPT/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Make custom wordlists using ChatGPT in seconds:

![WordlistGPT Example](https://i.imgur.com/Cs50k52.png)

## Features
- Use of ChatGPT to generate related words.
- Fast generation of uppercase variations, l33t variations and characters insertion.
- Customizable word sizes, batch saving, and more.

## Usage
Try wordlistgpt.py with 'harry potter':
```bash
git clone https://github.com/k4l1sh/WordlistGPT.git
cd WordlistGPT
python wordlistgpt.py -w 'harry potter'
```

You can also run directly from url if you are feeling lazy:
```bash
curl -sSL https://raw.githubusercontent.com/k4l1sh/WordlistGPT/main/wordlistgpt.py | python - -w 'harry potter'
```
A file named `wordlist.txt` will be created with the generated wordlist.

To take advantage of ChatGPT to generate related words, you need to get an OpenAI API key from [OpenAI API keys](https://platform.openai.com/account/api-keys).

After getting an OpenAI API key, create an .env file with `API_KEY=your_openai_api_key_here` or run the script with OpenAI API key in the arguments `--key your_openai_api_key_here`.

## Wordlist Generation Process

The Wordlist Generator follows a systematic process to generate a wordlist that is suitable for different purposes. Here's a step-by-step breakdown of how the wordlist is created:

1. **Words from GPT**: 
    - For each word in the user-specified list, the generator makes an API call to OpenAI GPT, requesting related words.
    - The generator adds the response from GPT to the wordlist.

2. **Word Cleaning and Adjusting**:
    - Subwords from each word are split and added to the wordlist.
    - Non-word characters within the wordlist are stripped off, ensuring only clean words remain.

3. **Uppercase Variations**: 
    - For each word in the wordlist, variations are created by changing the case of the characters.
    - The variations are added to the wordlist

4. **Leet Variations**: 
    - Leet variations are generated based on a predefined leet mapping.
    - For each word in the wordlist, variations with leet characters are added to the wordlist.

5. **Insert Deterministic Characters**:
    - Deterministic characters, which are predefined sets of characters, can be inserted in the wordlist words.
    - These characters can be added to the left, right, or nested within the words based on user-defined positions.

6. **Insert Random Characters**: 
    - Random characters from a defined charset can be inserted into the words at random positions.
    - The number of random insertions and the level of randomness are both defined by user parameters.

## Argument Details
- `-w, --words`: Words to generate the wordlist for
- `-n, --number`: Number of words to generate in ChatGPT for each word. (default: 20)
- `-min, --min-size`: Minimum number of characters for each word. (default: 6)
- `-max, --max-size`: Maximum number of characters for each word. (default: 14)
- `-m, --max-words`: Maximum number of words in the wordlist if not batched. (default: 10000000)
- `-b, --batch_size`: Batch size for wordlist processing. (default: 1000000)
- `-d, --deterministic-chars`: Number of deterministic characters to be added. (default: 2)
- `-dc, --deterministic-charset`: Charset of deterministic characters to be added. (default: '0123456789_!@$%#')
- `-dp, --deterministic-position`: Position for inserting deterministic characters (default: ['left', 'right'])
- `-u, --uppercase`: Maximum number of characters to convert to uppercase in each word. (default: inf)
- `-l, --leet`: Maximum number of leet characters to replace in each word. (default: inf)
- `-lm, --leet-mapping`: JSON-formatted leet mapping dictionary. (default: provided)
- `-r, --random-chars`: Maximum range of random characters to be added. (default: 3)
- `-rc, --random-charset`: Charset of characters to be randomly added. (default: '0123456789!@$&+_-.?/+;#')
- `-rl, --random-level`: Number of iterations of random characters to be added. (default: 1)
- `-rw, --random-weights`: Weights for determining position of random character insertion. (default: 0.47, 0.47, 0.06)
- `-k, --key`: OpenAI API Key. (default: None)
- `-o, --output`: Output file for the generated wordlist. (default: `wordlist.txt`)
- `-v, --debug`: If True, enable debug logging. (default: False)
- `-s, --silent`: If True, disable logging. (default: False)

## More Examples

---
### Generate words related to "love"
- Get 50 words related to "love" from ChatGPT.
- Words can have at least 4 characters.
- Apply a maximum of 2 uppercase and leet variations.
```bash
python wordlistgpt.py -w 'love' -n 50 -min 4 --uppercase 2 --leet 2
```
---
### Create wordlist from "change" 
- Base word: "change"
- No related words from ChatGPT.
- No random characters insertion.
- Add up to 5 deterministic characters from the charset '0123456789_!@$%#' to be added only in the right.
```bash
python wordlistgpt.py -w 'change' -n 0 -r 0 -d 5 -dc '0123456789_!@$%#' -dp 'right'
```
---
### AI and cybersecurity related words
- Get 200 words each related to "artificial intelligence" and "cybersecurity".
- Limit words to 30 characters.
- Remove all leet, uppercase, deterministic and random characters variations.
- Save the list to "ai_wordlist.txt".
```bash
python wordlistgpt.py -w 'artificial intelligence' 'cybersecurity ' -n 200 -max 30 -u 0 -l 0 -d 0 -r 0 -o ai_wordlist.txt
```
---
### Create wordlist from "qwerty" 
- Base word: "qwerty"
- No related words from ChatGPT.
- Remove leet and random variations
- Add up to 3 deterministic characters from the charset 'abcdefghijklmnopqrstuvwxyz0123456789_!@$%#' to be added in the left and right.
- Save the results in "qwerty_wordlist.txt".
```bash
python wordlistgpt.py -w qwerty -n 0 -l 0 -d 3 -r 0 -dc 'abcdefghijklmnopqrstuvwxyz0123456789_!@$%#' -o qwerty_wordlist.txt
```
---
### Custom wordlist from "0123456789"
- Base word: "0123456789"
- Add up to 3 random characters from "!@#$%" iterating this process 999 times, inserting it only in the end.
```bash
python wordlistgpt.py -w '0123456789' -n 0 -d 0 --random-chars 3 --random-charset '!@#$%' --random-level 999 --random-weights 0 1 0
```
---
### Create wordlist for words related to "marvel" running from URL
- Fetch and run the script directly from URL.
- Generate words related to "marvel" using default configurations.
- Use your OpenAI API key in the arguments.
```bash
curl -sSL https://raw.githubusercontent.com/k4l1sh/WordlistGPT/main/wordlistgpt.py | python3 - -w marvel -k your_openai_api_key_here
```
---
## Contributing
Contributions are welcome! Please feel free to submit pull requests or raise issues.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
