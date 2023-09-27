import re

def is_roman_numeral(s):
    # Si no son palabras que parezcan numero romanos quitamos
    if s.upper() not in ['MIX', 'I', 'DIV', 'DIX']:
        pattern = '^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$'
        return bool(re.match(pattern, s.upper()))

if __name__ == '__main__':
    input_text = input('Enter the input text file path: ')

    with open(input_text, 'r') as infile:
        output_text = input('Enter the output text file name: ')
        with open(output_text, 'w') as outfile:
            for line in infile:
                if ',' in line:
                    number, word = line.strip().split(', ')
                    # print(word)
                    # if is_roman_numeral(word):
                    #    print(word)
                    if re.match("^[a-zA-Z]*'?[a-zA-Z]*$", word) and not is_roman_numeral(word):
                        outfile.write(number+', '+word + '\n')