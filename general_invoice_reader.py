from collections import namedtuple
import os
import xml.etree.ElementTree as ET
import pandas as pd

Text = namedtuple('Pdf_text', ['text', 'x1', 'y1', 'x2', 'y2'])


class FileProcessing(object):

    def reading_xml(self, pdf_file_path):
        root = None
        try:
            if ('.pdf' in pdf_file_path.lower()) and '.xml' not in pdf_file_path:
                tree = ET.parse(f'{pdf_file_path}.xml')
                root = tree.getroot()
        except:
            st = f"pdf2txt.py -t xml '{pdf_file_path}' > '{pdf_file_path + '.xml'}'"
            os.system(st)
            tree = ET.parse(f'{pdf_file_path}.xml')
            root = tree.getroot()
        return root

    def reading_data(self, root, page_no):
        l = []
        items = []
        for k in root[page_no - 1]:
            for j in k:
                if j.tag == 'textline':

                    try:
                        coor = j.attrib['bbox']
                        coor = coor.split(',')
                        coor = [float(io) for io in coor]
                        for i in j:

                            try:
                                if i.text == ' ':

                                    try:
                                        sa1 = float(i.attrib['bbox'].split(',')[2])
                                        sa2 = float(i.attrib['bbox'].split(',')[3])
                                        if ''.join(l) != '':

                                            items.append(Text(''.join(l), coor[0], coor[1], ca1, ca2))
                                            l = []
                                            coor[0] = sa1
                                        else:
                                            l = []
                                    except:
                                        if ''.join(l) != '':

                                            items.append(Text(''.join(l), coor[0], coor[1], ca1, ca2))
                                            l = []
                                            coor[0] = ca1
                                        else:
                                            l = []
                                        continue
                                l.append(i.text)
                                ca1 = float(i.attrib['bbox'].split(',')[2])
                                ca2 = float(i.attrib['bbox'].split(',')[3])
                            except:
                                continue
                        if ''.join(l) != '':

                            items.append(Text(''.join(l), coor[0], coor[1], coor[2], coor[3]))
                            l = []
                        else:
                            l = []
                    except:
                        continue
        return items

    def text_cleaning(self, items):
        for i in range(len(items)):
            items[i] = items[i]._replace(text=items[i].text.replace('\n', '').strip())

        d = [items[i].text == '' for i in range(len(items))]
        indexes = []
        for i in range(len(d)):
            if d[i] == True:
                indexes.append(i)

        for index in sorted(indexes, reverse=True):
            del items[index]

        return items

    def sorting_with_x(self, items):
        items = sorted(items, key=lambda x: x.x1)
        return items

    def row_identifiers(self, items):
        row_fig = []
        for i in range(len(items)):
            if (items[i].y1 + items[i].y2) / 2 not in row_fig:
                row_fig.append((items[i].y1 + items[i].y2) / 2)
        row_fig.sort()

        unique_fig = len(row_fig)
        row_gaps = [row_fig[i] - row_fig[i - 1] for i in range(1, len(row_fig))]
        word_size = min([abs(items[i].y2 - items[i].y1) for i in range(len(items))])
        word_size /= 4
        for i in row_gaps:
            if i < word_size:
                unique_fig -= 1
        new_figs = []
        k = []
        for i in range(len(row_fig) - 1):
            k.append(row_fig[i])
            if row_gaps[i] < word_size:
                continue
            else:
                new_figs.append(k)
                k = []
        if row_gaps[-1] < word_size:
            new_figs[-1].append(row_fig[-1])
        else:
            new_figs.append([row_fig[-1]])

        new_figs = [sum(i) / len(i) for i in new_figs]
        new_figs.sort(reverse=True)
        return (new_figs)

    def preprocess_file(self, file, key):  # MASTER FUNCTION
        root = self.reading_xml(file)
        items = self.reading_data(root, key)
        #         for lkj in range(1,len(root)):
        #             items+=self.reading_data(root,lkj+1)
        items = self.text_cleaning(items)
        items = self.sorting_with_x(items)
        lines = self.line_theory(items)
        lines = self.line_cleaning(lines)
        return lines

    def line_cleaning(self, lines):
        for line in range(len(lines)):
            delete_indexes = []
            for word in range(len(lines[line])):
                s = lines[line][word].text
                flag = 0
                for char in s:
                    if (char >= 'A' and char <= 'Z') or (char >= 'a' and char <= 'z'):
                        flag = 1
                        break
                    elif char >= '0' and char <= '9':
                        flag = 1
                        break
                    else:
                        continue
                if flag == 0:
                    delete_indexes.append(word)
            for index in delete_indexes[::-1]:
                lines[line].pop(index)
        return lines

    def line_theory(self, items):
        lines = []
        while items != []:
            t = items.pop(0)
            k = [t]
            y1, y2 = min(t.y1, t.y2), max(t.y1, t.y2)
            l = []
            for i in range(len(items)):
                y_mid = (items[i].y1 + items[i].y2) / 2
                if y_mid > y1 and y_mid < y2:
                    l.append(i)
            for i in reversed(l):
                k.append(items.pop(i))
            lines.append(k)
        lines = sorted(lines, key=lambda x: x[0].y1, reverse=True)
        for i in range(len(lines)):
            lines[i] = sorted(lines[i], key=lambda x: x.x1)
        return lines


class LiftingLineTheory(object):

    def get_obj_by_element(self, element, lines, position_conf=None):
        element_objects = []
        for lno in range(len(lines)):
            for ele in range(len(lines[lno]) - len(element) + 1):
                temp_buffer = [k.text.lower() for k in lines[lno][ele:ele + len(element)]]
                if all([m in n for m, n in zip(element, temp_buffer)]):
                    for k in range(ele, ele + len(element)):
                        element_objects.append(lines[lno][ele])
        return element_objects

    def vertical_objects_by_element(self, element, lines):
        element_obj = self.get_obj_by_element(element, lines)
        vertical_objects_list = {'above': [], 'below': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            x = (x1 + x2) / 2
            for i in lines:
                for j in i:
                    if (j.x1 <= x1 and j.x2 >= x1) or (j.x1 <= x2 and j.x2 >= x2) or (j.x1 <= x and j.x2 >= x):
                        if j.y2 > y2:
                            vertical_objects_list['above'].append(j)
                        elif j.y1 < y1:
                            vertical_objects_list['below'].append(j)
        fs = [i.text for i in vertical_objects_list['above']] + [i.text for i in vertical_objects_list['below']]
        return fs

    def vertical_above_objects_by_element(self, element, lines):
        element_obj = self.get_obj_by_element(element, lines)
        vertical_objects_list = {'above': [], 'below': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            x = (x1 + x2) / 2
            for i in lines:
                for j in i:
                    if (j.x1 <= x1 and j.x2 >= x1) or (j.x1 <= x2 and j.x2 >= x2) or (j.x1 <= x and j.x2 >= x):
                        if j.y2 > y2:
                            vertical_objects_list['above'].append(j)
        fs = [i.text for i in vertical_objects_list['above']]
        return fs

    def vertical_below_objects_by_element(self, element, lines):
        element_obj = self.get_obj_by_element(element, lines)
        vertical_objects_list = {'above': [], 'below': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            x = (x1 + x2) / 2
            for i in lines:
                for j in i:
                    if (j.x1 <= x1 and j.x2 >= x1) or (j.x1 <= x2 and j.x2 >= x2) or (j.x1 <= x and j.x2 >= x):
                        if j.y1 < y1:
                            vertical_objects_list['below'].append(j)
        fs = [i.text for i in vertical_objects_list['below']]
        return fs

    def vertical_objects_by_objects(self, element_obj, lines):

        vertical_objects_list = {'above': [], 'below': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            x = (x1 + x2) / 2
            for i in lines:
                for j in i:
                    if (j.x1 <= x1 and j.x2 >= x1) or (j.x1 <= x2 and j.x2 >= x2) or (j.x1 <= x and j.x2 >= x):
                        if j.y2 > y2:
                            vertical_objects_list['above'].append(j)
                        elif j.y1 < y1:
                            vertical_objects_list['below'].append(j)
        fs = [i for i in vertical_objects_list['above']] + [i for i in vertical_objects_list['below']]
        return fs

    def horizontal_objects_by_element(self, element, lines):
        element_obj = self.get_obj_by_element(element, lines)
        vertical_objects_list = {'left': [], 'right': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            y = (y1 + y2) / 2
            for i in lines:
                for j in i:
                    if (j.y1 <= y1 and j.y2 >= y1) or (j.y1 <= y2 and j.y2 >= y2) or (j.y1 <= y and j.y2 >= y):
                        if j.x2 > x2:
                            vertical_objects_list['right'].append(j)
                        elif j.x1 < x1:
                            vertical_objects_list['left'].append(j)
        fs = [i.text for i in vertical_objects_list['left']] + [i.text for i in vertical_objects_list['right']]
        return fs

    def horizontal_right_objects_by_element(self, element, lines):
        element_obj = self.get_obj_by_element(element, lines)
        vertical_objects_list = {'left': [], 'right': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            y = (y1 + y2) / 2
            for i in lines:
                for j in i:
                    if (j.y1 <= y1 and j.y2 >= y1) or (j.y1 <= y2 and j.y2 >= y2) or (j.y1 <= y and j.y2 >= y):
                        if j.x2 > x2:
                            vertical_objects_list['right'].append(j)
        fs = [i.text for i in vertical_objects_list['right']]
        return fs

    def horizontal_left_objects_by_element(self, element, lines):
        element_obj = self.get_obj_by_element(element, lines)
        vertical_objects_list = {'left': [], 'right': []}
        if element_obj is not None:
            x1 = element_obj[0].x1
            x2 = element_obj[-1].x2
            y1 = element_obj[0].y1
            y2 = element_obj[-1].y2
            y = (y1 + y2) / 2
            for i in lines:
                for j in i:
                    if (j.y1 <= y1 and j.y2 >= y1) or (j.y1 <= y2 and j.y2 >= y2) or (j.y1 <= y and j.y2 >= y):
                        if j.x1 < x1:
                            vertical_objects_list['left'].append(j)

        fs = [i.text for i in vertical_objects_list['left']]
        return fs


class InvoiceReading(FileProcessing, LiftingLineTheory):

    def complete_string(self, lines):
        lines_list = self.list_of_lines(lines)
        return '\n'.join(lines_list)

    def list_of_lines(self, lines):
        lines_list = []
        for i in lines:
            s = ''
            for j in i:
                s += j.text + ' '
            lines_list.append(s)
        return lines_list

    def exact_left_without_noise(self, key, ls, lines, validation_code='validation[0]=True'):
        x_min, x_max = ls[0].x1, ls[-1].x2
        y_min, y_max = ls[0].y1, ls[-1].y2

        x = (x_min + x_max) / 2

        abs_distances = [abs(x - (i.x1 + i.x2) / 2) if i.x2 < x_max else 10 ** 9 for i in
             lines[key]]  # logic for creating priority order
        abs_distances = [(i, abs_distances[i]) for i in range(len(abs_distances))]

        abs_distances = sorted(abs_distances, key=lambda x: x[1])

        for distance in abs_distances:
            string = lines[key][distance[0]].text
            validation = [[False, '']]
            exec(validation_code)
            try:
                if True in validation[0]:
                    return string if validation[0][1] == '' else validation[0][1]
            except:
                if validation[0]:
                    return string
        return None

    def exact_bottom_without_noise(self, key, ls, lines, validation_code='validation[0]=True'):
        x_min, x_max = ls[0].x1, ls[-1].x2
        y_min, y_max = ls[0].y1, ls[-1].y2

        y = (y_min + y_max) / 2

        vertical_list = self.vertical_objects_by_objects(ls, lines)

        abs_distances = [abs(y - (i.y1 + i.y2) / 2) if y_min > i.y1 else 10 ** 9 for i in
             vertical_list]  # logic for creating priority order
        abs_distances = [(i, abs_distances[i]) for i in range(len(abs_distances))]
        abs_distances = sorted(abs_distances, key=lambda x: x[1])

        for i in abs_distances:
            string = vertical_list[i[0]].text
            validation = [[False, '']]
            exec(validation_code)
            try:
                if True in validation[0]:
                    return string if validation[0][1] == '' else validation[0][1]
            except:
                if validation[0]:
                    return string
        return None

    def exact_right_without_noise(self, key, ls, lines, validation_code='validation[0]=True'):
        x_min, x_max = ls[0].x1, ls[-1].x2
        y_min, y_max = ls[0].y1, ls[-1].y2

        x = (x_min + x_max) / 2

        abs_distances = [abs(x - (i.x1 + i.x2) / 2) if i.x2 > x_max else 10 ** 9 for i in
             lines[key]]  # logic for creating priority order
        abs_distances = [(i, abs_distances[i]) for i in range(len(abs_distances))]

        abs_distances = sorted(abs_distances, key=lambda x: x[1])

        for distance in abs_distances:
            string = lines[key][distance[0]].text
            validation = [[False, '']]
            exec(validation_code)
            try:
                if True in validation[0]:
                    return string if validation[0][1] == '' else validation[0][1]
            except:
                if validation[0]:
                    return string
        string = ' '.join([i.text for i in lines[key]])
        validation = [[False, '']]
        exec(validation_code)
        try:
            if True in validation[0]:
                return string if validation[0][1] == '' else validation[0][1]
        except:
            if validation[0]:
                return string
        return None

    def key_finder(self, lines, key_conf, regex_code='validation[0]=True'):
        exact_bottom_list = []
        vertical_objects_list = []
        horizontal_objects_list = []
        exact_right_list = []
        for conf in key_conf:

            indexers = key_conf[conf]
            ls = {}
            keys = []
            for line in range(len(lines)):
                for word in range(len(lines[line]) - len(indexers) + 1):
                    temp_buffer = [k.text.lower() for k in lines[line][word:word + len(indexers)]]

                    if all([m in n for m, n in zip(indexers, temp_buffer)]):
                        keys.append(line)
                        ls[line] = []
                        for k in range(word, word + len(indexers)):
                            ls[line].append(lines[line][k])
                        break

            if keys is not None:
                for key in keys:
                    if conf == 'exact_bottom':
                        temp = self.exact_bottom_without_noise(key, ls[key], lines, regex_code)
                        exact_bottom_list.append(temp)
                    if conf == 'exact_right':
                        temp = self.exact_right_without_noise(key, ls[key], lines, regex_code)
                        exact_right_list.append(temp)
                    if conf == 'horizontal_objects_list':
                        horizontal_objects_list = self.horizontal_objects_by_element(key_conf[conf], lines)
                    if conf == 'vertical_objects_list':
                        vertical_objects_list = self.vertical_objects_by_element(key_conf[conf], lines)
        final_list = []
        for i in [exact_bottom_list, vertical_objects_list, exact_right_list, horizontal_objects_list]:
            if i != []:
                final_list.append(i)
        try:
            fl_intersection = final_list[0]
        except:
            return []
        for i in final_list[1:]:
            fl_intersection = list(set(fl_intersection).intersection(i))
        return fl_intersection

    def get_no_of_pages_in_pdf(self, filename):
        root = self.reading_xml(filename)
        return len(root)

    def final_running(self, file, file_conf, regex_code='validation[0]=True'):  # MASTER FUNCTION
        num_pages = self.get_no_of_pages_in_pdf(filename=file)
        result_data = {}
        for key in file_conf:
            if type(file_conf[key])==dict:
                regex_code = file_conf[key]['regex_code']
                if regex_code is None:
                    for page_no in range(1,num_pages+1):
                        lines = self.preprocess_file(file,page_no)
                        result_data[key] = self.key_finder(lines, file_conf[key]['location_conf'],
                                                           regex_code='validation[0]=True')
                        if result_data[key] is not None:
                            break
                else:
                    for page_no in range(1,num_pages+1):
                        lines = self.preprocess_file(file,page_no)
                        result_data[key] = self.key_finder(lines, file_conf[key]['location_conf'],regex_code)
                        if result_data[key] is not None:
                            break
        return result_data


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
        match += re.findall(r"\d{1,2}[/,-,.]\d{1,2}[/,-,.]\d{4}", s)
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
    'file_identifiers': ['tax', 'invoice', 'no', 'dated'],

    'amount': {
        'location_conf': {
            'exact_right': ['total', 'invoice', 'value']
        },
        'regex_code': None
    },
    'invoice': {
        'location_conf': {
            'exact_right': ['invoice', 'no']
        },
        'regex_code': None
    },
    'date': {
        'location_conf': {
            'exact_right': ['date'],
            'horizontal_objects_list': ['invoice', 'no']
        },
        'regex_code': date_regex
    },
    'dealer_gst': {
        'location_conf': {
            'exact_right': ['gst', 'no'],
            'horizontal_objects_list': ['transporter', 'name']
        },
        'regex_code': gstin_code
    },
    'seller_gst': {
        'location_conf': {
            'exact_right': ['gst', 'no'],
            'horizontal_objects_list': ['received', 'the', 'goods']
        },
        'regex_code': gstin_code
    }
}
