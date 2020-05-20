from general_invoice_reader import InvoiceReading
import re
import pandas as pd
from config_json import file_conf


class DirectUsage(InvoiceReading):

    def finding_gstin(self, filename):
        page_no = 1
        gstin = []
        while page_no < 100:    # I BELIEVE NO ANY SINGLE INVOICE CONTAIN MORE THAN 100 PAGES
            try:
                lines = self.preprocess_file(filename, page_no)
                pdf_string = self.complete_string(lines)
                gstin_found = re.findall(
                    '[0-3]{1}[0-9]{1}[a-zA-Z]{5}[0-9]{4}[a-zA-Z]{1}[1-9a-zA-Z]{1}[zZ]{1}[0-9a-zA-Z]{1}',
                    pdf_string
                )
                gstin = list(set(gstin + gstin_found))
                page_no += 1
                if len(gstin) >= 2:
                    break
            except Exception:
                break

        return gstin

    def numb(self, z):
        s = z.split(' ')
        result = 0
        fs = 0
        dict1 = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
                 'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
                 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
                 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
        dict2 = {'hundred': 100, 'thousand': 1000, 'lakh': 100000, 'lacs': 100000, 'crore': 10000000}
        for i in s:
            try:
                result += dict1[i]
            except Exception:
                result *= dict2[i]
                fs += result
                result = 0
        fs += result
        return fs

    def amount_calc(self, amt_string):
        b = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
             'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
             'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'forty', 'fifty',
             'sixty', 'seventy', 'eighty', 'ninety', 'hundred', 'thousand', 'lakh', 'lacs', 'crore')


        w = amt_string.split(' ')
        aw = ''
        for i in w:
            if i == 'and':
                break
            if i in b:
                aw = aw + i + ' '
        aw = aw[:-1]
        return self.numb(aw)


    def amount_by_words(self, pdf_string, word):
        # page_no = 1
        # pdf_string = ''
        # while page_no < 100:  # I BELIEVE NO ANY SINGLE INVOICE CONTAIN MORE THAN 100 PAGES
        #     try:
        #         lines = self.preprocess_file(filename, page_no)
        #         pdf_string += self.complete_string(lines) + '\n'
        #         page_no += 1
        #     except Exception:
        #         break
        pdf_string = pdf_string.lower()
        pdf_string = pdf_string.split('\n')
        for i in pdf_string:
            if word in i:
                return self.amount_calc(i)
        return None

    def detect_format(self, filename):
        page_no = 1
        pdf_string = ''
        while page_no < 100:  # I BELIEVE NO ANY SINGLE INVOICE CONTAIN MORE THAN 100 PAGES
            try:
                lines = self.preprocess_file(filename, page_no)
                pdf_string += self.complete_string(lines) + '\n'
                page_no += 1
            except Exception:
                break
        count = 0
        result_pan = None
        result_index = None
        for pan in file_conf:
            if pan in pdf_string:
                # print('yes')
                for conf_index in range(len(file_conf[pan])):
                    if self.count_invoices(filename, file_conf[pan][conf_index]):
                        result_pan = pan
                        result_index = conf_index
                        count += 1
        if count <= 1:
            return result_pan,result_index
        return None,None

    def count_invoices(self, filename, json_template):

        page_no = 1
        pdf_string = ''
        while page_no < 100:  # I BELIEVE NO ANY SINGLE INVOICE CONTAIN MORE THAN 100 PAGES
            try:
                lines = self.preprocess_file(filename, page_no)
                pdf_string += self.complete_string(lines) + '\n'
                page_no += 1
            except Exception:
                break
        pdf_string = pdf_string.lower()
        string = pdf_string
        # print(pdf_string)
        invoice_headers = json_template['invoice_headers']
        if invoice_headers is None:
            return True, string

        for header in invoice_headers:
            # print(header)
            try:
                k = pdf_string.index(header)
            except Exception:
                k = (-1)
            if k == (-1):
                return False,string
            else:
                pdf_string = pdf_string[k + len(header):]

        for header in invoice_headers:
            try:
                k = pdf_string.index(header)
            except Exception:
                k = (-1)
            if k == (-1):
                return True, string
            else:
                pdf_string = pdf_string[k + len(header):]

        return False,string

    def date_manipulation(self, s):
        import re
        d = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
             'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}
        s = str(s)
        s = s.lower()
        s += ' '
        s.replace('  ', ' ')

        a = re.findall(r'\d{1,2}[-,/]\d{1,2}[-,/]\d{4}', s)
        if len(a) > 0:
            a = a[0]
            for i in [' ', '-', '/']:
                b = a.split(i)
                if len(b) > 1:
                    break
            day = b[0]
            if len(day) == 1:
                day = '0' + day
            m = b[1]
            if len(m) == 1:
                m = '0' + m
            y = b[2]
            return pd.to_datetime(y + m + day, format='%Y%m%d', errors='ignore')

        a = re.findall(r'\d{4}[-,/]\d{2}[-,/]\d{2}', s)
        if len(a) > 0:
            a = a[0]
            for i in [' ', '-', '/']:
                b = a.split(i)
                if len(b) > 1:
                    break
            day = b[2]
            if len(day) == 1:
                day = '0' + day
            m = b[1]
            if len(m) == 1:
                m = '0' + m
            y = b[0]
            return pd.to_datetime(y + m + day, format='%Y%m%d', errors='ignore')

        a = (re.findall(r'\d{2}-\d{2}-\d{2}', s))
        if len(a) > 0:
            a = a[0]
            b = a.split('-')
            day = b[0]
            m = b[1]
            y = b[2]
            return pd.to_datetime('20' + y + m + day, format='%Y%m%d', errors='ignore')

        da = re.findall(r'\d{2}[-,/]', s)
        if len(da) == 3:
            day = da[0][:-1]
            m = da[1][:-1]
            y = da[2][:-1]
            return pd.to_datetime('20' + y + m + day, format='%Y%m%d', errors='ignore')

        l = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        match = []
        for i in l:
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{4}", s)
            match += re.findall(r"\d{1,2} " + str(i) + " \d{4}", s)
            match += re.findall(r"\d{1,2}/" + str(i) + "/\d{4}", s)
            if len(match) > 0:
                for i in [' ', '-', '/']:
                    a = match[0].split(i)
                    if len(a) > 1:
                        break
                day = a[0]
                m = d[a[1]]
                y = a[2]
                return pd.to_datetime(y + m + day, format='%Y%m%d', errors='ignore')

        for i in l:
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{2}", s)
            match += re.findall(r"\d{1,2} " + str(i) + " \d{2}", s)
            match += re.findall(r"\d{1,2}/" + str(i) + "/\d{2}", s)
            if len(match) > 0:
                for i in [' ', '-', '/']:
                    a = match[0].split(i)
                    if len(a) > 1:
                        break
                day = a[0]
                m = d[a[1]]
                y = a[2]
                return pd.to_datetime('20'+y + m + day, format='%Y%m%d', errors='ignore')

        for j in d:
            if j in s:
                m = d[j]
                m = m.strip()
                if len(m) == 1:
                    m = '0' + m
                da = re.findall(r'\d{1,2}[-,/," "]', s)[0][:-1]
                if len(da) == 0:
                    da = re.findall(r'[" ",,]\d{2}', s)
                    da = da[0][1:]
                da = da.strip()
                if len(da) == 1:
                    da = '0' + da
                return pd.to_datetime(m + da, format='%m%d', errors='ignore')

        match = []
        l = ['january', 'febuary', 'march', 'april', 'may', 'june', 'july', 'august',
             'september', 'october', 'november', 'december']
        for i in l:
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{4}", s)
            match += re.findall(r"\d{1,2} " + str(i) + " \d{4}", s)
            match += re.findall(r"\d{1,2}/" + str(i) + "/\d{4}", s)
            if len(match) > 0:
                for i in [' ', '-', '/']:
                    a = match[0].split(i)
                    if len(a) > 1:
                        break
                day = a[0]
                m = d[a[1]]
                y = a[2]
                return pd.to_datetime(y + m + day, format='%Y%m%d', errors='ignore')

        for i in l:
            match += re.findall(r"\d{1,2}-" + str(i) + "-\d{2}", s)
            match += re.findall(r"\d{1,2} " + str(i) + " \d{2}", s)
            match += re.findall(r"\d{1,2}/" + str(i) + "/\d{2}", s)
            if len(match) > 0:
                for i in [' ', '-', '/']:
                    a = match[0].split(i)
                    if len(a) > 1:
                        break
                day = a[0]
                m = d[a[1]]
                y = a[2]
                return pd.to_datetime('20' + y + m + day, format='%Y%m%d', errors='ignore')

        for j in d:
            if j in s:
                m = d[j]
                m = m.strip()
                if len(m) == 1:
                    m = '0' + m
                da = re.findall(r'\d{1,2}[-,/," "]', s)[0][:-1]
                if len(da) == 0:
                    da = re.findall(r'[" ",,]\d{2}', s)
                    da = da[0][1:]
                da = da.strip()
                if len(da) == 1:
                    da = '0' + da
                return pd.to_datetime(m + da, format='%m%d', errors='ignore')
