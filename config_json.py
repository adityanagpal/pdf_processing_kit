gstin_code = '''
def regex(string):
    import re
    k=re.findall('[0-3]{1}[0-9]{1}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9a-zA-Z]{1}[zZ]{1}[0-9a-zA-Z]{1}',string)
    if k!=[]:
        return [True,k[0]]

    if len(string)!=15:
        return [False,'']

    if not string.isalnum():
        return [False,'']
    return [True,'']

validation[0]=regex(string)

'''

amount_regex = '''
try:
    float(string.replace(',',''))
    validation[0]=[True,string]
except:
    validation[0]=[False,string]
'''

date_regex = '''
def regex(string):
    import re
    def dates_found(s):
        import re
        s = s.lower()+' '
        match = []
        l = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        l1 = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
              'october', 'november', 'december']
        for i in l:
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{4}", s)
            match += re.findall(r"\d{1,2} " + str(i) + " \d{4}", s)
            match += re.findall(r"\d{1,2}/" + str(i) + "/\d{4}", s)
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{2}", s)
        for i in l1:
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{4}", s)
            match += re.findall(r"\d{1,2}' '" + str(i) + "' '\d{4}", s)
            match += re.findall(r"\d{1,2}/" + str(i) + "/\d{4}", s)
        match += re.findall(r"\d{1,2}[-,/,.]\d{1,2}[-,/,.]\d{4}", s)
        match += re.findall(r"\d{4}[/,-]\d{1,2}[/,-]\d{1,2}", s)
        match += re.findall(r"\d{1,2}[/,-]\d{1,2}[/,-]\d{2} ", s)
        try:
            return match[0]
        except:
            return []
    k = dates_found(string)
    if k!=[]:
        return [True,k]

    return [False,'']

validation[0]=regex(string)

'''
file_conf = {
    'AADCS9958B':    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++STOVEKRAFT
    [
        {
        'invoice_headers':['invoice number','invoice date','billing address','delivery address',
                           'total amount [inr]'],
        'amount': {
            'location_conf': {
                'exact_right': ['invoice','total','[inr]']
            },
            'regex_code': amount_regex
        },
        'invoice': {
            'location_conf': {
                'exact_bottom': ['invoice', 'number']
            },
            'regex_code': None
        },
        'date': {
            'location_conf': {
                'exact_bottom': ['invoice','date'],
                # 'horizontal_objects_list': ['invoice', 'no']
            },
            'regex_code': date_regex
        },
    },],
    'AADCK0743L': #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++KENT
        [
        {

            'invoice_headers':['sales indent','indent no','indent booking date','customer order no',
                           'grand total'],
            'invoice': {
                'location_conf': {
                                'exact_right': ['indent', 'no']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['grand','total'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': None
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['indent','booking','date'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
        ],
        'AABCG9798D': #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++GANESHAM
        [
        {
            'invoice_headers':['invoice no','dated','place of supply','transport','grand total'],
            'invoice': {
                'location_conf': {
                                'exact_right': ['invoice', 'no']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['grand','total'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': None
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['dated'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
            ],
        'AAACC9574E': #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++CHANDRA
        [
        {
            'invoice_headers':['invoice no','date of invoice','place of supply','transport',
                           'grand total'],
            'invoice': {
                'location_conf': {
                                'exact_right': ['invoice', 'no']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['grand','total'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': None
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['date'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
            ],
        'AADCS1967Q': #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++SM Appliances
        [
        {
            'invoice_headers':['tax invoice','invoice no','dated','supplier’s ref',
                           'buyer','amount chargeable'],
            'invoice': {
                'location_conf': {
                                'exact_bottom': ['invoice', 'no']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['rs'],
                            'horizontal_objects_list' : ['total']
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': None
                    },
            'date': {
                        'location_conf': {
                            'exact_bottom': ['dated'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
            ],
        'AAECK1982G': #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++KCM
        [
        {
            'invoice_headers':['invoice no','invoice date','place of supply','date of supply',
                           'total invoice','grand total'],
            'invoice': {
                'location_conf': {
                                'exact_right': ['invoice', 'no']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['grand','total'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': None
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['invoice','date'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
            ],
        'AAACS8418H': #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Singer
        [
        {
            'invoice_headers': None,
            'invoice': {
                'location_conf': {
                                'exact_right': ['invoice', 'no']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['total','invoice','value'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': amount_regex
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['invoice','date'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
            ],
    'AFBPJ3030K':#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++BJL
    [
        {
            'invoice_headers': ['inv.no','date','vehicle no','sub total','net amount','grand total'],
            'invoice': {
                'location_conf': {
                                'exact_right': ['inv.no.:']
                            },
                            'regex_code': None
            },
            'amount': {
                        'location_conf': {
                            'exact_right': ['grand','total'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': amount_regex
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['date'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
    ],
    'AAMFD4475A':#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Dealer Digital Shoppe
    [
        {
            'invoice_headers': ['original for recipient','gstin','tax invoice','amount chargeable'],
            'invoice': {
                'location_conf': {
                                'exact_right': ['invoice','no']
                            },
                            'regex_code': None
            },
            'amount': {
                    'direct_conf': 'amount chargeable',
                        'location_conf': {
                            'exact_right': ['total'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': amount_regex
                    },
            'date': {
                        'location_conf': {
                            'exact_right': ['dated'],
                            # 'vertical_objects_list' : ['amount']
                        },
                        'regex_code': date_regex
                    },
        },
    ],
}
