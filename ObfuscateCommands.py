# Copyright [2021] [Intrinsec]
# Program written by Dany GIANG aka CyberMatters

import argparse
import sys
import logging
import base64
import re
import pandas as pd

logger = logging.getLogger(__name__)

def clean_dataset(df):

    logger.info("Cleaning dataset ...\n")
    pattern_command_ok = re.compile(r'^\*[^\*]+\*$') # Regex that matches a string that starts with a wildcard, ends with a wildcard, does not contain any other wildcards.
    cpt = 0
    len_df = len(df)

    while cpt < len_df:

        if (re.fullmatch(pattern_command_ok, df.at[cpt,'command'], flags=0) == None) or (len(df.at[cpt,'command']) < 7) : # drop the rows in which the command is shorter than 7 caracters or does not match the previously defined regex.
            df = df.drop(index=cpt)
        else:
            df.at[cpt,'command'] = re.sub('\*', '', df.at[cpt,'command']) # delete the wildcards

        cpt += 1

    df.reset_index(drop=True,inplace=True) 

    cols_to_keep = ['command','description']
    df = df.loc[:, cols_to_keep]

    logger.info("=> OK\n")

    return df

def base64_encode(df_clean, df_final, cpt_clean, cpt_final):

    add_char = [' ', '&', '|', ';', ',']

    encode_String64 = ""
    data_to_encode = df_clean.at[cpt_clean, 'command']
    encoded_Bytes64 = base64.b64encode(data_to_encode.encode("utf-8"))
    temp_encode_String64 = str(encoded_Bytes64, "utf-8")
    
    for char in range(0, len(temp_encode_String64)):

        encode_String64 = encode_String64 + temp_encode_String64[char]      
    
    df_final.at[cpt_final, 'obfuscated_command'] = "*" + encode_String64 + "*"
    df_final.at[cpt_final, 'encoding_type'] = "base_64"
    df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'

    cpt_final += 1
    encode_String64 = ""
    
    #1 character preceding data_to_encode

    for item in add_char :
        data_to_encode = item + df_clean.at[cpt_clean, 'command']
        encoded_Bytes64 = base64.b64encode(data_to_encode.encode("utf-8"))
        temp_encode_String64 = str(encoded_Bytes64, "utf-8")
        
        for char in range(0, len(temp_encode_String64)):

            encode_String64 = encode_String64 + temp_encode_String64[char]
        
        df_final.at[cpt_final, 'obfuscated_command'] = "*" + encode_String64 + "*"
        df_final.at[cpt_final, 'encoding_type'] = "base_64"
        df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
        
        cpt_final += 1
        encode_String64 = ""
    
    #1 character succeeding data_to_encode

    for item in add_char :

        data_to_encode = df_clean.at[cpt_clean, 'command'] + item 
        encoded_Bytes64 = base64.b64encode(data_to_encode.encode("utf-8"))
        temp_encode_String64 = str(encoded_Bytes64, "utf-8")
        
        for char in range(0, len(temp_encode_String64)):

            encode_String64 = encode_String64 + temp_encode_String64[char]

        df_final.at[cpt_final, 'obfuscated_command'] = "*" + encode_String64 + "*"
        df_final.at[cpt_final, 'encoding_type'] = "base_64"
        df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
        
        cpt_final += 1
        encode_String64 = ""
    
    #2 characters preceding data_to_encode

    for item1 in add_char:
        for item2 in add_char:
            data_to_encode = item1 + item2 + df_clean.at[cpt_clean, 'command'] 
            encoded_Bytes64 = base64.b64encode(data_to_encode.encode("utf-8"))
            temp_encode_String64 = str(encoded_Bytes64, "utf-8")
            
            for char in range(0, len(temp_encode_String64)):
                encode_String64 = encode_String64 + temp_encode_String64[char]
            
            df_final.at[cpt_final, 'obfuscated_command'] = "*" + encode_String64 + "*"
            df_final.at[cpt_final, 'encoding_type'] = "base_64"
            df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
        
            cpt_final += 1
            encode_String64 = ""
    
    #1 character preceding data_to_encode + 1 caracter succeeding

    for item1 in add_char:
        for item2 in add_char:
            data_to_encode = item1 + df_clean.at[cpt_clean, 'command'] + item2
            encoded_Bytes64 = base64.b64encode(data_to_encode.encode("utf-8"))
            temp_encode_String64 = str(encoded_Bytes64, "utf-8")
            
            for char in range(0, len(temp_encode_String64)):
                encode_String64 = encode_String64 + temp_encode_String64[char]
            
            df_final.at[cpt_final, 'obfuscated_command'] = "*" + encode_String64 + "*"
            df_final.at[cpt_final, 'encoding_type'] = "base_64"
            df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
        
            cpt_final += 1
            encode_String64 = ""

    return cpt_final
    
def hex_encode(df_clean, df_final, cpt_clean, cpt_final):

    data_to_encode = df_clean.at[cpt_clean, 'command'] 
    encoded_Bytes = data_to_encode.encode("utf-8")
    encode_String_hex = encoded_Bytes.hex()
    
    df_final.at[cpt_final, 'obfuscated_command'] = "*" + encode_String_hex + "*"
    df_final.at[cpt_final, 'encoding_type'] = "hex"
    df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
    
    return cpt_final + 1
    
def ascii_encode(df_clean, df_final, cpt_clean, cpt_final):

    data_to_encode = df_clean.at[cpt_clean, 'command'] 
    result=''

    for char in data_to_encode:
        result += str(ord(char)) + ' '

    df_final.at[cpt_final, 'obfuscated_command'] = "*" + result[:len(result)-1] + "*"
    df_final.at[cpt_final, 'encoding_type'] = "ascii"
    df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
    
    return cpt_final + 1

def rot_encode(df_clean, df_final, cpt_clean, cpt_final):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    
    data_to_encode = df_clean.at[cpt_clean, 'command'] 
    data_to_encode = data_to_encode.lower()
    result = ''
    
    for rot in range(1,26) :       
        result=''
        
        for char in data_to_encode:
            if char.isalpha():
                result += alphabet[(alphabet.index(char) + rot) % 26]
                
            else:
                result += char
       
        df_final.at[cpt_final, 'obfuscated_command'] = "*" + result + "*"
        df_final.at[cpt_final, 'encoding_type'] = "rot_" + str(rot)
        df_final.at[cpt_final, 'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'

        cpt_final = cpt_final + 1
        
    return cpt_final   

def encode(df_clean, df_final):

    logger.info("Encoding data ...\n")
    len_df_clean = len(df_clean)
    cpt_clean = 0
    cpt_final = 0
    
    while cpt_clean < len_df_clean : #For each row in the clean dataframe

        df_final.at[cpt_final,'obfuscated_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'
        df_final.at[cpt_final,'encoding_type'] = "plain_text"
        df_final.at[cpt_final,'plain_text_command'] = '*' + df_clean.at[cpt_clean, 'command'] + '*'

        cpt_final += 1
        
        cpt_final = base64_encode(df_clean, df_final, cpt_clean, cpt_final)
        cpt_final = hex_encode(df_clean, df_final, cpt_clean, cpt_final)
        cpt_final = ascii_encode(df_clean, df_final, cpt_clean, cpt_final)
        cpt_final = rot_encode(df_clean, df_final, cpt_clean, cpt_final)

        cpt_clean += 1

    logger.info("=> OK\n")

    return df_final

def retrieve_description(filePath1, df_final):

    logger.info("Retrieving description ...\n")

    df_initial = pd.read_csv(filePath1)
    len_final = len(df_final)
    cpt_final = 0

    while cpt_final < len_final :

        cpt_initial = 0
        done = False
        
        while done != True :
        
            if df_final.at[cpt_final,'plain_text_command'] == df_initial.at[cpt_initial,'command'] :
            
                df_final.at[cpt_final,'description'] = df_initial.at[cpt_initial,'description']
                df_final.at[cpt_final,'FE'] = df_initial.at[cpt_initial,'FE']
                df_final.at[cpt_final,'TTP'] = df_initial.at[cpt_initial,'TTP']
                
                done = True
                
            else :
                cpt_initial = cpt_initial + 1
        
        cpt_final = cpt_final + 1

    logger.info("=> OK\n")

    return df_final

#************************ MAIN *****************************

def main(argv):

    inputFile = ''
    outputFile = ''

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="-i is followed by the path of the input file which contains the plaintext commands and description", required=True)
    parser.add_argument("-o", "--output", help="-o is followed by the path of the output file path which will contain the obfuscated commands and description", required=True)
    args = parser.parse_args()
           
    filePath1 = args.input
    finalFilePath = args.output

    logging.basicConfig(level=logging.INFO)

    df = pd.read_csv(filePath1)
    
    # Call function that cleans dataset
    df_clean = clean_dataset(df)

    # Create the dataframe that will contain the obfuscated commands and associated descriptions
    data = {'obfuscated_command':['a'],'encoding_type':['b'],'plain_text_command':['c'],'description':['d'],'FE':['e'],'TTP':['f']}
    df_final = pd.DataFrame(data)

    df_final = encode(df_clean, df_final)

    df_final = retrieve_description(filePath1, df_final)

    df_final.to_csv(finalFilePath, index=False)

    logger.info("The program terminated successfully ;)")

if __name__=="__main__":
    main(sys.argv[1:])      