# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Citizen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phoneNumber', models.CharField(max_length=12)),
                ('active', models.BooleanField(default=True)),
                ('dateModified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=250)),
                ('command', models.CharField(max_length=20)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateModified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhoneNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=12)),
                ('description', models.CharField(max_length=100)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=250)),
                ('order', models.IntegerField()),
                ('type', models.CharField(default=b'MU', max_length=2, choices=[(b'OP', b'Open question'), (b'MU', b'Multiple-choice question')])),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateModified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=30)),
                ('greeting', models.CharField(max_length=250)),
                ('endMessage', models.CharField(max_length=250)),
                ('active', models.BooleanField(default=True)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('dateModified', models.DateTimeField(auto_now=True)),
                ('phoneNumber', models.ForeignKey(to='sms.PhoneNumber')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyCitizen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('finished', models.BooleanField(default=False)),
                ('citizen', models.ForeignKey(to='sms.Citizen')),
                ('survey', models.ForeignKey(to='sms.Survey')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SurveyCitizenAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('answer', models.CharField(max_length=250)),
                ('dateCreated', models.DateTimeField(auto_now_add=True)),
                ('option', models.ForeignKey(blank=True, to='sms.Option', null=True)),
                ('question', models.ForeignKey(to='sms.Question')),
                ('surveyCitizen', models.ForeignKey(to='sms.SurveyCitizen')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('twilioSid', models.CharField(max_length=60)),
                ('twilioAuth', models.CharField(max_length=60)),
                ('user', models.OneToOneField(related_name='info', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(to='sms.Survey'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(to='sms.Question'),
            preserve_default=True,
        ),
    ]
