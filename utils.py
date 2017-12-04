def phone_standard(text):
    text1 = text.replace('(', '')
    text1 = text1.replace(')', '')
    text1 = text1.replace('-', '')
    text1 = text1.replace(' ', '')
    if len(text1) == 11 and text1[0] == '8':  # 89000000000 format
        text1 = '7' + text1[1:]
    elif len(text1) == 12 and text1[0] == '+' and text1[1] == '7':  # +79000000000 format
        text1 = text1[1:]
    elif len(text1) == 10 and text1[0] == '9':  # 9000000000 format
        text1 = '7' + text1
    elif len(text1) == 11 and text1[0] == '7':  # 79000000000 format
        pass
    else:
        return ''
    return text1