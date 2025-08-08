from .common_dictionaries import TITLE_LEVELS_NUM

# def traverse_dict(nested: Mapping, parent_key="", keys_to_not_traverse_further=tuple()) -> Iterator[Tuple[str, str]]:
#     """Each key is joined with it's parent using dot as a separator.

#     Once a `parent_key` matches `keys_to_not_traverse_further` 
#    it will no longer find its child dicts.
#    """
#     for key, value in nested.items():
#         if isinstance(value, abc.Mapping) and key not in keys_to_not_traverse_further:
#             print(traverse_dict(value, f"{parent_key}.{key}", keys_to_not_traverse_further))
#         else:
#             print(f"{parent_key}.{key}", value)

def check_dict(dict_to_check=None,
               metadata_dict=None,
               level=2):
    
    if type(dict_to_check) is list:
        if any(type(x) is dict for x in dict_to_check):
            metadata_dict['text'].append('')
            level +=1 
            for entry in dict_to_check:
                if type(entry) is dict:
                    # try this
                    metadata_dict=check_dict(dict_to_check=entry,metadata_dict=metadata_dict,level=level)
                else:
                    print("nope - here's the type")
                    print(type(entry))
                    print(entry)
                    print()
                    import sys
                    sys.exit()
            return metadata_dict
        else:
            metadata_dict['text'].append(get_description(desc_var=dict_to_check))
            return metadata_dict
        
    elif type(dict_to_check) is dict:
        level += 1
        for key in dict_to_check.keys():
            metadata_dict['level'].append(TITLE_LEVELS_NUM[level])
            metadata_dict['label'].append(key)
            if type(dict_to_check[key]) is dict or type(dict_to_check[key]) is list:
                # try this
                if type(dict_to_check[key]) is dict:
                    metadata_dict['text'].append('')
                metadata_dict=check_dict(dict_to_check=dict_to_check[key],metadata_dict=metadata_dict,level=level)
            else:
                if dict_to_check[key] is None:
                    metadata_dict['text'].append('')
                else:
                    if type(dict_to_check[key]) is not str:
                        print("nope")
                        import sys
                        sys.exit()
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