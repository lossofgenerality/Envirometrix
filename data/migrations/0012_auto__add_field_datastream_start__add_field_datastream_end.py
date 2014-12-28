# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'DataStream.start'
        db.add_column(u'data_datastream', 'start',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'DataStream.end'
        db.add_column(u'data_datastream', 'end',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'DataStream.start'
        db.delete_column(u'data_datastream', 'start')

        # Deleting field 'DataStream.end'
        db.delete_column(u'data_datastream', 'end')


    models = {
        u'data.datastream': {
            'Meta': {'object_name': 'DataStream'},
            'datasets': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'naming_scheme': ('django.db.models.fields.CharField', [], {'default': "'*'", 'max_length': '400'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'timespan': ('django.db.models.fields.FloatField', [], {'default': '1'})
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
        },
        u'data.mathematicasource': {
            'Meta': {'object_name': 'MathematicaSource'},
            'client_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'client_subdirectory': ('django.db.models.fields.CharField', [], {'default': '\'lambda: ""\'', 'max_length': '400'}),
            'data_stream': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.DataStream']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mathematica_script': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'overwrite': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'data.pythonsource': {
            'Meta': {'object_name': 'PythonSource'},
            'client_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'client_subdirectory': ('django.db.models.fields.CharField', [], {'default': '\'lambda: ""\'', 'max_length': '400'}),
            'data_stream': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.DataStream']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'overwrite': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'python_script': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['data']