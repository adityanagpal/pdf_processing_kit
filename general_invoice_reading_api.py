import requests
from urllib.request import urlopen
import uuid
import json
from environs import Env
from aws_upload import *


from general_invoice_reader import InvoiceReading
from config_json import file_conf
from direct_usage_methods import DirectUsage
env = Env()
env.read_env()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "./")


class InvoiceParserV2:

    def on_post_upload(self, req, resp):
        file_obj = urlopen(json.loads(req.stream.read()).get("url")).read()
        uid = str(uuid.uuid4())
        file_name = "{}{}".format(uid, ".pdf")
        file_paths = os.path.join(file_path, "{}".format(file_name))
        with open(file_paths, "w+b") as writer:
            writer.write(file_obj)
            writer.close()



        aws_url = aws_upload_data_get_urls(input_file=file_paths)
        str_obj = DirectUsage()
        gstin = str_obj.finding_gstin(file_paths)
        if len(gstin) != 2:
            os.remove(file_paths)
            os.remove(file_paths + '.xml')
            resp.body = json.dumps({'error': '2 gstins are not found', 'aws_url': aws_url})
        else:
            body = {
                "gstin1": gstin[0],
                "gstin2": gstin[1]
            }
            s = requests.post(url=env.str('LAPIP_BASE_URL') + '/facility/seller-buyer-suggest-pdf/',
                              data=json.dumps(body), headers={"Content-Type": "application/json"})
            s = s.json()
            if 'buyer_gstin' in s and 'seller_gstin' in s:
                seller_gstin = s['seller_gstin']
                seller_pan = seller_gstin[2:12]
                if seller_pan not in file_conf:
                    os.remove(file_paths)
                    os.remove(file_paths + '.xml')
                    resp.body = json.dumps({'error': 'The configuration is not set for this seller', 'aws_url': aws_url})
                else:
                    inv_obj = InvoiceReading()
                    direct_usage_object = DirectUsage()
                    identify_flag = 0
                    for format_no in range(len(file_conf[seller_pan])):
                        # print(file_conf[seller_pan][format_no])
                        invoice_str_with_count = direct_usage_object.count_invoices(file_paths, file_conf[seller_pan][format_no])
                        if invoice_str_with_count[0]:
                            # print(seller_pan,format_no)
                            identify_flag = 1
                            try:
                                data = inv_obj.final_running(file_paths, file_conf[seller_pan][format_no])
                                data['seller_gstin'] = s['seller_gstin']
                                data['buyer_gstin'] = s['buyer_gstin']
                                # print(data)
                                try:
                                    for key in data:
                                        if type(data[key]) == list:
                                            try:
                                                data[key] = data[key][0]
                                            except Exception:
                                                data[key] = None
                                    try:
                                        data['date'] = str(str_obj.date_manipulation(data['date']).date())
                                    except:
                                        pass
                                    try:
                                        data['amount'] = float(data['amount'].replace(',', ''))
                                    except Exception:
                                        pass
                                    if data['amount'] is None and \
                                            'direct_conf' in file_conf[seller_pan][format_no]['amount']:
                                        # print('yes')
                                        data['amount']=direct_usage_object.amount_by_words(invoice_str_with_count[1],
                                                                    file_conf[seller_pan][format_no]['amount']['direct_conf'])

                                    data['aws_url'] = aws_url
                                    # print(file_conf[seller_pan][format_no]['amount'])
                                    try:
                                        resp.body = json.dumps(data)
                                    except Exception as e:
                                        resp.body = json.dumps({'error': e, 'aws_url': aws_url})
                                    try:
                                        os.remove(file_paths)
                                        os.remove(file_paths + '.xml')
                                    except Exception as e:
                                        resp.body = json.dumps({'error': e, 'aws_url': aws_url})
                                except Exception as e:
                                    # print(e)
                                    os.remove(file_paths)
                                    os.remove(file_paths + '.xml')
                                    resp.body = json.dumps({'error': 'can not able to identify some elements',
                                                            'aws_url': aws_url, 'err': e})
                            except Exception as e:
                                try:
                                    os.remove(file_paths)
                                    os.remove(file_paths + '.xml')
                                except:
                                    pass
                                resp.body = json.dumps({'error': e, 'aws_url': aws_url})
                            break
                        else:
                            continue
                    if identify_flag == 0:
                        os.remove(file_paths)
                        os.remove(file_paths + '.xml')

                        resp.body = json.dumps({'error': 'May be multiple invoices present or the backend config is wrong'})
            else:
                inv_obj = InvoiceReading()
                direct_usage_object = DirectUsage()
                seller_pan, conf_index = direct_usage_object.detect_format(file_paths)
                if seller_pan is not None:
                    try:
                        data = inv_obj.final_running(file_paths, file_conf[seller_pan][conf_index])
                        if seller_pan in gstin[0]:
                            data['seller_gstin'] = gstin[0]
                            data['buyer_gstin'] = gstin[1]
                        else:
                            data['seller_gstin'] = gstin[1]
                            data['buyer_gstin'] = gstin[0]
                        try:
                            for key in data:
                                if type(data[key]) == list:
                                    try:
                                        data[key] = data[key][0]
                                    except Exception:
                                        data[key] = None
                            if data['date'] is not None:
                                data['date'] = str(str_obj.date_manipulation(data['date']).date())
                            if data['amount'] is not None:
                                data['amount'] = float(data['amount'].replace(',', ''))

                            data['aws_url'] = aws_url
                            try:
                                resp.body = json.dumps(data)
                            except Exception as e:
                                resp.body = json.dumps({'error': e, 'aws_url': aws_url})
                            try:
                                os.remove(file_paths)
                                os.remove(file_paths + '.xml')
                            except Exception as e:
                                resp.body = json.dumps({'error': e, 'aws_url': aws_url})
                        except Exception as e:
                            os.remove(file_paths)
                            os.remove(file_paths + '.xml')
                            resp.body = json.dumps(
                                {'error': 'can not able to identify some elements', 'aws_url': aws_url})
                    except Exception as e:
                        os.remove(file_paths)
                        os.remove(file_paths + '.xml')
                        resp.body = json.dumps({'error': e, 'aws_url': aws_url})
                else:
                    os.remove(file_paths)
                    os.remove(file_paths + '.xml')
                    resp.body = json.dumps({'error': 'Gstins are not identified', 'aws_url': aws_url})
