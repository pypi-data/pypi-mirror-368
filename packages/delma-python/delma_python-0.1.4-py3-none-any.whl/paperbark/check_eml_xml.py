import xmlschema

def check_eml_xml(eml_xml='eml.xml'):
    """
    Checks whether or not your eml xml file is formatted correctly for GBIF.

    Parameters
    ----------
        ``eml_xml``: ``str``
            Name of the eml xml file you want to validate.  Default value is ``'eml.xml'``.

    Returns
    -------
        Raises a ``ValueError`` if something is wrong, or returns True if it passes.
    """

    # first, check 
    if eml_xml is None:
        raise ValueError("Please provide an eml file / variable")

    try:
        check = xmlschema.validate("{}/{}".format(eml_xml), 'http://rs.gbif.org/schema/eml-gbif-profile/1.1/eml-gbif-profile.xsd')
        return check
    except xmlschema.validators.exceptions.XMLSchemaChildrenValidationError as e:
        print("children error")
        print("There is an error with your eml.xml file:\n")
        if "value doesn't match any pattern of" in e.reason:
            value = str(e.elem).split(" ")[1]
            print("Please provide a value to {}".format(value))
            print()
        else:
            print(e.reason)
        breakpoint
    except xmlschema.validators.exceptions.XMLSchemaValidationError as e:
        print("schema validation")
        print("There is an error with your eml.xml file:\n")
        if "value doesn't match any pattern of" in e.reason:
            value = str(e.elem).split(" ")[1]
            print("Please provide a value to {}".format(value))
            print()
        elif "character data between child elements not allowed" in e.reason:
            value = str(e.elem).split(" ")[1]
            print("Please remove the value you've provided for {}".format(value))
            print()
        else:
            print(str(e.elem).split(" ")[1])
            print(e.reason)
        breakpoint