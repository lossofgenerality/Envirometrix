# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DataStream.datasets'
        db.add_column(u'data_datastream', 'datasets',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


        # Changing field 'DataStream.naming_scheme'
        db.alter_column(u'data_datastream', 'naming_scheme', self.gf('django.db.models.fields.CharField')(max_length=400))

    def backwards(self, orm):
        # Deleting field 'DataStream.datasets'
        db.delete_column(u'data_datastream', 'datasets')


        # Changing field 'DataStream.naming_scheme'
        db.alter_column(u'data_datastream', 'naming_scheme', self.gf('django.db.models.fields.CharField')(max_length=400, null=True))

    models = {
        u'data.datastream': {
            'Meta': {'object_name': 'DataStream'},
            'datasets': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'naming_scheme': ('django.db.models.fields.CharField', [], {'default': "'def naming_scheme(filename)'", 'max_length': '400'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'data.ftpsource': {
            'Meta': {'object_name': 'FTPSource'},
            'client_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'client_subdirectory': ('django.db.models.fields.CharField', [], {'default': '\'lambda: ""\'', 'max_length': '400'}),
            'data_stream': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.DataStream']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'file_test': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'host_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'overwrite': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'default': "'anonymous'", 'max_length': '100'})
        }
    }

    complete_apps = ['data']


#Copyright 2014-present lossofgenerality.com