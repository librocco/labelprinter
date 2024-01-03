from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, KeepInFrame
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
import datetime, cgi, os, tempfile
from reportlab.graphics.barcode.code128 import Code128

from threading import Thread

try:
    from html import escape
except ImportError:
    from cgi import escape


debug_mode = 0

printer = "QL-500RAW"
file = "/tmp/QL-500.ps"
openoffice = 'openoffice'
printerDevice = "/dev/usb/lp0"
psfilePath = "/tmp/QL-500.ps"


def checkPrinter():
    command = """sudo dmesg |grep "vid 0x04F9 pid 0x2015" |perl -pe "s/.*usb(lp[0-9]).*/\/dev\/usb\/\$1/"|tail -n1"""
    return os.popen(command).read().strip()

def print_ps_file(psfilePath = psfilePath, printerDevice=printerDevice):
    command = """
    cat %s |\
    gs -q -dBATCH -dPARANOIDSAFER -dQUIET -dNOPAUSE -sDEVICE=cups  -r300x300 -sOutputFile=- - 2> /dev/null |\
    rastertoptch dummyjob dummyuser dummytitle 1 'Align=Right BytesPerLine=90 PixelXfer=ULP PrintQuality=High PrintDensity=0 SoftwareMirror LabelPreamble';
    """ % (psfilePath,)
    (stdin, stdout, stderr) = os.popen3(command)
    rawdata = stdout.read()
    rawdata = rawdata[:-1] + '\x1a\x1b\x40'
    printerDevice = checkPrinter()
    if printerDevice:
        fh = open(printerDevice,'w')
        if not debug_mode:
            fh.write(rawdata)
        fh.close()

def print_pdf_file(pdffilepath, printerDevice=printerDevice):
    (fd, filepath) = tempfile.mkstemp('mylabels.ps')
    os.system("pdf2ps '%s' '%s'" % (pdffilepath, filepath))
    print_ps_file(filepath, printerDevice=printerDevice)
    os.unlink(filepath)

styles = {}
styles['title'] = ParagraphStyle(name='title',
                                  fontSize = 12,
                                  borderWidth=0,
                                  borderColor='black',
                                  leading = 12,
                                  leftIndent=3*mm,
                                  rightIndent=3*mm,
                                  fontname='Times-Roman',
                                  alignment=TA_CENTER,
                                  )
styles['website'] = ParagraphStyle(name='website', 
                                  fontSize = 12,
                                  borderWidth=0,
                                  leading = 12,
                                  alignment=TA_CENTER,
                                  leftIndent=3*mm,
                                  )
styles['publisher'] = ParagraphStyle(name='publisher', 
                                  fontSize = 12,
                                  alignment=TA_CENTER,
                                  leftIndent=3*mm,
                                  )
styles['isbn'] = styles['publisher']
pagesize=(62*mm, 29 * mm )

def draw_label_torino(bookdata, canvas, pagesize=pagesize):
    draw_label_generic(bookdata, canvas, pagesize=pagesize, website="www.libri-usati.com")
    canvas.showPage()

def draw_label_generic(bookdata, canvas, pagesize=pagesize, website=""):
    sanitize_bookdata(bookdata, canvas, pagesize=pagesize)
    isbn = bookdata['isbn']
    barWidth = (43.0*mm)/(max(len(isbn),6)*11 + 11)
    barcode = Code128(isbn,  barWidth=barWidth, barHeight=9*mm)
    #barcode.width = 10*mm
    barcode.drawOn(canvas, -3*mm, 13*mm)

    bookdata['website'] = "<b>%s</b>" % website
    title = dict(pos=[1*mm,1*mm], size=(pagesize[0],6*mm), name='title')
    isbn = dict(pos=[-15*mm,16*mm], size=(pagesize[0],8*mm), name='isbn')
    website = dict(pos=[1*mm, 20*mm], size=(pagesize[0],12*mm), name='website')
    process_fields(bookdata, canvas, pagesize=pagesize, fields=(title,isbn, website))
    canvas.setFont('Times-Bold',20)
    bookdata['price'] = float(bookdata['price'])
    canvas.drawCentredString(50*mm,16*mm, u'\u20ac ' + ('%.2f' % bookdata['price']).replace('.',','))


def sanitize_bookdata(bookdata, canvas, pagesize=pagesize):
    for item in ('title', 'publisher'):
        bookdata[item] = escape(bookdata[item])
    try:
        year = int(bookdata['year'])
        if not 1980 < year < datetime.datetime.now().year: raise ValueError
    except ValueError:
        bookdata['year'] = ''

def process_fields(bookdata, canvas, fields, pagesize=pagesize):
    for field in fields:
        p = Paragraph(bookdata[field['name']],styles[field['name']])
        k = KeepInFrame(field['size'][0], field['size'][1],[p],mode='shrink')
        w,h = k.wrapOn(canvas, field['size'][0], field['size'][1] )
        vpos = pagesize[1] - field['pos'][1] - h
        k.drawOn(canvas, field['pos'][0], vpos)


def draw_label_cuneo(bookdata, canvas, pagesize=pagesize):
    draw_label_generic(bookdata, canvas, pagesize=pagesize,
            website="www.illibraiocuneo.it")
    logo_filename = os.path.join(os.path.dirname(__file__) , 'logo_cuneo.png')
    canvas.drawImage(logo_filename, x=41*mm, y=8*mm, width=6*mm,  height=6*mm, preserveAspectRatio=True)
    current_year = str(datetime.datetime.now().year)
    canvas.setFont('Times-Roman',16)
    canvas.drawCentredString(54*mm,9*mm, current_year)
    canvas.showPage()


class LabelPrinter(Thread):
    def __init__(self, labels, draw_label=draw_label_cuneo):
        Thread.__init__(self)
        self.labels = labels
        self.draw_label = draw_label
    def run(self):
        (fd, canvasFileName) = tempfile.mkstemp('Labels.pdf')
        mycanvas = canvas.Canvas(canvasFileName,pagesize=pagesize)
        for label in self.labels:
            self.draw_label(label, mycanvas)
        mycanvas.save()
        print_pdf_file(canvasFileName)
        if not debug_mode:
            os.unlink(canvasFileName)



class LabelPrinterJob(object):
    def __init__(self, pagesize=pagesize, labeltype='cuneo'):
        if labeltype == 'cuneo':
            self.draw_label = draw_label_cuneo
        else:
            self.draw_label = draw_label_torino
        self.labels = []
    def addLabel(self,bookdata):
        #bookdata['price'] = "%.2f" % bookdata['price']
        #mybookdata = dict(map(lambda x: (x,str(bookdata[x])), bookdata.keys() )) 
        self.labels.append(bookdata)
    def printLabels(self):
        thr = LabelPrinter(self.labels, draw_label=self.draw_label)
        thr.start()



def isbn_prettify(isbn):
    if len(isbn) != 13:
        return isbn
    isbn = isbn[:3] + '-' + isbn[3:5]+ '-' + isbn[5:9]+ '-' + isbn[9:12]+ '-' + isbn[12:]
    return isbn


if __name__ == '__main__':
    try:
        from sqlite3 import dbapi2 as sqlite # python 2.5
    except ImportError:
        from pysqlite2 import dbapi2 as sqlite
    db = sqlite.connect('/home/silvio/.a_cache/old2_libri.db',isolation_level=None)
    db.text_factory = str
    cursor = db.cursor()
    import random
    n = random.randint(100,10000)
    cursor.execute("SELECT TITOLO, AUTORE, EDITORE, PREZZO, ANNO, ISBN FROM LIBRI2008 LIMIT 1 offset %i" % n)
    row = cursor.fetchone()
    c = canvas.Canvas("black.pdf",
#                      pagesize=(pagesize[0], pagesize[1]-11.5*mm)

                      pagesize=pagesize,
                    )
    while row:
        (title, website, publisher, price, year, isbn) = row
        draw_label(dict(
              title=title,
              website=website,
              publisher=publisher,
              price=price,
              year=year,
              isbn=isbn
              ),c)
        row = cursor.fetchone()
    c.save()
    print_pdf_file("black.pdf")
