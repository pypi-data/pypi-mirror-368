import subprocess
import pandas as pd
from .common_dictionaries import TITLE_LEVELS

def display_as_dataframe(metadata_md='metadata.md',
                         working_dir='./'):
    """
    Writes the ``eml.xml`` file from the metadata markdown file into your current working directory.  
    The ``eml.xml`` file is the metadata file containing things like authorship, licence, institution, 
    etc.

    Parameters
    ----------
        ``metadata_md``: ``str``
            Name of the markdown file that you want to convert to EML.  Default value is ``'metadata.md'``.
        ``working_dir``: ``str``
            Name of your working directory.  Default value is ``'./'``.
                
    Returns
    -------
        ``pandas dataframe`` denoting all the information in the metadata file
    """
    # check for last line
    number_lines = int(subprocess.check_output(['cat {}/{} | wc -l'.format(working_dir,metadata_md)],shell=True,text=True).strip())

    # initialise dictionary
    metadata_dict = {
        'level': [],
        'label': [],
        'text': []
    }

    # open the metadata file
    metadata_file = open(metadata_md, "r")

    # initialise variables
    title = ""
    description = ""
    
    # loop over metadata file to get information
    for i,line in enumerate(metadata_file):
        if line != "\n":
            if "#" == line[0]:
                title_parts = line.strip().split(' ')
                title = "".join(title_parts[1:]).upper()
                metadata_dict['level'].append(TITLE_LEVELS[title_parts[0]])
                metadata_dict['label'].append(title)
            else:
                if i == number_lines:
                    if description == '':
                        metadata_dict['text'].append(line.strip())
                    else:
                        description += line.strip()
                        metadata_dict['text'].append(' '.join(description))
                elif description != "":
                    description.append(line.strip())
                else:
                    description = [line.strip()]
        elif line == "\n" and title != "" and description != "":
            metadata_dict['text'].append(' '.join(description))
            title = ""
            description = ""
        elif line == "\n" and title != "":
            metadata_dict['text'].append('')
            title = ""
        else:
            pass

    # return all the metadata information as a pandas dataframe
    return pd.DataFrame(metadata_dict)