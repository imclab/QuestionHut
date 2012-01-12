from django.conf.urls.defaults import *
from django.conf import settings
import os
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^$', 'qa.views.index'),
    (r'^login$', 'qa.views.login'),
    (r'^join$', 'qa.views.join'),
    (r'^logout$', 'qa.views.logout'),
    (r'^error$', 'qa.views.error'),
    (r'^confirm$', 'qa.views.confirm'),
    (r'^faq$', 'qa.views.faq'),
    
    (r'^ask/?$', 'qa.views.ask'),
    (r'^ask_question$', 'qa.views.ask_question'),
    
    (r'^question/(?P<id>\d+)/?$', 'qa.views.question_view'),
    (r'^answer_question$', 'qa.views.answer_question'),

    (r'^ajax/delete$', 'qa.views.delete_question'),
    (r'^ajax/follow$', 'qa.views.follow_question'),
    (r'^ajax/subscribe$', 'qa.views.subscribe_to_hut'),
    
    
    (r'^ajax/vote$', 'qa.views.vote'),
    (r'^ajax/moderate$', 'qa.views.moderate_action'),
    (r'^ajax/select_answer$', 'qa.views.select_answer'),
    (r'^ajax/join_hut$', 'qa.views.join_hut'),
    (r'^ajax/drop_hut$', 'qa.views.drop_hut'),
    
    
    (r'^submit_comment$', 'qa.views.submit_comment'),
    
    (r'^moderate/?$', 'qa.views.moderate'),
    
    (r'^questions/?$', 'qa.views.questions_display'),
    
    (r'^users/?$', 'qa.views.users'),
    (r'^search/?$', 'qa.views.search'),
    
    (r'^admin/', include(admin.site.urls)),
    
    
    (r'^huts/?$', 'qa.views.huts'),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.dirname(settings.PROJECT_ROOT)}),
    )