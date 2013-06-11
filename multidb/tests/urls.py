from django.conf.urls import patterns

from multidb.tests.views import class_based_dummy_view, object_dummy_view

urlpatterns = patterns('',
  (r'^dummy/$', 'multidb.tests.views.dummy_view'),
  (r'^cdummy/$', class_based_dummy_view.as_view()),
  (r'^odummy/$', object_dummy_view()),
)
