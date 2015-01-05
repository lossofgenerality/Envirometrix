from django.db import models
from datetime import *
from django.conf import settings
from logger.utils import shared_task
from logger.models import Log
import os.path
import string
import h5py
import pysftp
import os
import re

from format_tags import *

mathematica_tips = """
    <ul style="color:#505050">
        <li>To import your extra arguments, include the tag {extra_args} at the beginning of your script.</li>
        <li>startDateTime and endDateTime come for free; they are strings of the form "YYYYMMDDHHMMSS". To parse as a Mathematica datetime list use DateList[{StringInsert["20150905120000","/", {5,7,9,11,13}], {"Year", "Month", "Day", "Hour24", "Minute", "Second"}}]. To parse an integer, use  ToExpression[startDateTime]</li>
        <li>datasets also comes for free; it is a string of the names of the selected datasets separated by commas. To parse as a list of strings use StringSplit[datasets, ","].</li>
        <li>To import data from the server, use the {data} tag. e.g. datafiles = {data}; will load the list of data urls under the name datafiles.</li>
        <li>All output will be saved to your user folder in a subdirectory corresponding to each session run. Use only filenames (not full paths) in your Export functions and everything else will be done automatically.</li>
        <li>The scripts are run using 16 parallel Mathematica kernels so you Mathematica\'s parallelizing functions wherever possible for faster execution.</li>
        <li>(NOT YET SUPPORTED) If your script outputs videos which you would like hosted on YouTube, export an empty txt file with filename ".youtube.txt" in the same directory as your videos.</li>
    </ul>
    """
    
    
class DataStream(models.Model):
    """
    This class represents metadata about the atmospheric data sources on the server
    """
    
    """
    Fields
    """
    name = models.CharField(max_length=200, null=True,
        help_text=r'A useful description')
        
    organization = models.CharField(max_length=200, null=True, blank=True,
        help_text=r'The organization that produced this data')
        
    description = models.TextField(blank=True,
        help_text=r'A useful explanation of the purpose of this data.')
        
    tags = models.CharField(max_length=200, null=True,
        help_text=r'A comma separated list of relevant terms. These are used by the data api to find related data streams')
        
    datasets = models.TextField(blank=True, default='[]',
        help_text=r'A If each file contains more than one dataset (e.g. HDF5 files), a comma separated list of the included datasets.')
        
    naming_scheme = models.CharField(max_length=400, default='.',
        help_text=r'A string of the file naming format with important information replaced by the tags listed below. If the desired tag is not available, you may directly enter a variable as a regex group. {}'.format(tag_table()))
        
    timespan = models.FloatField(default=1,
        help_text=r'The length of time in days covered by each data file. If only a start or end date can be parsed from the file name, this will be used to determine what period of time each file represents. If both start and end times can be parsed from the naming scheme, this value will be ignored.')
        
    start = models.DateTimeField(null=True, blank=True,
        help_text=r'The datetime of the earliest datapoint in the stream.')
    
    end = models.DateTimeField(null=True, blank=True,
        help_text=r'The datetime of the latest datapoint in the stream.')
    
    """
    methods
    """
    def __unicode__(self):
        return self.name
        
    @property
    def filelist(self):
        """
        Assembles a list of all data files for this data stream.
        """
        if hasattr(self, 'ftpsource'):
            walk = os.walk(os.path.join(settings.STATIC_ROOT, 'data', self.ftpsource.client_directory))
        elif hasattr(self, 'mathematicasource'):
            walk = os.walk(os.path.join(settings.STATIC_ROOT, 'data', self.mathematicasource.client_directory))
        elif hasattr(self, 'pythonsource'):
            walk = os.walk(os.path.join(settings.STATIC_ROOT, 'data', self.pythonsource.client_directory))
        else:
            return []
            
        filelist = []
        for root, dirs, files in walk:
            for file in files:
                filelist.append(os.path.relpath(os.path.join(root, file), os.path.join(settings.STATIC_ROOT, 'data')))
        return filelist
        
    def filedate(self, filename):
        """
        Gets the start date and time for the given file.
        """
        vars = self.parse(os.path.split(filename)[1])
        if vars and 'startDatetime' in vars:
            return vars['startDatetime']
        else:
            return None
        
    @property
    def earliest(self):
        """
        Finds the earliest date of any of the available files.
        """
        if len(self.filelist) > 0 and self.filedate(self.filelist[0]):
            return min(map(self.filedate, self.filelist))
        else:
            return None
            
    @property
    def latest(self):
        """
        Finds the latest date and time of any of the available files.
        """
        if len(self.filelist) > 0 and self.filedate(self.filelist[0]):
            return max(map(self.filedate, self.filelist))
        else:
            return None
            
    def parse(self, filename):
        """
        Parses all available information from the given filename.
        """
        filename = os.path.split(filename)[1]
        try:
            fmt = self.naming_scheme
            temp = fmt
            for tag in tags:
                temp = temp.replace(tag.tag, tag.re)

            vars = re.search(temp, filename).groupdict()
            
            for tag in [tag for tag in tags if tag.tag in fmt]:
                vars = tag.relations(vars)
                
            if not 'startDatetime' in vars and 'endDatetime' in vars:
                startdatetime = vars['endDatetime'] - timedelta(self.timespan)
                
                vars['startDatetime'] = startdatetime
                vars['startDate'] = startdatetime.date()
                vars['startYear'] = startdatetime.strftime('%Y')
                vars['startMonth'] = startdatetime.strftime('%m')
                vars['startDay'] = startdatetime.strftime('%d')
                
                vars['startTime'] = startdatetime.time()
                vars['startHour'] = startdatetime.strftime('%H')
                vars['startMinute'] = startdatetime.strftime('%M')
                vars['startSecond'] = startdatetime.strftime('%S')
                
            elif 'startDatetime' in vars and not 'endDatetime' in vars:
                enddatetime = vars['startDatetime'] + timedelta(self.timespan)
                
                vars['endDatetime'] = enddatetime
                vars['endDate'] = enddatetime.date()
                vars['endYear'] = enddatetime.strftime('%Y')
                vars['endMonth'] = enddatetime.strftime('%m')
                vars['endDay'] = enddatetime.strftime('%d')
                
                vars['endTime'] = enddatetime.time()
                vars['endHour'] = enddatetime.strftime('%H')
                vars['endMinute'] = enddatetime.strftime('%M')
                vars['endSecond'] = enddatetime.strftime('%S')
                
            return vars
        except:
            Log.error('analysis.models.DataStream.parse', """
                An error occurred while attempting to parse filename {} using naming convention {}
                Check that the naming convention for this data stream has not been changed at the source.
            """.format(filename, self.naming_scheme))
            
        
        
        
    @property
    def js(self):
        """
        Returns the code of a javascript object with the attributes of this data stream.
        """
        response = {
            'name':str(self.name), 
            'organization':str(self.organization), 
            'description':str(self.description),
            'datasets':str(self.datasets),
            'tags':str(self.tags), 
            'files':str(len(self.filelist))
        }
        
        # Too slow for use in GUI 
        
        if self.start:
            response['earliest']=self.start.strftime('%m/%d/%Y')
        if self.end:
            response['latest']=self.end.strftime('%m/%d/%Y')
        
        return str(response)
        
    def get_datasets(self, filename=None):
        """
        Reads the file to get a list of contained datasets if possible.
        """
        try:
            filename = filename or os.path.join(settings.STATIC_ROOT, 'data', self.filelist[0])
            file = h5py.File(filename)
        except:
            return []
            
        groups = file.values()
        datasets = []

        while len(groups)>0:
            item = groups.pop()
            if isinstance(item, h5py.Dataset):
                data = {
                    'name': item.name,
                    'shape': file[item.name].shape
                    }
                data.update(dict(file[item.name].attrs.items()))
                datasets.append(data)
            else:
                for subitem in item.values():
                    groups.append(subitem)

        return datasets
        
    def update_datetimes(self):
        """
        Find and save the most recent datetime range for this data.
        """
        self.start = self.earliest
        self.end = self.latest
        self.save()

        
class DataFile():
    """
    This class represents an individual data file. It provides a more convenient syntax for accessing the properties of a file than is available through its DataStream, especially if one file is to be accessed repeatedly.
    
    This is not currently in use.
    """
    
    """
    Methods
    """
    def __init__(self, datastream, filename):
        self.datastream = datastream
        self.filename = filename
        self.path = os.path.join(settings.STATIC_ROOT, 'data', self.datastream.filelist[0], self.filename)
        
        for key, val in datastream.parse(filename).iteritems():
            setattr(self, key, val)
    
    @property
    def ext(self):
        return os.path.splitext(self.filename)[1]
    
    
class FTPSource(models.Model):
    """
    This class represents a data source accessed through FTP
    """
    
    """
    Fields
    """
    name = models.CharField(max_length=200, null=True,
        help_text=r'A useful description')
        
    data_stream = models.OneToOneField(DataStream, null=True, blank=True,
        help_text=r'The metadata associated with this FTP source')
    
    host = models.CharField(max_length=200,
        help_text=r'The static address of the FTP server')
        
    host_directory = models.CharField(max_length=400,
        help_text=r'Python code which, when evaluated, yeilds a callable which takes no arguments and returns the filepath or the desired directory. You may use any of the functions from the Python datetime library. e.g., lambda: "/sm/706/ByDate/V07/{}".format((date.today()-timedelta(2)).strftime("%Y/%m/%d"))')
    
    file_test = models.CharField(max_length=400,
        help_text=r'Python code which, when evaluated, yeilds a callable which takes a filename as an arguments and returns the a boolean representing whether the file should be fetched. You may use any of the functions from the Python datetime library. e.g., lambda name: name.startswith("2B31")')
    
    client_directory = models.CharField(max_length=400,
        help_text=r'The static parent directory where the files should be saved.')
    
    client_subdirectory = models.CharField(max_length=400, default='lambda: ""',
        help_text=r'Like host_directory but should return the filepath of the subdirectory where the files should be saved. Have this return an empty string if you want all files saved directly to the client directory.')
        
    user = models.CharField(max_length=100, default='anonymous',
        help_text=r'The username to use when logging into the FTP server.')
        
    password = models.CharField(max_length=100, default='', blank=True,
        help_text=r'The password to use when logging into the FTP server.')
        
    overwrite = models.BooleanField(default=True,
        help_text=r'If true, duplicate files will be overwritten every time data is fetched. If false, files with the same filenames as an existing file in the client directory will be ignored')
        
    """
    methods
    """
    def __unicode__(self):
        return self.name
    
    @shared_task
    def fetch_data_ftp(self):
        from ftplib import FTP
        import os

        host_directory = eval(self.host_directory)
        test = eval(self.file_test)
        client_subdirectory = eval(self.client_subdirectory)
        target =os.path.join(settings.STATIC_ROOT, 'data', self.client_directory, client_subdirectory())

        ftp = FTP(host=self.host)
        ftp.login(user=self.user, passwd=self.password)
        try:
            ftp.cwd(host_directory())
        except ftp_lib.error_perm as e:
            if e.errno == 550:
                Log.error('atmospherics.data.models.FTPSource.fetch_data_ftp', """
                    An error occurred while accessing the directory {} on {}.
                    
                    Try checking the host server to ensure that their naming and filing scheme has not changed.
                    
                    The code used to generate this directory: {}
                """.format( host_directory(), self.host, self.host_directory ))
            else:
                raise
            

        data = []
        for datafile in ftp.nlst():
            if test(datafile):
                if os.path.exists(os.path.join(target, datafile)) and self.overwrite == False:
                    pass
                else:
                    data.append(datafile)

        
        if not os.path.exists(target): 
            try: 
                os.makedirs(target)
            except OSError, e:
                if e.errno !=17:
                    raise
                pass
        
        for datafile in data:
            file = open(os.path.join(target, datafile), 'wb')
            ftp.retrbinary('RETR {}'.format(datafile), file.write)
            file.close()
            
        ftp.quit()
        
        
class MathematicaSource(models.Model):
    """
    This class represents a data source calculated from existing data through a Mathematica script
    """
    
    """
    Fields
    """
    name = models.CharField(max_length=200, null=True,
        help_text=r'A useful description')
        
    data_stream = models.OneToOneField(DataStream, null=True, blank=True,
        help_text=r'The metadata associated with this Mathematica Source')
        
    mathematica_script = models.TextField(
        help_text=r'')
        
    client_directory = models.CharField(max_length=400,
        help_text=r'The static parent directory where the files should be saved')
        
    client_subdirectory = models.CharField(max_length=400, default='lambda: ""',
        help_text=r'Python code which, when evaluated, yeilds a callable which takes no arguments and returns the filepath of the desired directory. You may use any of the functions from the Python datetime library. e.g., lambda: "/sm/706/ByDate/V07/{}".format((date.today()-timedelta(2)).strftime("%Y/%m/%d"))')
        
    overwrite = models.BooleanField(default=True,
        help_text=r'If true, duplicate files will be overwritten every time data is fetched. If false, files with the same filenames as an existing file in the client directory will be ignored')
        
    """
    Methods
    """
    def __unicode__(self):
        return self.name
        
    def replace_exports(self, tempdir):
        code = self.mathematica_script
        
        regex = r'Export\[+\s*(?P<file>.+?)\s*,'
        
        code = re.sub(regex, 'Export["{}/"<>\g<file>, '.format(tempdir), code)
        matches = re.findall(regex, code)
                        
        return code, matches
        
    @shared_task
    def fetch_data_math(self):
        ssh=pysftp.Connection(settings.SSH_HOST, username=settings.SSH_USER, password=settings.SSH_PASSWORD)
        
        temp = ssh.execute('mktemp -d')[0].rstrip('\n')
        ssh.chdir(temp)
        
        code, matches = self.replace_exports(temp)
        
        Log.debug('atmospherics.data.models.MathematicaSource.fetch_data', code)
        code = code.replace("'", '\'"\'"\'')
        command = "echo '{}' > {}/package.m".format(code, temp)
        ssh.execute(command)

        ret = ssh.execute('xvfb-run -s "-screen 0 640x480x24" math -script {}/package.m &\n\n\n\n'.format(temp))
        
        if ret:
            message = 'A message was returned by mathematica script  {}.m:\n{}'.format(self.name, ret[-100:])
            Log.info('atmospherics.data.models.MathematicaSource.fetch_data', message)

        ssh.execute('rm {}'.format(os.path.join(temp, 'package.m')))
        
        client_subdirectory = eval(self.client_subdirectory)
        target =os.path.join(settings.STATIC_ROOT, 'data', self.client_directory, client_subdirectory())
        if not os.path.exists(target):
            os.makedirs(target)
        ssh.get_d(temp, target)
        
        #ssh.execute('rm -rf {}'.format(temp))
        ssh.execute('disown')
        ssh.close()

        message = 'MathematicaSource {} run.\nOutput saved to:\nhttp://atmospherics.lossofgenerality.com/{}'.format(self.name, target)
        Log.info('atmospherics.data.models.MathematicaSource.fetch_data', message)
        
        
class PythonSource(models.Model):
    """
    This class represents a data source calculated from existing data through a Python script
    """
    
    """
    Fields
    """
    name = models.CharField(max_length=200, null=True,
        help_text=r'A useful description')
        
    data_stream = models.OneToOneField(DataStream, null=True, blank=True,
        help_text=r'The metadata associated with this Mathematica Source')
        
    python_script = models.TextField(
        help_text=r'')
        
    client_directory = models.CharField(max_length=400,
        help_text=r'The static parent directory where the files should be saved')
        
    client_subdirectory = models.CharField(max_length=400, default='lambda: ""',
        help_text=r'Python code which, when evaluated, yeilds a callable which takes no arguments and returns the filepath of the desired directory. You may use any of the functions from the Python datetime library. e.g., lambda: "/sm/706/ByDate/V07/{}".format((date.today()-timedelta(2)).strftime("%Y/%m/%d"))')
        
    overwrite = models.BooleanField(default=True,
        help_text=r'If true, duplicate files will be overwritten every time data is fetched. If false, files with the same filenames as an existing file in the client directory will be ignored')
        
    """
    Methods
    """
    def __unicode__(self):
        return self.name
        
    @shared_task
    def fetch_data_py(self):
        code = self.code.replace("'", '\'"\'"\'')
        code = code.replace("\\", "\\\\")
        exec(code)


#Copyright 2014-present lossofgenerality.com