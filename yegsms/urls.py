from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'yegsms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^login/', 'sms.views.login'),
    url(r'^logout/', 'sms.views.logout'),
	url(r'^sms/$', 'sms.views.inbound'),
	url(r'^register|signup/$', 'sms.views.register'),
	url(r'^dashboard/$', 'sms.views.dashboard'),
    url(r'^dashboard/statistics/$', 'sms.views.stats'),
	url(r'^surveys/$', 'sms.views.surveys'),
	url(r'^surveys/(?P<id>\d+)/$', 'sms.views.surveys'),
    url(r'^surveys/(?P<id>\d+)/remove/$', 'sms.views.deletesurvey'),
	url(r'^surveys/(create|add)/$', 'sms.views.newsurvey'),
    url(r'^surveys/(?P<id>\d+)/questions/(create|add)/$', 'sms.views.newquestion'),
    url(r'^surveys/(?P<id>\d+)/questions/(?P<qid>\d+)/$', 'sms.views.questions'),
    url(r'^surveys/(?P<id>\d+)/questions/(?P<qid>\d+)/remove/$', 'sms.views.deletequestion'),
    url(r'^surveys/(?P<id>\d+)/questions/(?P<qid>\d+)/options/(?P<oid>\d+)/remove/$', 'sms.views.deleteoption'),
)
