from __future__ import absolute_import
from logger.utils import shared_task
import pysftp
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from celery.app import shared_task as shared_task_celery
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from logger.models import Log
import os
from datetime import *



@shared_task
def mathematica_package(math_package, extra_args, user):
    """
    Runs the given Math package on the Thorek01 server.
    """
    ssh=pysftp.Connection(settings.SSH_HOST, username=settings.SSH_USER, password=settings.SSH_PASSWORD)
    
    temp = ssh.execute('mktemp -d')[0].rstrip('\n')
    ssh.chdir(temp)
    
    code, matches = math_package.replace_exports(temp)
        
    code = code.replace('{extra_args}', extra_args['extra_args'])
    code = code.replace('{data}', extra_args['data'])
    
    Log.debug('atmospherics.analysis.tasks.mathematica_package', code)
    code = code.replace("'", '\'"\'"\'')
    command = "echo '{}' > {}/package.m".format(code, temp)
    ssh.execute(command)

    ret = ssh.execute('xvfb-run -s "-screen 0 640x480x24" math -script {}/package.m &\n\n\n\n'.format(temp))
    
    if ret:
        message = 'A message was returned by mathematica script  {}.m:\n{}'.format(math_package.name, ret[-100:])
        Log.info('atmospherics.analysis.tasks.mathematica_package', message)

    #ssh.execute('rm {}'.format(os.path.join(temp, 'package.m')))
    
    target = os.path.join(settings.MEDIA_ROOT, user.username, 'output', math_package.name.replace(' ', '_')+datetime.now().strftime('_%m%d%y_%H%M'))
    os.makedirs(target)
    ssh.get_d(temp, target)
    
    #ssh.execute('rm -rf {}'.format(temp))
    ssh.execute('disown')
    ssh.close()

    message = 'Mathematica package {} run.\nOutput saved to:\nhttp://atmospherics.lossofgenerality.com/{}'.format(math_package.name, os.path.join('output', user.username, os.path.split(target)[1]))
    Log.info('atmospherics.analysis.tasks.mathematica_package', message)
    if user.email:
        subject = 'Atmospherics Mathematica {} Complete'.format(math_package.name)
        from_email = 'Atmospherics<atmospherics@lossofgenerality.com>'
        email = EmailMultiAlternatives(subject,
                                       message,
                                       from_email,
                                       [user.email])
        email.send()
    

@shared_task_celery
def mathematica_session(math_session, extra_args, user):
    """
    Runs the given Math session on the Thorek01 server.
    """
    ssh=pysftp.Connection(settings.SSH_HOST, username=settings.SSH_USER, password=settings.SSH_PASSWORD)

    if ssh.execute('pidof MathKernel') or ssh.execute('pidof Mathematica'):
        ssh.close()
        mathematica_session.retry(countdown=5*60, max_retries=(60/5)*24)
    
    temp = ssh.execute('mktemp -d')[0].rstrip('\n')
    ssh.chdir(temp)
    
    code, matches = math_session.replace_exports(temp)
        
    code = code.replace('{extra_args}', extra_args['extra_args'])
    code = code.replace('{data}', extra_args['data'])
    
    Log.debug('atmospherics.analysis.tasks.mathematica_session', code)
    code = code.replace("'", '\'"\'"\'')
    command = "echo '{}' > {}/package.m".format(code, temp)
    ssh.execute(command)

    ret = ssh.execute('xvfb-run -s "-screen 0 640x480x24" math -script {}/package.m &\n\n\n\n'.format(temp))
    
    target = os.path.join(settings.MEDIA_ROOT, user.username, 'output', math_session.name.replace(' ', '_')+datetime.now().strftime('_%m%d%y_%H%M'))
    
    os.makedirs(target)
    ssh.get_d(temp, target)
    
    if ret:
        message = '''
            A message was returned by mathematica script  {}.m:\n
            (trimmed to contain only the last 100 lines) \n\n
            {}
        '''.format(math_session.name, '\n'.join(ret[-100:]))
        Log.info('atmospherics.analysis.tasks.mathematica_session', message)
        
        with open(os.path.join(target, 'response.txt'), 'w') as logfile:
            logfile.write(message)
    
    #ssh.execute('rm -rf {}'.format(temp))
    ssh.execute('disown')
    ssh.close()

    message = 'Mathematica session {} run.\nOutput saved to:\nhttp://atmospherics.lossofgenerality.com/{}'.format(math_session.name, os.path.join('output', user.username, os.path.split(target)[1]))
    Log.info('atmospherics.analysis.tasks.mathematica_session', message)
    if hasattr(user, 'email'):
        subject = 'Atmospherics Mathematica {} Complete'.format(math_session.name)
        from_email = 'Atmospherics<atmospherics@lossofgenerality.com>'
        email = EmailMultiAlternatives(subject,
                                       message,
                                       from_email,
                                       [user.email])
        email.send()
 
        
@shared_task
def run_python_scripts():
    """
    Runs the given python script locally.
    """
    from .models import PythonScript
    
    for script in PythonScript.objects.filter(periodic=True):
        script.run_script()


#Copyright 2014-present lossofgenerality.com