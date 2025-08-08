import subprocess
import metapype
import metapype.eml.export
import metapype.eml.names as names
from metapype.model.node import Node
from .common_dictionaries import TITLE_LEVELS

def use_eml_xml(metadata_md='metadata.md',
                working_dir='./',
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
        metadata.add_attribute('system', 'ALA-registry')

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
        last_line = subprocess.check_output(['tail', '-1', metadata_md],text=True).strip()

        # open the metadata file
        metadata_file = open(metadata_md, "r")

        # initialise list so we have everything in order
        title_list = []

        # loop over things in metadata
        title = ""
        description = ""
        duplicate = 0
        for line in metadata_file:
            if line != "\n":
                if "#" == line[0]:
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
                if title not in elements:
                    elements[title] = description
                else:
                    elements["{}{}".format(title,duplicate)] = description
                    duplicate += 1
                title = ""
                description = ""
            elif line == "\n" and title != "":
                if title not in elements:
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

            # get attribute and set nodes
            attr = getattr(names,t)
            current_node = Node(attr,parent=level_dict[titles[t] - 1])
            if type(elements[t]) is list:
                current_node.content = "".join(elements[t])
            level_dict[titles[t]] = current_node
            level_dict[titles[t] - 1].add_child(current_node)
            
        # write xml
        xml_str = metapype.eml.export.to_xml(metadata)
        with open("{}/{}".format(working_dir,eml_xml), 'w') as f:
            f.write(xml_str)