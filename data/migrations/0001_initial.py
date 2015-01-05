# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FTPSource'
        db.create_table(u'data_ftpsource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('host_directory', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('file_test', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('client_directory', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('user', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
            ('password', self.gf('django.db.models.fields.CharField')(default='', max_length=100)),
        ))
        db.send_create_signal(u'data', ['FTPSource'])


    def backwards(self, orm):
        # Deleting model 'FTPSource'
        db.delete_table(u'data_ftpsource')


    models = {
        u'data.ftpsource': {
            'Meta': {'object_name': 'FTPSource'},
            'client_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'file_test': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'host_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'user': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'})
        }
    }

    complete_apps = ['data']


#Copyright 2014-present lossofgenerality.com
#License: http://www.gnu.org/licenses/old-licenses/gpl-2.0.html