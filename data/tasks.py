from __future__ import absolute_import
from logger.utils import shared_task

@shared_task
def fetch_FTP():
    from .models import FTPSource
    
    for source in FTPSource.objects.all():
        source.fetch_data_ftp()
        source.data_stream.update_datetimes()
        
        
@shared_task
def fetch_Math():
    from .models import MathematicaSource
    
    for source in MathematicaSource.objects.all():
        source.fetch_data_math()


#Copyright 2014-present lossofgenerality.com