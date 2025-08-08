import os
import io
import requests
import xmltodict
from .common_dictionaries import TITLE_LEVELS_NUM
from .recursive_md_function import check_dict,add_entry

def create_md(metadata_md='metadata.md',
              working_dir='./',
              xml_url=None):
        """
        Creates a markdown file containing the metadata information needed for the DwCA.  The user can edit this 
        markdown, and use it to generate the metadata files.

        Parameters
        ----------
            ``metadata_md`` : ``str``
                Name of the metadata file you will edit.  Default is ``'metadata.md'``.
            ``working_dir``: ``str``
                Name of your working directory.  Default value is ``'./'``.
            ``xml_url`` : ``str``
                URL of the eml xml file you want to emulate.  Default is ``None``.

        Returns
        -------
            ``None``
        """
        
        if not os.path.exists(metadata_md) and xml_url is None:
            os.system("cp {} {}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metadata_template.md'),os.path.join(working_dir,metadata_md)))
        elif xml_url is not None:
            #  testing here
            #  https://collections.ala.org.au/ws/eml/dr368
                # initialise dictionary
            metadata_dict = {
                'level': [],
                'label': [],
                'text': []
            }
            
            xml_dict = xmltodict.parse(io.BytesIO(requests.get(xml_url).content))['eml:eml']
            for header in ['dataset','additionalMetadata']:
                metadata_dict = add_entry(metadata_dict=metadata_dict,level=TITLE_LEVELS_NUM[1],label=header,text='')
                for key in xml_dict[header].keys():
                    if type(xml_dict[header][key]) is dict:
                        metadata_dict=add_entry(metadata_dict=metadata_dict,level=TITLE_LEVELS_NUM[2],label=key,text='')
                        metadata_dict=check_dict(xml_dict[header][key],metadata_dict=metadata_dict,level=2)
                    elif type(xml_dict[header][key]) is list:
                        if any(type(x) is dict for x in xml_dict[header][key]):
                            for entry in xml_dict[header][key]:
                                metadata_dict['level'].append(TITLE_LEVELS_NUM[2])
                                metadata_dict['label'].append(key)
                                metadata_dict=check_dict(xml_dict[header][key],metadata_dict=metadata_dict,level=2)
                        else:
                            metadata_dict['level'].append(TITLE_LEVELS_NUM[2])
                            metadata_dict['label'].append(key)
                            metadata_dict=check_dict(xml_dict[header][key],metadata_dict=metadata_dict,level=2)
                    elif type(xml_dict[header][key]) is str:
                        metadata_dict['level'].append(TITLE_LEVELS_NUM[2])
                        metadata_dict['label'].append(key)
                        metadata_dict=check_dict(xml_dict[header][key],metadata_dict=metadata_dict,level=2)
                    elif xml_dict[header][key] is None:
                        metadata_dict=add_entry(metadata_dict=metadata_dict,level=TITLE_LEVELS_NUM[2],label=key,text='')
                    else:
                         raise ValueError("other type: {}".format(type(xml_dict[header][key])))
            # print(metadata_dict)
            max_num = 0
            for entry in metadata_dict:
                 if len(metadata_dict[entry]) > max_num:
                      max_num = len(metadata_dict[entry])

            for entry in metadata_dict:
                 if len(metadata_dict[entry]) < max_num:
                      difference = max_num - len(metadata_dict[entry])
                      metadata_dict[entry] = metadata_dict[entry] + ['' for x in range(difference)]
            
            import pandas as pd
            # print(pd.DataFrame(metadata_dict))
            # return pd.DataFrame(metadata_dict)
            metadata_file = open('{}/{}'.format(working_dir,metadata_md),"w")
            for i,row in pd.DataFrame(metadata_dict).iterrows():
                 metadata_file.write('{} {}\n{}\n'.format(row['level'],row['label'],row['text']))
            # metadata_file.write('{} {}\n\n'.format(TITLE_LEVELS_NUM[1],header))
            # metadata_file.write('{} {}\n{}\n'.format(TITLE_LEVELS_NUM[level],key,description))
            metadata_file.close()
        else:
            pass