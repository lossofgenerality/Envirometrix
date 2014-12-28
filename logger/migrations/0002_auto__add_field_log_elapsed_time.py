# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Log.elapsed_time'
        db.add_column(u'logger_log', 'elapsed_time',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=30, decimal_places=10, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Log.elapsed_time'
        db.delete_column(u'logger_log', 'elapsed_time')


    models = {
        u'logger.log': {
            'Meta': {'object_name': 'Log'},
            'elapsed_time': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '30', 'decimal_places': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'info'", 'max_length': '20'}),
            'subsystem': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'time_stamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'})
        }
    }

    complete_apps = ['logger']