#-coding: utf-8-

element = {
    "isbn": "9788889385173",
    "author": " Giovanzana M., Musso D.",
    "publisher": "Terre di Mezzo",
    "title": u"Io boicotto Nestlé",
    "price": "9",
    "year": "2005",
    "out_of_print": "false",
    "edited_by": "",
    "category": "338",
    "synopsis": "",
    "parent_warehouse_quantity": "1",
    "inout": "in",
    "quantity": "1",
    "warehouse_price": "",
}

from labelprinter.label import LabelPrinterJob

job = LabelPrinterJob(labeltype='cuneo')
job.addLabel(element)
job.printLabels()


print("DONe")
