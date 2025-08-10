import argparse
import sys

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', '0': '-----', ' ': '/'
}

def encode(text):
    return ' '.join(MORSE_CODE_DICT.get(c, '') for c in text.upper())

def decode(morse):
    reverse = {v: k for k, v in MORSE_CODE_DICT.items()}
    return ''.join(reverse.get(code, '') for code in morse.split(' '))

def main():
    parser = argparse.ArgumentParser(description="Morse Code Encoder/Decoder")
    parser.add_argument("-e", "--encode", help="Text to encode")
    parser.add_argument("-d", "--decode", help="Morse code to decode")
    args = parser.parse_args()

    if args.encode:
        print(encode(args.encode))
    elif args.decode:
        print(decode(args.decode))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()