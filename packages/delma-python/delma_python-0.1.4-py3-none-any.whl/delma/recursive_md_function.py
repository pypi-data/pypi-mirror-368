from .common_dictionaries import TITLE_LEVELS_NUM

def check_dict(dict_to_check=None,
               metadata_dict=None,
               level=2):

    if type(dict_to_check) is list:
        if any(type(x) is dict for x in dict_to_check):
            metadata_dict['text'].append('')
            # level +=1 # try this
            for entry in dict_to_check:
                if type(entry) is dict:
                    # try this
                    metadata_dict=check_dict(dict_to_check=entry,metadata_dict=metadata_dict,level=level)
            return metadata_dict
        else:
            metadata_dict['text'].append(get_description(desc_var=dict_to_check))
            return metadata_dict
        
    elif type(dict_to_check) is dict:
        level += 1
        for key in dict_to_check.keys():
            if key in ['#text','@xmlns:lang'] and type(dict_to_check[key]) is dict:
                pass
            else:
                if key[0] in ['@','#']:
                    pass
                else:
                    metadata_dict['level'].append(TITLE_LEVELS_NUM[level])
                    metadata_dict['label'].append(key)
                    if type(dict_to_check[key]) is dict or type(dict_to_check[key]) is list:
                        if type(dict_to_check[key]) is dict:
                            metadata_dict['text'].append('')
                        metadata_dict=check_dict(dict_to_check=dict_to_check[key],metadata_dict=metadata_dict,level=level)
                    else:
                        if dict_to_check[key] is None:
                            metadata_dict['text'].append('')
                        else:
                            metadata_dict['text'].append(get_description(desc_var=dict_to_check[key]))
        return metadata_dict
            
    elif type(dict_to_check) is str:
        metadata_dict['text'].append(get_description(desc_var=dict_to_check))
        return metadata_dict
    
    elif dict_to_check is None:
        metadata_dict['text'].append('')
        return metadata_dict
    
    else:
        raise ValueError("nope: {}".format(type(dict_to_check)))
        
def get_description(desc_var=None):

    # first, check if it is string
    if type(desc_var) is str:
        return '{}\n'.format(desc_var)
    
    # then, check if it is None
    elif desc_var is None:
        return '\n'
    
    elif type(desc_var) is list:
        return '{}\n'.format('\n'.join(desc_var))
    
    else:
        raise ValueError("type not taken into account in get_description: {}".format(type(desc_var)))
    
def add_entry(metadata_dict,
              level=None,
              label=None,
              text=None):
    
    metadata_dict['level'].append(level)
    metadata_dict['label'].append(label)
    metadata_dict['text'].append(text)
    return metadata_dict