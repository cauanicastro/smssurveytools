from django.db import models
from django import forms
import logging
import traceback
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import TwilioRestClient
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError, MultipleObjectsReturned
from django.contrib.auth.models import User

class UserInfo(models.Model):
	user = models.OneToOneField(User, related_name="info")
	twilioSid = models.CharField(max_length=60, unique=True)
	twilioAuth = models.CharField(max_length=60, unique=True)

	def getSurveyNumber(self):
		try:
			return Survey.objects.filter(phoneNumber__user=self.user).count()
		except:
			return 0

	def getSurveys(self):
		try:
			return Survey.objects.filter(phoneNumber__user=self.user)
		except Survey.DoesNotExist:
			return []

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('first_name', 'last_name','email', 'username', 'password')

class UserInfoForm(forms.ModelForm):
	def clean(self):
		try:
			aux = User.objects.get(info__twilioSid=self.cleaned_data.get('twilioSid'), info__twilioAuth=self.cleaned_data.get('twilioAuth'))
			raise ValidationError("Twilio credentials already in use")
		except MultipleObjectsReturned:
			raise ValidationError("Twilio credentials already in use")
		except User.DoesNotExist:
			logging.warn('captured error at model: %s', traceback.format_exc())
			print(traceback.format_exc())
			try:
				if not TwiAuth.testCredentials(self.cleaned_data.get('twilioSid'), self.cleaned_data.get('twilioAuth')):
					raise ValidationError("Twilio credentials are invalid.")
				return self.cleaned_data
			except:
				raise ValidationError("Twilio credentials are invalid.")
	class Meta:
		model = UserInfo
		fields = ('twilioSid', 'twilioAuth')

class PhoneNumber(models.Model):
	number = models.CharField(max_length=12)
	description = models.CharField(max_length=100)
	user = models.ForeignKey(User, null=False, blank=False)

	@staticmethod
	def get(number):
		return PhoneNumber.objects.get(number=number)
	def __unicode__(self):
		return self.number

class Survey(models.Model):
	title = models.CharField(max_length=30)
	phoneNumber = models.ForeignKey(PhoneNumber)
	greeting = models.CharField(max_length=250)
	endMessage = models.CharField(max_length=250)
	active = models.BooleanField(default=True)
	dateCreated = models.DateTimeField(auto_now_add=True)
	dateModified = models.DateTimeField(auto_now=True)
	
	@staticmethod
	def getSurvey(number):
		try:
			return Survey.objects.get(phoneNumber__number=number) #change to get
		except:
			raise Exception("Error: Current number is not associated with any survey.")

	@staticmethod
	def getById(id, user):
		try:
			return Survey.objects.get(phoneNumber__user=user, id=id) #change to get
		except:
			raise Exception("Error: Survey does not exist.")

	def getNumber(self):
		return self.phoneNumber.number

	def getQuestionsCount(self):
		try:
			return Question.objects.filter(survey=self).count()
		except:
			return 0
			
	def addQuestion(self, type, content):
		order = self.getQuestionsCount() + 1
		q = Question(survey=self, type=type, content=content, order=order)
		q.save()
		return q

	def getQuestionById(self, id):
		return Question.objects.get(survey=self, id=id)
	
	def getAllQuestions(self):
		try:
			return Question.objects.filter(survey=self).order_by('order')
		except:
			return []
		
	def getCompletedTimesCount(self):
		return SurveyCitizenAnswer.objects.filter(surveyCitizen__survey=self).count()

	def getTotalVotesCount(self):
		return SurveyCitizen.objects.filter(survey=self, finished=True).count()
	
	def getCompletedTimesUniqueCount(self):
		return SurveyCitizen.objects.filter(survey=self, finished=True).distinct('citizen').count()
	
	def getQuickStats(self):
		text = ''
		text += 'This survey have %s questions, and was completed %s times by %s different people. ' % (self.getQuestionsCount(), self.getCompletedTimesCount(), self.getCompletedTimesUniqueCount())
		count = 0
		for q in self.getAllQuestions():
			count += 1
			qReplies = q.getRepliesCount()
			aux = 'Question %s: received %s replies. ' % (count, qReplies)
			if not q.isOpenQuestion():
				count2 = 0
				for o in q.getOptionsList():
					percent = ((float(o.getRepliesCount()) / qReplies) * 100)
					aux += 'Option %s, received %s votes (%s p). ' % (o.command, o.getRepliesCount(), "{0:.2f}".format(percent))
			text += aux
		return text

	def getStats(self):
		stats = {}
		stats['questionsCount'] = self.getQuestionsCount()
		stats['votes'] = self.getTotalVotesCount()
		stats['completedTimes'] = self.getCompletedTimesCount()
		stats['completedPeople'] = self.getCompletedTimesUniqueCount()
		stats['questions'] = []
		for q in self.getAllQuestions():
			question = {}
			question["obj"] = q
			question["repliesCount"] = q.getRepliesCount()
			if not q.isOpenQuestion():
				question["replies"] = []
				for o in q.getOptionsList():
					option = {}
					option["obj"] = o
					option["votes"] = o.getRepliesCount()
					percent = ((float(option["votes"]) / question["repliesCount"]) * 100)
					option["votesPercent"] = "{0:.2f}%".format(percent)
					question["replies"].append(option)
			else:
				question["openAnswers"] = []
				for a in SurveyCitizenAnswer.objects.filter(surveyCitizen__survey=self, question=q):
					answer = {}
					answer['content'] = a.answer
					answer['date'] = a.dateCreated
					question["openAnswers"].append(answer)
			stats['questions'].append(question)
		return stats

	def getUser(self):
		return UserInfo.objects.get(user = self.phoneNumber.user)

	def remove(self):
		self.delete()
		return True

	def __unicode__(self):
		return self.title

class SurveyForm(forms.ModelForm):
	def clean_phoneNumber(self):
		try:
			aux = Survey.objects.get(phoneNumber=self.cleaned_data['phoneNumber'])
			raise ValidationError("This phone number is already in use.")
		except MultipleObjectsReturned:
			raise ValidationError("This phone number is already in use.")
		except Survey.DoesNotExist:
			return self.cleaned_data['phoneNumber']

	class Meta:
		model = Survey
		exclude = ('dateCreated', 'dateModified', 'greeting')

class Question(models.Model):
	OPEN = 'OP'
	MULTIPLE = 'MU'
	TYPE_CHOICES = (
		(OPEN, 'Open question'),
		(MULTIPLE, 'Multiple-choice question'),
	)	
	survey = models.ForeignKey(Survey)
	content = models.CharField(max_length=250)
	order = models.IntegerField()
	type = models.CharField(max_length=2,choices=TYPE_CHOICES,default=MULTIPLE)
	dateCreated = models.DateTimeField(auto_now_add=True)
	dateModified = models.DateTimeField(auto_now=True)

	def getRepliesCount(self):
		return SurveyCitizenAnswer.objects.filter(surveyCitizen__survey=self.survey, question=self).count()
	
	def getOptionsList(self):
		return Option.objects.filter(question=self)

	def isValid(self):
		if self.isOpenQuestion():
			return True
		else:
			try:
				return Option.objects.filter(question=self).count() > 1
			except:
				return False
		
	def getOptionsText(self):
		try:
			options = ', '.join(o.command for o in self.getOptionsList())
			return 'Available options: ' + options
		except:
			return ''

	def remove(self):
		try:
			for obj in Question.objects.filter(order__gt=self.order):
				obj.order = obj.order - 1
				obj.save()
		except Question.DoesNotExist:
			pass
		self.delete()
		return True

	def addOption(self, description, command):
		if self.type == OPEN:
			raise Exception("Error: Cannot add options to open questions!")
		opt = Option(question=self, description=description, command=command)
		opt.save()
		return opt

	def isLast(self):
		return self.survey.getQuestionsCount() == self.order
	
	def isOpenQuestion(self):
		return self.type == self.OPEN

	def isValidOption(self, option):
		if self.isOpenQuestion():
			return True
		for obj in self.getOptionsList():
			if obj.command.lower().strip() == option.lower().strip():
				return True
		return False
	
	def getOption(self, text):
		return Option.objects.get(question=self, command__iexact=text)

	def getOptionById(self, id):
		return Option.objects.get(question=self, id=id)

	def __unicode__(self):
		return self.content

class QuestionForm(forms.ModelForm):
	survey = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	class Meta:
		model = Question
		fields = ('content', 'type')

class Option(models.Model):
	question = models.ForeignKey(Question)
	description = models.CharField(max_length=250)
	command = models.CharField(max_length=20)
	dateCreated = models.DateTimeField(auto_now_add=True)
	dateModified = models.DateTimeField(auto_now=True)

	def getRepliesCount(self):
		return SurveyCitizenAnswer.objects.filter(surveyCitizen__survey=self.question.survey, question=self.question, option = self).count()
	
	def remove(self):
		self.delete()

	def __unicode__(self):
		return self.command

class OptionForm(forms.ModelForm):
	question = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
	class Meta:
		model = Option
		fields = ('description', 'command')

class Citizen(models.Model):
	phoneNumber = models.CharField(max_length=12)
	active = models.BooleanField(default=True)
	dateModified = models.DateTimeField(auto_now=True)
	#Returns citizen by his/her phone number. If don't exist, create a new one.

	@staticmethod
	def getCitizen(number):
		try:
			return Citizen.objects.get(phoneNumber=number)
		except:
			c = Citizen(phoneNumber=number)
			c.save()
			return c

	def __unicode__(self):
		return self.phoneNumber

class SurveyCitizen(models.Model):
	survey = models.ForeignKey(Survey)
	citizen = models.ForeignKey(Citizen)
	finished = models.BooleanField(default=False)

	@staticmethod
	def getOpenSurvey(calledNumber,callerNumber):
		survey = Survey.getSurvey(calledNumber)
		citizen = Citizen.getCitizen(callerNumber)
		try:
			return SurveyCitizen.objects.get(survey=survey, citizen=citizen, finished=False)
		except:
			s = SurveyCitizen(survey=survey, citizen=citizen)
			s.save()
			return s
	
	def recordAnswer(self, question, answer, skip=False):
		sca = ''
		if skip:
			sca = SurveyCitizenAnswer(surveyCitizen=self, question=question, answer='')
		elif question.isOpenQuestion():
			sca = SurveyCitizenAnswer(surveyCitizen=self, question=question, answer=answer)
		else:
			if not answer:
				raise Exception("Error: A multiple-choice question requires an option!") #create specific exception object
			if not question.isValidOption(answer):
				raise Exception("Error: Invalid option") #create specific exception object
			sca = SurveyCitizenAnswer(surveyCitizen=self, question=question, option=question.getOption(answer))
		sca.save()
		return sca
	
	def isFirstQuestion(self):
		return len(self.getAnswers()) == 0
			
	def getAnswers(self):
		try:
			return SurveyCitizenAnswer.objects.filter(surveyCitizen_id=self.id)
		except:
			return []
			
	def getNextQuestion(self):		
		try:
			aux = SurveyCitizenAnswer.objects.filter(surveyCitizen=self)
			aux = aux.order_by('-dateCreated')[0]
			return Question.objects.get(survey=self.survey, order=aux.question.order + 1)
		except: # catch only this one: Entry.DoesNotExist
			try:
				return Question.objects.get(survey=self.survey, order=1)
			except:
				raise Exception("Error: Current survey have no question(s) associated with.") #make custom exception

class SurveyCitizenAnswer(models.Model):
	surveyCitizen = models.ForeignKey(SurveyCitizen)
	question = models.ForeignKey(Question)
	option = models.ForeignKey(Option, blank=True, null=True)
	answer = models.CharField(max_length=250)
	dateCreated = models.DateTimeField(auto_now_add=True)

class TwiAuth:
	def __init__(self, survey = None, user = None):
		if not user and not survey:
			raise Exception('Either user or survey is required')
		if user:
			self.user = user
		elif survey:
			self.user = survey.getUser()
		self.client = TwilioRestClient(self.user.twilioSid, self.user.twilioAuth)

	def getNumbers(self):
		lst = []
		for n in self.client.phone_numbers.list():
			try:
				lst.append(PhoneNumber.get(n.phone_number))
			except: #exception to catch: phone not found
				p = PhoneNumber(user = self.user.user, number = n.phone_number, description = '')
				p.save()
				lst.append(p)
		return lst

	@staticmethod
	def testCredentials(sid, auth):
		try:
			client = TwilioRestClient(sid, auth)
			client.accounts.get(sid)
			return True
		except:
			return False

	@csrf_exempt
	def sendMessage(self, receiver, sender, message):
		self.client.sms.messages.create(to=receiver, from_=sender, body=message)
		return True

class Interaction:
	question = ''
	def __init__(self, sender, receiver, command):
		try:
			self.obj = SurveyCitizen.getOpenSurvey(receiver, sender)
		except: #catch specifically no survey kind of exception
			raise Exception("Error getting interaction")
		self.command = command
		self.twilioclient = TwiAuth(survey = self.obj.survey)

	def sendMessage(self, message):
		return self.twilioclient.sendMessage(self.obj.citizen.phoneNumber, self.obj.survey.getNumber(), message)

	def processCommands(self):
		if (self.command.lower().strip() == 'stats'):
			statusstr = self.obj.survey.getQuickStats()
			n = 120
			for i in range(0, len(statusstr), n):
				self.sendMessage(statusstr[i:i+n])
			return True
		return False

	def finishSurvey(self):
		self.obj.finished = True
		self.obj.save()
		self.sendMessage(self.obj.survey.endMessage)
		return True

	def process(self):
		### check if command is special command, check whether command is valid, check whether question is last ###
		if not self.processCommands():
			try:
				self.question = self.obj.getNextQuestion()
			except:
				self.sendMessage("Thank you for your message, the survey is currently innactive, please try again later!")
				return True
			if not self.question.isValidOption(self.command):
				self.sendMessage(self.question.content)
				if not self.question.isOpenQuestion():
					self.sendMessage(self.question.getOptionsText())
				return True
			self.obj.recordAnswer(self.question, self.command)
			if self.question.isLast():
				return self.finishSurvey()
			self.question = self.obj.getNextQuestion()
			while not self.question.isValid():
				if self.question.isLast():
					return self.finishSurvey()
				self.obj.recordAnswer(self.question, '', skip=True)
				self.question = self.obj.getNextQuestion()
			self.sendMessage(self.question.content)
			if not self.question.isOpenQuestion():
				self.sendMessage(self.question.getOptionsText())
			return True
		return True