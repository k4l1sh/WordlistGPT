
# WordlistGPT

[![Releases](https://img.shields.io/github/release/k4l1sh/WordlistGPT.svg)](https://github.com/k4l1sh/WordlistGPT/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Make custom wordlists using ChatGPT in seconds:

![WordlistGPT Example](https://i.imgur.com/Cs50k52.png)

## Features
- Use of ChatGPT to generate related words.
- Fast generation of uppercase and l33t variations.
- Customizable word sizes, random character insertion, and more.

## Usage
Try wordlistgpt.py with a hello world:
```bash
git clone https://github.com/k4l1sh/WordlistGPT.git
cd WordlistGPT
python wordlistgpt.py -w 'hello world'
```

You can also run directly from url if you are feeling lazy:
```bash
curl -sSL https://raw.githubusercontent.com/k4l1sh/WordlistGPT/main/wordlistgpt.py | python - -w 'hello world'
```
A file named `wordlist.txt` will be created with the generated wordlist.

To take advantage of ChatGPT to generate related words, you need to get an OpenAI API key from [OpenAI API keys](https://platform.openai.com/account/api-keys).

After getting an OpenAI API key, create an .env file with `API_KEY=your_openai_api_key_here` or run the script with OpenAI API key in the arguments `--key your_openai_api_key_here`.

### Argument Details
- `-w, --words`: Words to generate the wordlist for
- `-n, --number`: Number of words to generate in ChatGPT for each word. (default: 20)
- `-min, --min-size`: Minimum number of characters for each word. (default: 6)
- `-max, --max-size`: Maximum number of characters for each word. (default: 14)
- `-m, --max-words`: Maximum number of words in the wordlist if not batched. (default: 10000000)
- `-b, --batch_size`: Batch size for wordlist processing. (default: 1000000)
- `-d, --deterministic-chars`: Number of deterministic characters to be added. (default: 2)
- `-dc, --deterministic-charset`: Charset of deterministic characters to be added. (default: provided)
- `-dp, --deterministic-position`: Position for inserting deterministic characters (default: ['left', 'right'])
- `-u, --uppercase`: Maximum number of characters to convert to uppercase in each word. (default: inf)
- `-l, --leet`: Maximum number of leet characters to replace in each word. (default: inf)
- `-lm, --leet-mapping`: JSON-formatted leet mapping dictionary. (default: provided)
- `-r, --random-chars`: Maximum range of random characters to be added. (default: 3)
- `-rc, --random-charset`: Charset of characters to be randomly added. (default: provided)
- `-rl, --random-level`: Number of iterations of random characters to be added. (default: 1)
- `-rw, --random-weights`: Weights for determining position of random character insertion. (default: 0.47, 0.47, 0.06)
- `-k, --key`: OpenAI API Key. (default: None)
- `-o, --output`: Output file for the generated wordlist. (default: `wordlist.txt`)
- `-d, --debug`: If True, enable debug logging. (default: False)
- `-s, --silent`: If True, disable logging. (default: False)

## More Examples

Generate 50 related words to 'love' from ChatGPT, set the minimum characters to 4 and maximum uppercase and leet variations to 2:
```bash
python wordlistgpt.py -w 'love' -n 50 -min 4 --uppercase 2 --leet 2
```

Generate 200 related words each for 'artificial intelligence' and 'cybersecurity' from ChatGPT, without any leet speak, uppercase, or random character variations, with a maximum word length of 30 and save it in a custom file 'ai_wordlist.txt':
```bash
python wordlistgpt.py -w 'artificial intelligence' 'cybersecurity '-n 200 -max 30 -u 0 -l 0 -r 0 -o ai_wordlist.txt
```

Generate a wordlist based on the word '0123456789' without ChatGPT, use a maximum range of 10 random characters to be added with a custom random charset of '!@#$%' and random level to iterate 99999 times with the random characters variations to be inserted only in the end of the word:
```bash
python wordlistgpt.py -w '0123456789' -n 0 -max 20 --random-chars 10 --random-charset '!@#$%' --random-level 99999 --random-weights 0 1 0
```

Run wordlistgpt.py directly from url for the word 'marvel' with the default configurations and your OpenAI API key:
```bash
curl -sSL https://raw.githubusercontent.com/k4l1sh/WordlistGPT/main/wordlistgpt.py | python3 - -w marvel -k your_openai_api_key_here
```

## Contributing
Contributions are welcome! Please feel free to submit pull requests or raise issues.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
