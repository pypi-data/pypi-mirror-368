import subprocess
import datetime
import metapype
import metapype.eml.export
import metapype.eml.names as names
from metapype.model.node import Node
from .common_dictionaries import TITLE_LEVELS

def write_eml(metadata_md='metadata.md',
              working_dir='./',
              publishing_dir='./',
              eml_xml='eml.xml'):
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
            ``eml_xml``: ``str``
                Name of your eml xml file.  Default value is ``'eml.xml'``.
                    
        Returns
        -------
            ``None``
        """
        # initialise the eml.xml file
        metadata = Node(names.EML)
        metadata.add_attribute('packageId', 'edi.23.1') # doi:10.xxxx/eml.1.1
        metadata.add_attribute('system', 'https://doi.org')
        metadata.add_attribute('scope', 'system')

        # initialise elements
        elements = {}
        titles = {}
        level_dict = {0: metadata,
                      1 : None,
                      2 : None,
                      3 : None,
                      4 : None,
                      5 : None,
                      6 : None}

        # check for last line
        last_line = subprocess.check_output(['tail', '-1', '{}/{}'.format(working_dir,metadata_md)],text=True).strip()

        # open the metadata file
        metadata_file = open('{}/{}'.format(working_dir,metadata_md), "r")

        # initialise list so we have everything in order
        title_list = []

        # loop over things in metadata
        title = ""
        description = ""
        duplicate = 0
        comment=False
        for line in metadata_file:
            
            # first, check for comment
            if not comment:
                if line[0:4] == '<!--' and line.strip()[-3:] != '-->':
                    comment=True
            else:
                if line.strip()[-3:] == '-->':
                    comment=False

            # then, process information
            if not comment and line.strip()[-3:] != '-->':
                if line != "\n":
                    if "#" == line[0]:
                        title = ""
                        description = ""
                        title_parts = line.strip().split(' ')
                        title = "".join(title_parts[1:]).upper()
                        titles[title] = TITLE_LEVELS[title_parts[0]]
                        title_list.append(title)
                        if line.strip() == last_line:
                            elements[title] = ''
                    else:
                        if description != "":
                            description.append(line.strip())
                        else:
                            description = [line.strip()]
                        if line.strip() == last_line:
                            elements[title] = description
                elif line == "\n" and title != "" and description != "":

                    # try adding new lines
                    if type(description) is list:
                        description += ["\n"]
                    else:
                        description += "\n"

                    if title not in elements:
                        elements[title] = description
                    else:
                        # how to deal with duplicates and multiple lines?
                        elements["{}{}".format(title,duplicate)] = description
                        duplicate += 1
                    # temporarily removed this
                    # title = ""
                    # description = "" # try this
                elif line == "\n" and title != "":
                    if title not in elements:
                        if title == "PUBDATE":
                            elements[title] = datetime.datetime.today().strftime('%Y-%m-%d')
                        else:
                            elements[title] = ""
                    else:
                        elements["{}{}".format(title,duplicate)] = ""
                        duplicate += 1
                    title = ""
                else:
                    pass
               
        # close markdown file
        metadata_file.close()
        
        # loop over all levels
        for t in title_list:
            
            # check for duplicates
            if t[-1].isdigit():
                t = t[:-1]
            elif t[-2:].isdigit():
                t = t[:-2]
            elif t[0] == '@':
                t = t[1:]

            # get attribute
            if t in ['ULINK','CITETITLE','GBIF','DATESTAMP','HIERARCHYLEVEL','RIGHTS','DIRECTORY']:
                attr = t.lower()
            else:
                attr = getattr(names,t)

            # set nodes
            # if t != 'DIRECTORY':
            current_node = Node(attr,parent=level_dict[titles[t] - 1]) 

            # set node information 
            if t == 'USERID':   
                current_node.add_attribute('directory',"https://orcid.org")   
                if type(elements["DIRECTORY"]) in [str,list]:
                    current_node.content = strip_newline(elements["DIRECTORY"])
                else:
                    current_node.content = ""
            elif t == 'DIRECTORY':
                pass
            elif type(elements[t]) is list:
                if elements[t][-1] == "\n":
                    elements[t] = elements[t][:-1]
                    current_node.content = strip_newline(element=elements[t])
                else:
                    if "\n" in elements[t] and t in ["ABSTRACT","INTRODUCTION"]:
                        indices = [n for n,x in enumerate(elements[t]) if x == "\n"]
                        start = 0
                        for index in indices:
                            first_para = elements[t][start:index]
                            para_attr = getattr(names,"PARA")
                            para_node = Node(para_attr,parent=current_node)
                            para_node.content = strip_newline(element=first_para)
                            start = index + 1
                            current_node.add_child(para_node)
                    else:
                        current_node.content = strip_newline(element=elements[t])
            elif type(elements[t]) is str and t not in ["DATASET","CREATOR","INDIVIDUALNAME","ADDRESS","USERID","CONTACT","LICENSED","KEYWORDSET"]:
                current_node.content = strip_newline(element=elements[t])
            else:
                pass

            if t != 'DIRECTORY':
                level_dict[titles[t]] = current_node
                level_dict[titles[t] - 1].add_child(current_node)

        # write xml
        xml_str = metapype.eml.export.to_xml(metadata)
        with open("{}/{}".format(publishing_dir,eml_xml), 'w') as f:
            f.write(xml_str)

def strip_newline(element=None):

    if type(element) in [str,list]:
        if type(element) is str:
            if element[-2:] == "\n":
                return element[:-2]
            else:
                return element
        if element[-1] == "\n":
            element = element[:-1]
            return " ".join(element)
        else:
            return " ".join(element)