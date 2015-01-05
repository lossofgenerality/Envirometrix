from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from logger.utils import shared_task
from logger.models import Log
from .tasks import *
from data.models import *
from datetime import *
import pysftp
import argtypes
import os
import re

#from .argtypes import *

class SeparatedValuesField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def _to_python(self, value):
        if not value: return
        if isinstance(value, list):
            return value
        return [x.strip() for x in value.split(self.token)]

    def get_db_prep_value(self, value, *args, **kwargs):
        if not value:
            return
        value = self._to_python(value)
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([s for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
        

def user_script_dir(instance, filename):
    return os.path.join(instance.user.username, 'scripts', filename)
    
mathematica_tips = """<ul style="color:#505050">
        <li>To import your extra arguments, include the tag {extra_args} at the beginning of your script.</li>
        <li>startDateTime and endDateTime come for free; they are strings of the form "YYYYMMDDHHMMSS". To parse as a Mathematica datetime list use DateList[{StringInsert["20150905120000","/", {5,7,9,11,13}], {"Year", "Month", "Day", "Hour24", "Minute", "Second"}}]. To parse an integer, use  ToExpression[startDateTime]</li>
        <li>datasets also comes for free; it is a string of the names of the selected datasets separated by commas. To parse as a list of strings use StringSplit[datasets, ","].</li>
        <li>To import data from the server, use the {data} tag. e.g. datafiles = {data}; will load the list of data urls under the name datafiles.</li>
        <li>All output will be saved to your user folder in a subdirectory corresponding to each session run. Use only filenames (not full paths) in your Export functions and everything else will be done automatically.</li>
        <li>The scripts are run using 16 parallel Mathematica kernels so you Mathematica\'s parallelizing functions wherever possible for faster execution.</li>
        <li>(NOT YET SUPPORTED) If your script outputs videos which you would like hosted on YouTube, export an empty txt file with filename ".youtube.txt" in the same directory as your videos.</li>
    </ul>"""


class MathematicaSession(models.Model):
    """
    This class represents a task to analyze using Mathematica
    """

    """
    Options
    """

    """
    Fields
    """
    name = models.CharField(max_length=200)
        
    description = models.TextField(null=True, blank=True)
        
    mathematica_script = models.TextField(
        help_text='Mathematica tips:\n{}'.format(mathematica_tips))
    
    user = models.ForeignKey(User)
    
    extra_args = SeparatedValuesField(default='args = [[]]', blank=True, null=True, 
        help_text='''
            <p style="color:#505050">
                A two dimensional array of ArgType objects where the inner lists 
                represent args which will be displayed in the same row. This may
                contain additional python code to improve readability or dynamically
                generate values.
                </br></br>
                However, this <b>must</b> end with the declaration of a variable
                named "args" which contains the array.
            </p>
            <center>{}</center>
            '''.format(argtypes.doc_table())
        )

    data_streams = models.ManyToManyField(DataStream,
        help_text='The data streams which may be used with this script')
        
    dataset_test = models.TextField(default='lambda set: True', blank=False,
        help_text='''
            A Python function which takes a dictionary of information about
            a dataset and returns a boolean indicating whether the dataset
            is acceptable for use with this script. An example of the input
            dictionary: 
            {
                'shape': (160, 221), 
                'CodeMissingValue': '-9999.900391', 
                'name': '/S1/convectPrecipFraction', 
                'DimensionNames': 'nscan,npixel'
            }
            '''
        )
        
    draft = models.BooleanField(default=True,
        help_text='''
            If selected, this session will not appear in the interface.
        '''
        )
        
    """
    Methods
    """
    def __unicode__(self):
        return self.name

    def save(self, start_session=False, extra_args={}, user=None, **kwargs):
        if not self.pk is None:
            if start_session:
                super(MathematicaSession, self).save(**kwargs)
                self.start_session({}, email)
            else:
                super(MathematicaSession, self).save(**kwargs)
        else:
            super(MathematicaSession, self).save(**kwargs)

    def start_session(self, extra_args, user):
        return mathematica_session.delay(self, extra_args, user)
        
    def replace_exports(self, tempdir):
        """
        Injects the temporary directory path into all Export calls in the script and returns their locations.
        """
        code = self.mathematica_script
        
        regex = r'Export\[+\s*(?P<file>.+?)\s*,'
        
        code = re.sub(regex, 'Export["{}/"<>\g<file>, '.format(tempdir), code)
        matches = re.findall(regex, code)
                        
        return code, matches
                
    def get_data(self):
        all_data = []
        dataset_test = eval(self.dataset_test)
        
        for stream in self.data_streams.all():
            dic = {'stream': stream}
            datasets = eval(stream.datasets)
            try:
                dic['datasets'] = [set for set in datasets if dataset_test(set)]
            except KeyError:
                pass
            all_data.append(dic)
            
        return all_data
            
        
        
        
class MathematicaPackage(models.Model):
    """
    This class represents a Mathematica package file (*.m) uploaded by a user
    """

    """
    Options
    """

    """
    Fields
    """
    name = models.CharField(max_length=200)
        
    description = models.CharField(max_length=200, null=True, blank=True)
    
    file = models.FileField(max_length=200, upload_to=user_script_dir,
        help_text='Mathematica tips:\n{}'.format(mathematica_tips))
    
    mathematica_script = models.TextField()
    
    user = models.ForeignKey(User)

    extra_args = SeparatedValuesField(default='args = [[]]', blank=True, null=True, 
        help_text='''
            <p style="color:#505050">
                A two dimensional array of ArgType objects where the inner lists 
                represent args which will be displayed in the same row. This may
                contain additional python code to improve readability or dynamically
                generate values.
                </br></br>
                However, this <b>must</b> end with the declaration of a variable
                named "args" which contains the array.
            </p>
            <center>{}</center>
            '''.format(argtypes.doc_table())
        )
        
    data_streams = models.ManyToManyField(DataStream,
        help_text='The data streams which may be used with this script')
    """
    Methods
    """
    def __unicode__(self):
        return self.name

    def save(self, start_package=False, extra_args={}, user=None, **kwargs):
        if not self.pk is None:
            if start_package:
                super(MathematicaPackage, self).save(**kwargs)
                self.run_package(email)
            else:
                super(MathematicaPackage, self).save(**kwargs)
        else:
            super(MathematicaPackage, self).save(**kwargs)

    def start_package(self, extra_args, user):
        mathematica_package.delay(self, extra_args, user)
        
    def replace_exports(self, tempdir):
        """
        Injects the temporary directory path into all Export calls in the script and returns their locations.
        """
        with open (self.file.path, 'r') as file:
            code = file.read()
                
        regex = r'Export[+\s*[\'\"]+(?P<file>.+?)[\'\"]+\s*,'
        
        code = re.sub(regex, 'Export["{}/\g<file>", '.format(tempdir), code)
        matches = re.findall(regex, code)
                        
        return code, matches

        

class PythonScript(models.Model):
    """
    This class represents a Mathematica package file (*.m) uploaded by a user
    """
    
    """
    Fields
    """
    name = models.CharField(max_length=200, null=True,
        help_text=r'A useful description')
        
    description = models.CharField(max_length=200, null=True, blank=True)
        
    user = models.ForeignKey(User)
        
    code = models.TextField(
        help_text=r'A Python script')
        
    extra_args = SeparatedValuesField(default='args = [[]]', blank=True, null=True, 
        help_text='''
            <p style="color:#505050">
                A two dimensional array of ArgType objects where the inner lists 
                represent args which will be displayed in the same row. This may
                contain additional python code to improve readability or dynamically
                generate values.
                </br></br>
                However, this <b>must</b> end with the declaration of a variable
                named "args" which contains the array.
            </p>
            <center>{}</center>
            '''.format(argtypes.doc_table())
        )
        
    data_streams = models.ManyToManyField(DataStream,
        help_text='The data streams which may be used with this script')
        
    """
    Methods
    """
    def __unicode__(self):
        return self.name
        
    def save(self, start_session=False, extra_args={}, user=None, **kwargs):
        if not self.pk is None:
            if start_session:
                super(PythonScript, self).save(**kwargs)
                self.start_session({}, email)
            else:
                super(PythonScript, self).save(**kwargs)
        else:
            super(PythonScript, self).save(**kwargs)
        
    @shared_task
    def run_script(self):
        code = self.code.replace("'", '\'"\'"\'')
        code = code.replace("\\", "\\\\")
        exec(code)
    
    
    
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^analysis\.models\.SeparatedValuesField"])
    


#Copyright 2014-present lossofgenerality.com
#License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html