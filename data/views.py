from django.views.defaults import page_not_found, bad_request
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from logger.models import Log
from .models import *
from datetime import *


def data_api(request):
    """
    View which accepts queries and returns a list of links to data files which fit.
    """
    if not ('set' in request.GET or 'tag' in request.GET or 'org' in request.GET or 'ids' in request.GET):
        return page_not_found(request)
    
    elif 'set' in request.GET:
        try:
            datastreams = [DataStream.objects.get(name=request.GET["set"])]
        except DataStream.DoesNotExist:
            return page_not_found(request)
  
    elif 'ids' in request.GET:
        datastreams = []
        for id in request.GET['ids'].strip(',').split(','):
            try:
                datastreams.append(DataStream.objects.get(pk=id))
            except DataStream.DoesNotExist:
                pass
  
    elif 'tag' in request.GET:
         datastreams = DataStream.objects.filter(tags__icontains=request.GET["tag"])
            
    elif 'org' in request.GET:
         datastreams = DataStream.objects.filter(organization__icontains=request.GET["org"])
         
    if len(datastreams) == 0:
            return page_not_found(request)
            
    response = HttpResponse()
    
    files = []
    i=0
    for datastream in datastreams:
        if len(datastream.filelist)>0:
            for file in datastream.filelist:
                filevars = datastream.parse(file)
                add = True            
                
                filestart = filevars['startDatetime']
                fileend = filevars['startDatetime']
                
                if 'start' in request.GET and 'end' in request.GET:
                    if any([
                        datetime.strptime(request.GET['start'], "%Y%m%d%H%M%S") >= fileend,
                        datetime.strptime(request.GET['end'], "%Y%m%d%H%M%S") <= filestart
                    ]):
                        add = False
                        
                elif 'start' in request.GET:
                    if not datetime.strptime(request.GET['start'], "%Y%m%d%H%M%S") >= fileend:
                        add = False
                        
                elif 'end' in request.GET:
                    if not datetime.strptime(request.GET['end'], "%Y%m%d%H%M%S") <= filestart:
                        add = False
                        
                if add: 
                    files.append(file)
    
                
            i += len(files)
            for file in sorted(files):
                url = os.path.join('..', file)
                response.write('<p><a href="{}">{}</a></p>'.format(url, file))
            
    response.write('<p>{} files found</p>'.format(i))
    
    return response
        
    
        
    


#Copyright 2014-present lossofgenerality.com
#License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html