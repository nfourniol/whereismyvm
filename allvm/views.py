
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from allvm.services.hypervisor import HypervisorService
from allvm.dto.hypervisorDto import HypervisorDataList
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
from django.http import HttpResponseServerError
from allvm.services.email import EmailService
from allvm.services.utils import ConfigService
from datetime import datetime
#from guppy import hpy


def index(request):
    
    hypervisorService: HypervisorService = HypervisorService()
    hypervisorDataList: HypervisorDataList = hypervisorService.getHypervisorDataList()

    template = loader.get_template('allvm/index.html')
    context = {
        'hypervisorDataList': hypervisorDataList,
    }
    return HttpResponse(template.render(context, request))


#def memory(request):
#    import gc
#    n = gc.collect()
#    print("**\n**\n**\nNumber of unreachable objects collected by GC:", n)  
#    print("**\n**\n**\n")
#
#    hp = hpy()
#    heap = hp.heap()
#    print(heap.all)
#
#    return HttpResponse()


def render_to_pdf(request):

    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    formatted_now = now.strftime("%d/%m/%Y %H:%M:%S")

    hypervisorService: HypervisorService = HypervisorService()
    hypervisorDataList: HypervisorDataList = hypervisorService.getHypervisorDataList()

    template = loader.get_template('allvm/index_for_pdf.html')
    context = {
        'hypervisorDataList': hypervisorDataList,
        'formatted_now' : formatted_now
    }

    html = template.render(context, request)
    result = BytesIO()
 
    #This part will create the pdf.
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    # During the creation of the documnent we will have an error log "missing explicit frame definition for content or just static frames"
    # => it's for the use of an external css file xhtml2pdf can't manage this, it's not a problem beause we also copied css directly without file linking
    if not pdf.err:
        cfg = ConfigService()
        mailService = EmailService()
        for recipient in cfg.getMailRecipients():
            mailService.sendEmailWithAttachment(recipient, 'Where Is My VM?', 'See attchment', 'whereismyvm.pdf', result.getvalue(), 'application/pdf')

        context = {
            'status': 'OK',
        }
        template = loader.get_template('allvm/status_send_pdf.html')
        return HttpResponse(template.render(context, request))
    else:
        context = {
            'status': 'KO',
        }
        template = loader.get_template('allvm/status_send_pdf.html')
        return HttpResponseServerError(template.render(context, request))

