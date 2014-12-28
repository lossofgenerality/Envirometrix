from django.test import TestCase
from django.test import Client
from datetime import *
from random import *
import itertools
from analysis.argtypes import *


def run_random(math_session):
    """
    Runs the given session with randomly varied parameters
    """
    c = Client()
    c.login(username='testbot', password='testbot')
    exec(math_session.extra_args)
    extra_args = list(itertools.chain(*args))
    expanded_args = []
    for arg in extra_args:
        if hasattr(arg, 'subargs'):
            expanded_args += arg.subargs
        else:
            expanded_args.append(arg)
    
    arg_dict = {'_extra_{}'.format(arg.label.replace(' ', '_')): [arg.default] for arg in expanded_args}
    
    
    nonempty_streams = [stream for stream in math_session.get_data() if len(stream['stream'].filelist)>0]
    
    streams = sample(nonempty_streams, randint(1, len(nonempty_streams)))
    
    dic = {}
    
    if all(['datasets' in stream for stream in streams]):
        common = [set for set in streams[0]['datasets']
            if all([
                set['name'] in [set2['name'] for set2 in stream['datasets']] for stream in streams            
                ])
        ]
        
        if len(common)>0:
            datasets = sample(common, min([3, randint(1, len(common))]))
            dic.update({u'_dataset_'+set['name'].replace(' ', '_'): [u'on'] for set in datasets})
        
    dic.update({u'_stream_'+stream['stream'].name.replace(' ', '_'): [u'on'] for stream in streams})
    dic.update(arg_dict)
    dic.update({
        u'startdate': [(streams[0]['stream'].latest-timedelta(1)).strftime('%m/%d/%Y')], 
        u'starttime': [u'12:00:00'], 
        u'enddate': [(streams[0]['stream'].latest-timedelta(1)).strftime('%m/%d/%Y')], 
        u'endtime': [u'12:30:00'],
        u'session': [math_session.name.replace(' ', '_')], 
        u'csrfmiddlewaretoken': [u'uAQInlHYMFcxX3R294t0TxoXxc8YUrbZ'], 
        u'querytype': [u'name']
    })
    response = c.post('/analysis/api/', dic)

def run_static(math_session):
    """
    Runs the given session with parameters which do not change between runs
    """
    c = Client()
    c.login(username='testbot', password='testbot')
    exec(math_session.extra_args)
    extra_args = list(itertools.chain(*args))
    expanded_args = []
    for arg in extra_args:
        if hasattr(arg, 'subargs'):
            expanded_args += arg.subargs
        else:
            expanded_args.append(arg)
    
    arg_dict = {'_extra_{}'.format(arg.label.replace(' ', '_')): [arg.default] for arg in expanded_args}
    
    stream = [stream for stream in math_session.data_streams.all() if len(stream.filelist)>0][0]
          
    dic = {
        u'startdate': [(stream.earliest+timedelta(1)).strftime('%m/%d/%Y')], 
        u'starttime': [u'12:00:00'], 
        u'enddate': [(stream.earliest+timedelta(1)).strftime('%m/%d/%Y')], 
        u'endtime': [u'12:30:00'],
        u'_stream_'+stream.name.replace(' ', '_'): [u'on'], 
        u'session': [math_session.name.replace(' ', '_')], 
        u'csrfmiddlewaretoken': [u'uAQInlHYMFcxX3R294t0TxoXxc8YUrbZ'], 
        u'querytype': [u'name'],
        u'_dataset_/S1/mostLikelyPrecipitation': [u'on'],
    }
    dic.update(arg_dict)
    response = c.post('/analysis/api/', dic)