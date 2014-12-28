import json
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from .models import *
from analysis.models import *
import collections
import urllib
import re

from random import *

from .argtypes import *

@dajaxice_register
def search_data(request, session_name, type, string):
    """
    Returns data streams corresponding to Math session and search box.
    """
    session = MathematicaSession.objects.get(name=session_name)
    response = {'datastreams':[]}
    
    if type == 'name':
        response['datastreams'] = [stream.js for stream in session.data_streams.filter(name__icontains=string)]
            
        
    elif type == 'organization':
        response['datastreams'] = [stream.js for stream in session.data_streams.filter(organization__icontains=string)]
            
    elif type == 'tags':
        tags = string.split(", ")
        for tag in tags:
            response['datastreams'] = [stream.js for stream in session.data_streams.filter(tags__icontains=tag)]
                
    if len(response['datastreams'])==0:
            response['datastreams'] = ["{'name':'No matching datastreams were found'}"]
            
    return simplejson.dumps(response)
    
    
@dajaxice_register
def get_args(requests, session_name):
    """
    Builds required interface content for given Math script.
    """
    session = MathematicaSession.objects.get(name=session_name)
    exec(session.extra_args)
    response = {
        'head': build_head(args),
        'body': build_menu(args)
    }
    return simplejson.dumps(response)
    
    
@dajaxice_register
def datasets(request, session_name, stream_names):
    """
    Returns list of datasets which all of the given data streams share.
    """
    session = MathematicaSession.objects.get(name=session_name)
    streams = [DataStream.objects.get(name=stream_name) for stream_name in stream_names]
    streamsets = [datastream['datasets'] for datastream in session.get_data() \
        if datastream['stream'] in streams]
    
    if any([stream.start for stream in streams]):
        start = min([stream.start for stream in streams if stream.start])
        start = start.strftime('%m/%d/%Y')
        end = max([stream.end for stream in streams if stream.end])
        end = end.strftime('%m/%d/%Y')
    else:
        start, end = None, None
    
    if len(stream_names) == 0:
        common = []
    elif len(stream_names) == 1:
        common = streamsets[0]
    else:
        common = [
            set for set in streamsets[0] if all([
                set['name'] !=u'none',
                all([set['name'] in [set2['name'] for set2 in sets] for sets in streamsets])
                ])
            ]
    
    response = {
        'datasets': common,
        'start': start,
        'end': end
    }
    return simplejson.dumps(response)
    