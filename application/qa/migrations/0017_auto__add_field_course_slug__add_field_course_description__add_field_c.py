# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Course.slug'
        db.add_column('qa_course', 'slug', self.gf('django.db.models.fields.CharField')(default='', max_length=50), keep_default=False)

        # Adding field 'Course.description'
        db.add_column('qa_course', 'description', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Course.default_level'
        db.add_column('qa_course', 'default_level', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Course.slug'
        db.delete_column('qa_course', 'slug')

        # Deleting field 'Course.description'
        db.delete_column('qa_course', 'description')

        # Deleting field 'Course.default_level'
        db.delete_column('qa_course', 'default_level')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'qa.answer': {
            'Meta': {'object_name': 'Answer'},
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['qa.Question']"}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'qa.course': {
            'Meta': {'object_name': 'Course'},
            'default_level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'qa.question': {
            'Meta': {'object_name': 'Question'},
            'answered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['qa.Course']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'questions'", 'symmetrical': 'False', 'to': "orm['qa.Tag']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'qa.role': {
            'Meta': {'object_name': 'Role'},
            'hut': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qa.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qa.UserProfile']"})
        },
        'qa.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'qa.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'bio': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'confirmation_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'students'", 'symmetrical': 'False', 'through': "orm['qa.Role']", 'to': "orm['qa.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_moderator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderator_courses': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'moderators'", 'symmetrical': 'False', 'to': "orm['qa.Course']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'qa.vote': {
            'Meta': {'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'score': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['qa']
