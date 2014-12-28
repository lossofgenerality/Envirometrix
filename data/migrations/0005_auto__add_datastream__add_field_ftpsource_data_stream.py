# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataStream'
        db.create_table(u'data_datastream', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('organization', self.gf('django.db.models.fields.CharField')(max_length=200, null=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'data', ['DataStream'])

        # Adding field 'FTPSource.data_stream'
        db.add_column(u'data_ftpsource', 'data_stream',
                      self.gf('django.db.models.fields.related.OneToOneField')(to=orm['data.DataStream'], unique=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'DataStream'
        db.delete_table(u'data_datastream')

        # Deleting field 'FTPSource.data_stream'
        db.delete_column(u'data_ftpsource', 'data_stream_id')


    models = {
        u'data.datastream': {
            'Meta': {'object_name': 'DataStream'},
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'organization': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'})
        },
        u'data.ftpsource': {
            'Meta': {'object_name': 'FTPSource'},
            'client_directory': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'data_stream': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['data.DataStream']", 'unique': 'True', 'null': 'True'}),
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