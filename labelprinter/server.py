import bobo
from labelprinter.label import LabelPrinterJob
import json

@bobo.query('/printlabel/:labeltype?/')
def single_label(callback='funk', jsondata='', labeltype='cuneo'):
    if jsondata:
        data = json.loads(jsondata)
        job = LabelPrinterJob(labeltype=labeltype)
        if type(data) is type({}):
            data = [data]
        for element in data:
            job.addLabel(element)
        job.printLabels()
        return "%s({'status':[{'label_name':''}]});" % callback
    else:
        return "No data supplied"
