from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth, messages
from sms.models import *
import logging
import traceback
from django_twilio.decorators import twilio_view
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.forms.models import inlineformset_factory

@twilio_view
def inbound(request):
	try:
		i = Interaction(request.REQUEST.get('From', ''), request.REQUEST.get('To', ''), request.REQUEST.get('Body', ''))
		return i.process()
	except:
		logging.warn('captured error at main level: %s', traceback.format_exc())
		return

def login(request):
    context = {}
    populateContext(request, context)
    if context['authenticated'] == True:
        return HttpResponseRedirect('/dashboard/')
    if request.method == 'POST':
        try:
            context['username'] = request.POST['inputUsername']
            password = request.POST['inputPassword']
            user = auth.authenticate(username=context['username'], password=password)
            if user is not None:
                auth.login(request, user)
                return HttpResponseRedirect('/dashboard/')
            else:
                context['error'] = 'Username and/or Password are invalid.'
        except:
            context['error'] = 'Username and/or Password are invalid.'
    return render(request,
        'login.html', 
        context)

def register(request):
    context = {}
    populateContext(request, context)
    if request.method == 'POST':
        context['user_form'] = UserForm(data=request.POST)
        context['info_form'] = UserInfoForm(data=request.POST)

        if context['user_form'].is_valid() and context['info_form'].is_valid():
            user = context['user_form'].save()
            user.set_password(user.password)
            user.save()

            info = context['info_form'].save(commit=False)
            info.user = user
            info.save()
            ## create phoneNumbers from twi account
            tw = TwiAuth(user = info)
            tw.getNumbers()
            return HttpResponseRedirect('/login/')
        else:
            print context['user_form'].errors, context['info_form'].errors
    else:
        context['user_form'] = UserForm()
        context['info_form'] = UserInfoForm()
    return render(request, 
            'signup.html',
            context)     

def home(request):
    context = {}
    populateContext(request, context)
    return render(request,
        'index.html',
        context)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def dashboard(request):
    context = {}
    populateContext(request,context)
    return render_to_response('dashboard.html', context)

@login_required
def stats(request):
    context = {}
    populateContext(request,context)
    context['statsList'] = []
    for s in context['user'].getSurveys():
        context['statsList'].append(s.getStats())
    return render_to_response('stat.html', context)

@login_required
def surveys(request, id=False):
    context = {}
    populateContext(request, context)
    if request.method == 'GET' and id:
        try:
            context['survey'] = Survey.getById(id, request.user)
            return render_to_response('survey.html', context)
        except:
            return HttpResponseRedirect('/surveys/')
    else:
        context['surveys'] = request.user.info.getSurveys()
        return render_to_response('surveys.html', context)

@login_required
def questions(request, id, qid):
    context = {}
    populateContext(request, context)
    context['survey'] = Survey.getById(id, request.user)
    context['question'] = context['survey'].getQuestionById(qid)
    if request.method == "POST":
        context['form'] = OptionForm(data=request.POST)
        if context['form'].is_valid():
            option = context['form'].save(commit=False)
            option.question = context['question']
            option.save()
            return HttpResponseRedirect('/surveys/{0}/questions/{1}/'.format(context['survey'].id, context['question'].id))
        else:
            print context['form'].errors
    else: 
        context['form'] = OptionForm(initial={'question':context['question'].id})
    return render(request,
        'question.html',
        context)

@login_required
def newquestion(request, id):
    context = {}
    populateContext(request, context)
    survey = "";
    try:
        survey = Survey.getById(id, request.user)
        context['id'] = survey.id
    except: #TODO: get specific kind of exception
        return HttpResponseRedirect('/surveys/')
    if request.method == 'POST':
        context['form'] = QuestionForm(data=request.POST)
        if context['form'].is_valid():
            question = context['form'].save(commit=False)
            order = survey.getQuestionsCount() + 1
            question.order = order
            question.survey = survey
            question.save()
            return HttpResponseRedirect('/surveys/%s/' % context['id'])
        else:
            print context['form'].errors
    else:
        context['form'] = QuestionForm(initial={'survey':context['id']})

    return render(request, 
        'createquestion.html',
        context) 

@login_required
def newsurvey(request, extra=False):
    context = {}
    populateContext(request, context)
    if request.method == 'POST':
        context['form'] = SurveyForm(data=request.POST)
        if context['form'].is_valid():
            context['form'].save()
            return HttpResponseRedirect('/surveys/')
        else:
            print context['form'].errors
    else:
        context['form'] = SurveyForm()
    
    return render(request, 
        'createsurvey.html',
        context)

@login_required
def deletesurvey(request, id):
    try:
        survey = Survey.getById(id, request.user)
        survey.remove()
    except:
        print traceback.format_exc()
    return HttpResponseRedirect('/surveys/')

@login_required
def deletequestion(request, id, qid):
    try:
        survey = Survey.getById(id, request.user)
        question = survey.getQuestionById(qid)
        question.remove()
    except:
        print traceback.format_exc()
    return HttpResponseRedirect('/surveys/{0}/'.format(id))

@login_required
def deleteoption(request, id, qid, oid):
    try:
        survey = Survey.getById(id, request.user)
        question = survey.getQuestionById(qid)
        option = question.getOptionById(oid)
        option.remove()
    except:
        print traceback.format_exc()
    return HttpResponseRedirect('/surveys/{0}/questions/{1}/'.format(id, qid))

def populateContext(request, context):
    context['authenticated'] = request.user.is_authenticated()
    if context['authenticated'] == True:
        context['user'] = request.user.info