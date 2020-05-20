import falcon
from environs import Env
from falcon_multipart.middleware import MultipartMiddleware

from general_invoice_reading_api import InvoiceParserV2
from inv_reading import InvoiceParser

env = Env()
env.read_env()


app = falcon.API(middleware=[MultipartMiddleware()])

app.add_route('/invoice-parse', InvoiceParserV2(), suffix='upload')

app.add_route('/test', InvoiceParser(), suffix='upload')
