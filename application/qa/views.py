# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from django.shortcuts import get_object_or_404

# Models
from django.contrib.auth.models import User

print "Here... 1"

from qa.models import Tag, Question, Answer, Vote, UserProfile, Course, Role, Comment, State

print "Here... 2"

import re
from django.core.mail import send_mail, EmailMessage, send_mass_mail
from django.conf import settings

from qa.search import get_query
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import datetime


from django.utils import simplejson
def json_response(obj):
    """
    Helper method to turn a python object into json format and return an HttpResponse object.
    """
    return HttpResponse(simplejson.dumps(obj), mimetype="application/x-javascript")


models = {
    'A': Answer,
    'Q': Question
}

MESSAGES = {
    'moderation': 'Your question has been submitted for moderation, and if approved will be shown soon.',
    'email': 'You must enter in a properly formatted Stanford email address.',
    'fname': 'You must enter in a first name.',
    'lname': 'You must enter in a last name',
    'passwd': 'You must enter in a password',
    'class':  'You must select at least one class.',
    'amod': 'Your answer has been submitted for moderation, and if approved will be shown soon.',
    'act': 'Your account has been activated. Please log in with your email and password.',
    'inact': 'Your account could not be succesfully activated.',
    'waitforact': 'Thanks for creating an account. You should receive a confirmation email shortly which will activate your account.',
    'passwdmatch': 'Your passwords did not match. Please enter them again.',
    'notactive': 'Your account is not yet active.',
    'loginerror': 'There was an error loggin you in. Please check your password.',
    'perms': 'That page does not exist.',
    'exists': 'An account already exists with this email.',
    'noaccount': 'We could not find an account with that email address.'
}

## Permissions Method
def can_see_question(user, question):
    hut = question.course

    if user.is_anonymous():
        return question.course.public
        
    up = user.get_profile()
    return hut in up.courses.all()

@login_required
def huts(request):
    # Show a user all of their 'huts'
    all_huts = Course.objects.filter(public=True)
    user_huts = request.user.get_profile().courses.all()
    other_huts = set(all_huts) - set(user_huts)
    return render_to_response(
        "huts.html",
        {
            'huts': user_huts,
            'other': other_huts
        },
        context_instance = RequestContext(request)
    )
    
@login_required
def delete_question(request):
    qid = request.POST['qid']
    question = Question.objects.get(pk=qid)
    if not request.user.get_profile().is_moderator_for_hut(question.course):
        return json_response({"status": "fail"})
    
    question.delete()
    return json_response({"status":"ok"})
    
@login_required
def follow_question(request):
    qid = request.POST['qid']
    action = request.POST['action']
    question = Question.objects.get(pk=qid)
    if action == "unfollow":
        question.remove_follower(request.user)
    elif action == "follow":
        question.add_follower(request.user)
    
    return json_response({"status":"ok"})
    
@login_required
def subscribe_to_hut(request):
    hut_id = request.POST['hut_id']
    hut = Course.objects.get(pk=hut_id)
    action = request.POST['action']
    if action == "subscribe":
        hut.add_subscriber(request.user)
    elif action == "unsubscribe":
        hut.remove_subscriber(request.user)
    
    return json_response({"status": "ok"})
    
    
@login_required
def join_hut(request):
    hut_id = request.POST['hut']
    hut = Course.objects.get(pk=hut_id)    
    role = Role(hut=hut, profile=request.user.get_profile(), level=hut.default_level)
    role.save()
    return json_response({
        'status': 'ok'
    })

@login_required
def drop_hut(request):
    hut_id = request.POST['hut']
    hut = Course.objects.get(pk=hut_id)    
    role = Role.objects.get(hut=hut, profile=request.user.get_profile())
    role.delete()
    return json_response({
        'status': 'ok'
    })
    

@csrf_protect
@login_required  
def vote(request):
    votes = Vote.submit_vote(request)
    return json_response({
        "status": "ok",
        "votes": votes
    })

def verify_email(email):
    """
    Accept emails like 
        jkeeshin@stanford.edu and 
        jkeeshin@cs.stanford.edu
    
        NAME@(SUBDOMAIN.)?stanford.edu
    """
    if re.match("^.+\\@(.+\\.)?stanford\\.edu$", email) != None:
        return True
    return False
    

#
# Send an email to a list of users. The users will appear in the bcc field
# If we are testing locally, print a message instead of sending the email
#    
def send_email(subject, content, from_email, to_email):
    if not settings.LOCAL:
        msg = EmailMessage(subject=subject, body=content, from_email=from_email, bcc=to_email)
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()   
    else:
        print "Send Email Message (Local)" 
 
# Message all of the users who are subscribed to this hut
#
#   hut         the hut that users were subscribed to
#   question    the question that was just asked
#   actor       the user who asked the question, should not be notified if they are a subsriber
#   
def message_subscribers(hut, question, actor):
    subscribers = hut.get_subscribers().exclude(id=actor.id)
    subject = 'QuestionHut: New Question For %s: %s' % (hut.title, question.title)
    content = 'There is a new question for %s.\n\nCheck it out here %squestion/%d' % (hut.title, settings.BASE_URL, question.id)
    from_addr = 'Question Hut <jkeeshin@cs.stanford.edu>'
    to_bcc = [subscriber.email for subscriber in subscribers]
    send_email(subject, content, from_addr, to_bcc)
    
    

#
# Message all of the people who follow this question
#
#   question    the question that was just acted on
#   actor       the user who just acted, they should *not* receive a notification
#               about what just happened, because they did it
#   
def message_followers(question, actor):
    followers = question.get_followers()

    subject = 'QuestionHut: New Response on a Question: %s' % question.title
    email_content = """There is a new response on a question you follow.\n\nCheck out the question here %squestion/%d""" % (settings.BASE_URL, question.id)

    from_addr = 'Question Hut <jkeeshin@cs.stanford.edu>'
    
    mail_list = []
    for user in followers:
        if user != actor:
            cur_email = (subject, email_content, from_addr, [user.email])
            mail_list.append(cur_email)
            
    if mail_list:      
        data_tuple = tuple(mail_list)
        
        if not settings.LOCAL:
            send_mass_mail(data_tuple)
        else:
            print "Messaging question followers (local)"

def generate_code(user):
    import datetime, hashlib
    now = str(datetime.datetime.now())
    verify = "%s%s" % (user.email, now)
    code = hashlib.sha224(verify).hexdigest()
    
    up = user.get_profile()
    up.confirmation_code = code
    up.save()
    return code

## To email must be a list
def send_confirmation_email(user):
    code = generate_code(user)
    subject = 'Welcome to QuestionHut: Confirm Your Email Address'
    email_content = 'Thanks for signing up for Question Hut. Please confirm your email address by ' \
            'visititing the following link: <br/><br/> %sconfirm?u=%d&code=%s' % (settings.BASE_URL, user.id, code)
    send_email(subject, email_content, 'Question Hut <questionhut@gmail.com>', [user.email])

def confirm(request):
    uid = request.GET['u']
    code = request.GET['code']
    
    user = User.objects.get(pk=uid)
    msg = 'inact'
    if user.get_profile().confirmation_code == code:
        msg = 'act'
        user.is_active = True
        user.save()
    
    return redirect('/?msg=%s' % msg ) ## include message



	
@csrf_protect
def join(request):
    try:
        User.objects.get(email=request.POST['email'])
        return index(request, message='exists')
    except User.DoesNotExist:
        pass
        
    if len(request.POST['first_name']) == 0:
        return index(request, message='fname')
    if len(request.POST['last_name']) == 0:
        return index(request, message='lname')
    if len(request.POST['password']) == 0:
        return index(request, 'passwd')
        
    if request.POST['password'] != request.POST['password2']:
        return index(request, 'passwdmatch')
    
    if not verify_email(request.POST['email']):
        return index(request, 'email')
    
    user = User.objects.create_user(request.POST['email'], #email is username
                                    request.POST['email'], #email
                                    request.POST['password'])
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.is_active = False #comment in
    user.save()
    
    userprofile = UserProfile(user=user)
    userprofile.save()

    send_confirmation_email(user)  #comment in
    return redirect('/?msg=waitforact') #comment out
    
def authenticate(request, email, password):
    user = auth.authenticate(username=email, password=password)
    if user is not None:
        if not user.is_active:
            auth.logout(request)
            return redirect('/?msg=notactive')

        auth.login(request, user)
        return redirect('/')
    else:
        return redirect('/?msg=loginerror')
    
@csrf_protect
def login(request):
    exists = User.objects.filter(email=request.POST['email'])
    if len(exists) == 0:
        return redirect('/?msg=noaccount')
        
    return authenticate(request, request.POST['email'], request.POST['password'])
    
def logout(request):
    auth.logout(request)
    return redirect('/')
    
def error(request):
    return render_to_response(
        "error.html",
        {},
        context_instance = RequestContext(request)
    )
        
    
def sort_questions(query_set, sort):
    if sort == 'best':
        return query_set.order_by('-votes')[:60]
    elif sort == 'popular':
        return query_set.order_by('-views')[:60]
    else:
        return query_set.order_by('-last_updated')[:60]
        
        
def has_permission(user, huts):
    if not user.is_authenticated():
        return False
    
    up = user.get_profile()
    user_huts = up.courses.all()
    for hut in huts:
        if hut not in user_huts:
            return False
    return True

def get_questions(huts=[], tags=None, approved=True, status='all', user=None):
    """
    The method that gets a list of questions. We first make sure we have a user.
    Then we get all of the questions in the specified huts, and possibly filter
    by whether it is answered and what tags it has. If this call was invalid
    instead of returning a queryset, we return False to the caller.
    
    @author Jeremy Keeshin      October 13, 2011
    """
    if not user or not huts:
        return False
    
    if not has_permission(user=user, huts=huts):
        return False
        
    qs = Question.objects.filter(approved=approved, course__in=huts)
    
    if status == 'unanswered':
        qs = qs.annotate(num_answers=Count('answers')).filter(num_answers=0)

    if tags is not None:
        tag_list = tags.split(',')
        for tag in tag_list:
            try: 
                the_tag = Tag.objects.get(title=tag)
                qs = qs.filter(tags=the_tag)
            except Tag.DoesNotExist:
                pass

    return qs
    
def get_course(request):
    """
    Based on the get parameters of to the questions view, we decide what list
    of huts to give to the user. This method returns a list of huts as well as a descriptor
    in a tuple. If the user only is a member of one hut, we return that.
    
    @author Jeremy Keeshin      October 13, 2011
    """
    courses = request.user.get_profile().courses.all()
    
    if 'hut' in request.GET:
        hut_text = request.GET['hut']
    else:
        hut_text = 'all'

    if hut_text != 'all':
        hut = Course.objects.get(slug=hut_text)
        return [hut], hut_text

    if len(courses) == 1:
        return [courses[0]], courses[0].slug
    return courses, hut_text
    
def get_sort_method(request):
    return request.GET['sort'] if 'sort' in request.GET else 'recent'
    
def get_time_limit(request):
    return request.GET['time'] if 'time' in request.GET else 'quarter'
    
    
def time_period(query_set, time):
    import datetime
    
    now = datetime.datetime.now()
    if time == 'today':
        day = datetime.timedelta(days=1)
        return query_set.filter(created_at__gte=now-day)        
    if time == 'week':
        week = datetime.timedelta(days=7)
        return query_set.filter(created_at__gte=now-week)
    elif time == 'month':
        month = datetime.timedelta(weeks=4)
        return query_set.filter(created_at__gte=now-month)
    elif time == 'all':
        return query_set
    # elif time == 'quarter':
    else:
        return query_set.filter(tags__title=State.CURRENT_QUARTER)

    
@login_required  
def questions_display(request, message=None):
    sort = get_sort_method(request)
    time = get_time_limit(request)
    hut_list, hut = get_course(request)   
    if len(hut_list) == 0:
        return redirect('/huts')

    hut_obj = hut_list[0] if len(hut_list) == 1 else None
         
    tags = request.GET['tags'] if 'tags' in request.GET else None
    status = request.GET['status'] if 'status' in request.GET else 'all'
        
    query_set = get_questions(huts=hut_list, tags=tags, status=status, user=request.user)
    
    # Explicitly check for false, since empty list [] is okay
    if query_set == False:
        return redirect('/')

    query_set = time_period(query_set=query_set, time=time)    
    query_set = sort_questions(query_set=query_set, sort=sort)
    
    up = request.user.get_profile()
    last_visited = up.last_visited
    up.last_visit = datetime.now()
    up.save()
    
    return render_to_response(
        "index.html",
        {
            'user': request.user,
            'questions': query_set,
            'sort': sort,
            'hut': hut,
            'hut_obj': hut_obj,
            'time': time,
            'status': status,
            'courses': request.user.get_profile().courses.all(),
            'message': message,
            'last_visited': last_visited
        },
        context_instance = RequestContext(request)
    )
    
def index(request, message=None):
    if message != None:
        message = MESSAGES[message]  
    elif 'msg' in request.GET:
        the_msg = request.GET['msg']
        if the_msg in MESSAGES:
            message = MESSAGES[the_msg]
    
    if not request.user.is_authenticated():
        return render_to_response(
            "login.html",
            {
                'message': message,
                'previous': request.POST
            },
            context_instance = RequestContext(request)
        )
    else:
        #return redirect('/huts')
        return questions_display(request=request, message=message)

       
def question_view(request, id=None):
    if not id: 
        return redirect('/error')

    message = None
    if 'msg' in request.GET:
        the_msg = request.GET['msg']
        if the_msg in MESSAGES:
            message = MESSAGES[the_msg]
    
    
        
    question = get_object_or_404(Question, pk=id)
    
    if not can_see_question(user=request.user, question=question):
        return redirect('/?msg=perms')
        
    if request.user.is_authenticated():
        moderator = request.user.get_profile().is_moderator_for_hut(question.course)
    else:
        moderator = False
    
    question.views += 1
    question.save()
    return render_to_response(
        "question.html",
        {
            'user': request.user,
            'question': question,
            'message': message,
            'answers': question.answers.filter(approved=True).order_by('-votes'),
            'moderator': moderator
        },
        context_instance = RequestContext(request)
    )
    
@login_required
def submit_comment(request):
    content = request.POST['content']
    kind = request.POST['kind']
    obj_id = request.POST['obj_id']

    obj = Comment.get_parent(kind=kind, obj_id=obj_id)
    obj.update_timestamp()
    obj.add_follower(request.user)
    
    comment = Comment(author=request.user, content=content, kind=kind, obj_id=obj_id)
    comment.save()
    
    message_followers(question=comment.get_question(), actor=request.user)
    
    return redirect('/question/' + request.POST['redirect'])
    
    
    
@login_required  
def answer_question(request):
    if not request.user.is_authenticated():
        return redirect('/')
    else:
        q_id = request.POST['question']
        content = request.POST['answer']
        question = Question.objects.get(pk=q_id)
        question.update_timestamp()
        answer = Answer(author=request.user,
                        question=question,
                        content=content)
        answer.save()
        
        message_followers(question=question, actor=request.user)
        
        ## Add the user to the list of followers for this question
        question.add_follower(request.user)
                        
        if question.course.has_approved(request.user):
            answer.approved = True
            answer.save()
            return redirect('/question/%s' % q_id)
            
        
                        
        return redirect('/question/%s?msg=amod' % q_id)
    
    
@csrf_protect
@login_required  
def ask_question(request):
    if not request.user.is_authenticated():
        return redirect('/')
    else:
        hut_slug = request.POST['hut']
        hut = Course.objects.get(slug=hut_slug)
        
        title = request.POST['title']
        if len(title) == 0:
            return ask(request, error='You need to enter a title.', hut_slug=hut_slug)
        
        content = request.POST['content']
        if len(content) == 0:
            return ask(request, error='You need to enter some content to your question.', title=title, hut_slug=hut_slug)
        
        tags = request.POST['tags'].strip().replace(',', '').replace('#', '').split(' ')
        if len(tags) == 1 and len(tags[0]) == 0:
            return ask(request, error='You need to enter some tags.', title=title, content=content, hut_slug=hut_slug)

        question = Question(title=title, content=content, author=request.user, course=hut)
        question.save()

        question.add_tag(hut.slug)
        
        question.add_tag(State.CURRENT_QUARTER)
        
        question.add_follower(request.user)
            
        for tag in tags:
            question.add_tag(tag)
            
                  
        if hut.has_approved(request.user):
            question.approved = True
            question.save()
            
            message_subscribers(hut, question, request.user)
            
            return redirect('/question/%d' % question.id)
        
        return redirect('/?msg=moderation')
    
@login_required  
def ask(request, error=None, title=None, content=None, hut_slug=None):
    if not request.user.is_authenticated():
        return redirect('/')
    else:
        if 'select' in request.GET:
            return render_to_response(
                "select.html",
                {
                    'user': request.user,
                    'huts': request.user.get_profile().courses.all()
                },
                context_instance = RequestContext(request)    
            )
        
        try:
            if not hut_slug:
                hut = Course.objects.get(slug=request.GET['hut'])
            else:
                hut = Course.objects.get(slug=hut_slug)
        except Course.DoesNotExist:
            return redirect('/ask?select')
        
        return render_to_response(
            "ask.html",
            {
                'user': request.user,
                'courses': request.user.get_profile().courses.all(),
                'error': error,
                'title': title,
                'content': content,
                'hut': hut
            },
            context_instance = RequestContext(request)
        )
        
        
def select_answer(request):
    answer = Answer.objects.get(pk=request.POST['answer'])
    question = Question.objects.get(pk=request.POST['question'])
    question.select_answer(answer)
    return json_response({
        "status": "ok"
    })
        
@login_required  
def moderate(request):
    profile = request.user.get_profile()
    if not request.user.is_authenticated() or not profile.is_hut_moderator():
        return redirect('/')

    hut_text = request.GET['course'] if 'course' in request.GET else None    
    sort = request.GET['sort'] if 'sort' in request.GET else 'recent'    
    
    query_set = answers = hut = None
    if hut_text:   
        hut = Course.objects.get(slug=hut_text)
        if hut not in profile.moderator_huts():
            ## Then they cannot moderate this specific class
            return redirect('/moderate')
        
        query_set = get_questions(huts=[hut], approved=False, user=request.user)
        query_set = sort_questions(query_set=query_set, sort=sort)    
        answers = Answer.objects.filter(approved=False, question__course__title=hut_text).order_by('-created_at')

    return render_to_response(
        "moderate.html",
        {
            'user': request.user,
            'questions': query_set,
            'sort': sort,
            'course': hut_text,
            'hut': hut,
            'moderator_huts': profile.moderator_huts(),
            'answers': answers
        },
        context_instance = RequestContext(request)
    )
    
@csrf_protect  
@login_required    
def moderate_action(request):
    obj_id = request.POST['id']
    action = request.POST['action']
    Model = models[request.POST['kind']] # 'Q' or 'A'
    obj = Model.objects.get(pk=obj_id)
    obj.moderate(action)
    return json_response({
        "status": "ok"
    })
    
@login_required  
def search(request):
    from itertools import chain
    
    q_query = get_query(request.GET['q'], ['title', 'content'])    

    a_query = get_query(request.GET['q'], ['content'])    
    
    courses = request.user.get_profile().courses.all()

    questions = Question.objects.filter(q_query).filter(approved=True).filter(course__in=courses).order_by('-votes')
    answers = Answer.objects.filter(a_query).filter(approved=True).filter(question__course__in=courses).order_by('-votes').values('question')
    more = Question.objects.filter(id__in=answers)

    ## Search comments on questions
    q_comments = Comment.objects.filter(a_query).filter(kind=Comment.QUESTION_TYPE).values('obj_id')
    comment_questions = Question.objects.filter(id__in=q_comments).filter(approved=True).filter(course__in=courses)

    ## Search comments on answers
    a_comments = Comment.objects.filter(a_query).filter(kind=Comment.ANSWER_TYPE).values('obj_id')
    answers = Answer.objects.filter(id__in=a_comments).filter(approved=True).filter(question__course__in=courses).order_by('-votes').values('question')
    comment_answers = Question.objects.filter(id__in=answers)

    questions = list(set(chain(questions, more, comment_questions, comment_answers)))

    return render_to_response(
        "search.html",
        {
            'user': request.user,
            'questions': questions
        },
        context_instance = RequestContext(request)
    )
    
def faq(request):
    return render_to_response(
        "faq.html",
        {
            'user': request.user    
        },
        context_instance = RequestContext(request)
    )
    
def users(request):
    hut = request.GET['hut'] if 'hut' in request.GET else ''
    try:
        hut = Course.objects.get(slug=hut)
    except Course.DoesNotExist:
        return redirect('/')
    
    if not has_permission(user=request.user, huts=[hut]):
        return redirect('/')
    return render_to_response(
        "users.html",
        {
            'user': request.user,
            'users': hut.members.all().order_by('-points'),
            'hut': hut  
        },
        context_instance = RequestContext(request)
    )
    
