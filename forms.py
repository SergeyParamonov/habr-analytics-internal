# -*- coding: utf-8 -*-
from wtforms import Form, SelectField, validators, TextField, RadioField

class HubList(Form):
  hubs = SelectField("Hub")

  def set_choices(self, choices):
    self.hubs.choices = choices
    self.hubs.choices.insert(0, ('', u'\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0425\u0430\u0431'))


class UserNameForm(Form):
  name = TextField(u'Username', [validators.required(), validators.length(max=50)])
  datatype = RadioField(u'Type',  [validators.required()], choices=[(u'pageview',u'Просмотры'),('score',u'Рейтинг'),('favorites',u'Избранное')], default='pageview')

class MonitorForm(Form):
  post_id  = SelectField("Title")
  datatype = RadioField(u'Type',  [validators.required()], choices=[(u'pageview',u'Просмотры'),('favorites',u'Избранное'), ('shares',u'Репосты')], default='pageview')

  def set_choices(self, choices):
    self.post_id.choices = choices
