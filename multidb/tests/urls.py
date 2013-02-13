from django.conf.urls import patterns

urlpatterns = patterns('',
  (r'^normal/$', 'multidb.tests.views.normal_view'),
  (r'^always_pin/$', 'multidb.tests.views.view_that_always_changes_the_db'),
)
