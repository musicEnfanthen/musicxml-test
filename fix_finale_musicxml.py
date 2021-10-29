import os, shutil
from lxml import etree  # pip install lxml
from natsort import natsorted # pip install natsort

# this program is intended to analyze a musicXML-file for errors that might have occured
# during an export from Finale (using the Dolet-plugin) and fix a few of them
#
# currently only 'shape articulation 20' and 'shape articulation 22' will be fixed, the others
# are either too obscure or not easily fixable with a script, but hopefully the three
# 'error-analysis' txt-files will be helpful to find issues – and either fix them by hand (enjoy)
# or possibly prevent them from happening in Finale
#
# comparisons have been made between a pdf-export from Finale and a rendering of the musicXML
# using the Verovio toolkit in Python (https://book.verovio.org/toolkit-reference/toolkit-methods.html#rendertosvgfile)
#
#
# here are some more errors whose 'appearance' has been tracked down:
# – shape expression 96 & 97: likely square brackets (for editorial indication) around elements
#       above the note text (e.g. around the '3' for triplets or a 'ppp')
# – unknown beam extension: beams across bars, possibly also connected to a row change at that bar


def listXMLFiles () -> str:
    # list files in the current directory and ask for a file name
    # (this and the following functions asking for user input are far from foolproof)
    print ('Here is a list of possible files in the current directory:')
    for file in os.listdir('.'):
        if file.endswith('.xml') or file.endswith('.musicxml') or file.endswith('.mxml'):
            print('-', file)
    while True:
        filename = input('\nPlease provide the (relative) path of the file you would like to analyze.\n(feel free to copy & paste any of the above)\n')
        if filename.endswith('.xml') or filename.endswith('.musicxml') or filename.endswith('.mxml'):
            return filename
        else:
            print('invalid file')


def createErrorFiles (filename: str) -> None:

    # create a folder for the error files
    folder_name = 'error-files'
    if folder_name in os.listdir():
        if input(f'It appears there already is a folder "{folder_name}" in this directory; would you like to overwrite it? (y/n)') == 'y':
            shutil.rmtree(folder_name)
        else:
            return None
    os.makedirs(folder_name)
    print(f'created directory {folder_name}')

    # open the chosen file and proceed to create several insightful files
    with open (filename, 'r') as input_file:
        err_list_file_name = folder_name + '/' + filename.split('.')[0] + ('_errorlist.txt')
        with open (err_list_file_name, 'w') as output1:

            # get all problematic lines (signaled by the error ?DoletFinale)
            # and write them to a file
            err_list = [line.strip() for line in input_file if '?DoletFinale' in line]
            for item in err_list:
                output1.write(item+'\n')
            print(f'created file "{err_list_file_name}"')

            # put the errors in a dictionary according to error and count occurrences
            # create an additional dictionary which contains the errorcodes as keys and
            # all location information as values
            # also format the to-be-written values
            err_score_dict = {}
            err_dict = {}
            for item in err_list:
                wordlist = str(item).split(' ')
                err_code = ''
                err_location = ''
                for word in wordlist[1:4]:
                    err_code += word+' '
                err_code = err_code.strip(' ')
                for word in wordlist[4:]:
                    err_location += word+' '
                err_location = err_location.strip(' ?>')

                if err_code not in err_score_dict.keys():
                    err_score_dict[err_code] = 1
                    err_dict[err_code] = [err_location]
                else:
                    err_score_dict[err_code] += 1
                    err_dict[err_code].append(err_location)

            # write the 'scoreboard' dictionary to a file
            err_scores_file_name = folder_name + '/' + filename.split('.')[0] + ('_errorscores.txt')
            with open (err_scores_file_name, 'w') as output2:
                err_dict_sorted = {}
                for err in sorted(err_score_dict, key=err_score_dict.get, reverse=True):                   
                    err_dict_sorted[err] = err_score_dict[err]
                for item in err_dict_sorted:
                    output2.write(item+': '+str(err_dict_sorted[item])+'\n')
            print(f'created file "{err_scores_file_name}"')

            # write the 'location' dictionary sorted by first occurence to a file
            err_locations_file_name = folder_name + '/' + filename.split('.')[0] + ('_errorssortedbylocation.txt')
            with open (err_locations_file_name, 'w') as output3:
                for key in err_dict.keys():
                    output3.write(key+':\n')
                    for value in err_dict[key]:
                        output3.write(' - '+value+'\n')
                    output3.write('\n')
            print(f'created file "{err_locations_file_name}"')

            # write the 'location' dictionary sorted by error-code to a file
            err_locations2_file_name = folder_name + '/' + filename.split('.')[0] + ('_errorssortedbyerror.txt')
            with open (err_locations2_file_name, 'w') as output4:
                for key in natsorted(err_dict):
                    output4.write(key+':\n')
                    for value in err_dict[key]:
                        output4.write(' - '+value+'\n')
                    output4.write('\n')
            print(f'created file "{err_locations_file_name}"')


def createFixedFile (filename: str) -> None:
# (using lxml as elementTree cannot select processing instructions)
# (currently only all at once)

    # read in the desired file with etree
    tree = etree.parse(filename)
    root = tree.getroot()

    # get all the export errors – signified by the XML-processing-instruction ?DoletFinale
    # and implement fixes for specific known errors
    export_errors = tree.xpath('//processing-instruction()')
    for item in export_errors:

        # 'shape articulation 20' appears to be the missing slash on a short suspension note
        # as musicXML has an option to codify that, the fix is as follows:
        # find all 'shape articulation 20', search for the <note> element among the ancestors
        # go into it's <grace> child element, add the attribute 'slash="yes"'
        # and finally remove the error message
        #
        # 'shape articulation 22' is pretty much the same as 20, just for a different note
        # orientation (downwards stem)
        if 'Shape articulation 20' in str(item) or 'Shape articulation 22' in str(item):
            for parent in item.iterancestors('note'):
                parent.find('grace').set('slash', 'yes')
            etree.strip_elements(item.getparent(), item.tag)
        
    # write the 'fixed' resulting musicXML to a new file
    fixed_file_name = filename.split('.')[0] + ('_fixed.') + filename.split('.')[1]
    with open (fixed_file_name, 'wb') as f:
        f.write(etree.tostring(root, pretty_print=True))
    print(f'created file "{fixed_file_name}"')



# run the program in a sensible sequence
filename = listXMLFiles()
# ask whether error-analysis files should be created, triggering the corresponding actions
if input('Would you like to create error-analysis files? (y/n)') == 'y':
    createErrorFiles(filename)
# ask whether the implemented fixes should be applied
if input('Would you like to create a file with all currently implemented fixes? (y/n)') == 'y':
    createFixedFile(filename)
# state that this program has ceased doing stuff
print('done')