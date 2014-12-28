from django.views.defaults import page_not_found
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import *
from data.models import *
from datetime import *
from django.conf import settings
from itertools import chain
import urllib
import os
from .file_previews import embed_code



@login_required
def math_gui(request):
    """
    View for the Mathematica script interface.
    """
    if request.user.is_superuser:
        session_list = MathematicaSession.objects.all()
    else:
        session_list = MathematicaSession.objects.filter(draft=False)
        
    return render(request, 'mathgui.html', {'session_list': session_list, 'user': request.user.first_name})
    
def analysis_api(request):
    """
    View that runs a Mathematica session with arguments given from the math_gui page.
    """
    session = MathematicaSession.objects.get(name=request.POST['session'])
    
    if 'startdate' in request.POST and not request.POST['startdate'] == '':
        startdate = datetime.strptime(request.POST['startdate'], '%m/%d/%Y').strftime('%Y%m%d')
        if 'starttime' in request.POST and not request.POST['starttime'] == '':
            starttime = datetime.strptime(request.POST['starttime'], '%H:%M:%S').strftime('%H%M%S')
        else:
            starttime = '000000'
            
        startdatetime = startdate + starttime
    else:
        startdatetime = ''
        
    
    if 'enddate' in request.POST and not request.POST['enddate'] == '':
        enddate = datetime.strptime(request.POST['enddate'], '%m/%d/%Y').strftime('%Y%m%d')
        if 'endtime' in request.POST and not request.POST['endtime'] == '':
            endtime = datetime.strptime(request.POST['endtime'], '%H:%M:%S').strftime('%H%M%S')
        else:
            endtime = '000000'
            
        enddatetime = enddate + endtime
    else:
        enddatetime = ''
    
    streams = []
    streamids = []
    datasets = []
    extra =""
    for key, item in request.POST.items():
        if key.startswith('_extra_'):
            extra = extra + '{}="{}"; '.format(key[7:], item)
        elif key.startswith('_stream_') and item == u'on':
            streams.append(key[8:])
            streamids.append(str(DataStream.objects.get(name=key[8:]).id))
        elif key.startswith('_dataset_') and item == u'on':
            datasets.append(key[9:])
            
    url = 'http://atmospherics.lossofgenerality.com/data/api/?ids={}'.format(','.join(streamids))
    if not startdatetime == '':
        url += '&start={}'.format(startdatetime)
    if not enddatetime == '':
        url += '&end={}'.format(enddatetime)
    
    api_output = urllib.urlopen(url).read()        
        
    if '<p>0 files found</p>' in api_output:
        context = {'status': 'Failed',
            'message': 'Sorry. There are no data files corresponding to the datastreams and timeframe that you selected. Please try again with different settings.'}
            
    elif 'files found' in api_output:
        data = r'Import["'+url+r'", {"HTML", "Hyperlinks"}]'
        extra += 'startDateTime="{}"; endDateTime="{}"; datasets="{}";'.format(startdatetime, enddatetime, format(','.join(datasets)))
        extra +='streams="{}";'.format(','.join(streams))
        extra_args = {'extra_args': extra, 'data': data}
        
        res = session.start_session(extra_args, request.user)
          
        if res:
            if not res.id:
                tries = 1
                while not res.id and tries < 25:
                    res = session.start_session(extra_args, request.user)
                    tries += 1
                if not res.id:
                    Log.debug('atmospherics.analysis.tasks.mathematica_session', 'math session {} started by {} was not assigned an id after {} tries.'.format(session.name, request.user, tries))
                    
                    context = {'status': 'Failed',
                        'message': 'Something went wrong. Your request was tried several times and still did not work. Please check your settings and try again.'}
                    return response
            else:
                Log.debug('atmospherics.analysis.tasks.mathematica_session', 'math session {} started by user {} given id {}'.format(session.name, request.user, res.id))
                
                context = {'status': 'Success',
                    'message': 'Thank you. Your Mathematica session will be run soon. You will recieve an email when it is complete.'}
        else:
            context = {
                'status': 'Success',
                'message': '''
                    Thank you. Your Mathematica session will be run soon but there will be a delay while our server finish running another task.
                    You will recieve an email when it is complete.'''
                    }
    else:
        Log.debug('atmospherics.analysis.tasks.mathematica_session', 'math session {} started by user {} returned an api error.\napi call: {}'.format(session.name, request.user, url))
        
        context = {'status': 'Failed',
            'message': 'Sorry. Something went wrong with the data api. Please review your settings and try again.'}
    
    return render(request, 'redirect.html', context)
    
    
def results_page(request, user, dir):
    """
    View for the page which distpays the output of a particular script.
    """
    session = dir[:-12]
    time = datetime.strptime(dir[-4:], '%H%M').strftime('%I:%M %p')
    date = datetime.strptime(dir[-11:-5], '%m%d%y').strftime('%x')
    
    
    full_path = os.path.join(settings.MEDIA_ROOT, user, 'output', dir)
    baseurl = 'http://atmospherics.lossofgenerality.com{}'.format(os.path.join(settings.MEDIA_URL, user, 'output', dir))
    
    
    # !!! comment out before commit !!! #
    #baseurl = 'http://192.168.0.111:8000{}'.format(os.path.join(settings.MEDIA_URL, user, 'output', dir))
    
    if not os.path.exists(full_path):
        return page_not_found(request)
    else:
        itemlist = []
        
        files = os.listdir(full_path)
        urls = [os.path.join(baseurl, file) for file in files]
        
        for i in range(len(urls)):
            ext = os.path.splitext(urls[i])[1]
            size = os.path.getsize(os.path.join(full_path, files[i]))
            entry = {
                'name': files[i],
                'url': urls[i],
                'size': size
            }
            if ext in embed_code:
                if '{content}' in embed_code[ext]:
                    contents = '<br/>'.join([line for line in open(os.path.join(full_path, files[i])).readlines()])
                    entry['code'] = embed_code[ext].format(**{'content': contents })
                else:
                    entry['code'] = embed_code[ext].format(**{'url': urls[i]})
                
            itemlist.append(entry)
            
    return render(request, 'results.html', {'item_list': itemlist, 'session': session, 'date': date, 'time': time, 'runner': user})
    
    
def output_index(request, user):
    """
    View for the page which lists all script outputs for a user.
    """
    full_path = os.path.join(settings.MEDIA_ROOT, user, 'output')
    baseurl = 'http://atmospherics.lossofgenerality.com/{}'.format(os.path.join('output', user))
    
    if not os.path.exists(full_path):
        return page_not_found(request)
    else:
        itemlist = []
        
        dirs = os.listdir(full_path)
        rel_urls = [os.path.join('.', dir) for dir in dirs]
        abs_urls = [os.path.join(baseurl, dir) for dir in dirs]
        
        for i in range(len(rel_urls)):
            dirpath = os.path.join(full_path, dirs[i])
            size = sum([os.path.getsize(os.path.join(dirpath, file)) for file in os.listdir(dirpath)])
            
            try:
                date = datetime.strptime(dirs[i][-11:-5], '%m%d%y').strftime('%x')
                time = datetime.strptime(dirs[i][-4:], '%H%M').strftime('%I:%M %p')
            except ValueError:
                pass
            
            itemlist.append({
                'name': dirs[i][:-12],
                'url': rel_urls[i],
                'date': date,
                'time': time,
                'numfiles': len(os.listdir(os.path.join(full_path, dirs[i])))-1,
                'size': size
            })
    
    itemlist.sort(key = lambda x: datetime.strptime(x['date']+x['time'], '%x%I:%M %p'), reverse=True)
    
    return render(request, 'output.html', {'item_list': itemlist, 'user': user})
    
    
    
    
    
    
    
    
    