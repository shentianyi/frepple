#
# Copyright (C) 2007-2013 by frePPLe bvba
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from freppledb.common.models import User, AuditModel, MultiDBManager

import logging
logger = logging.getLogger(__name__)


class Task(models.Model):
  '''
  Expected status values are:
    - 'Waiting'
    - 'Done'
    - 'Failed'
    - 'Canceled'
    - 'DD%', where DD represents the percentage completed
  Other values are okay, but the above have translations.
  '''
  # Database fields
  id = models.AutoField(_('identifier'), primary_key=True, editable=False)
  #. Translators: Translation included with Django
  name = models.CharField(_('name'), max_length=50, db_index=True, editable=False)
  submitted = models.DateTimeField(_('submitted'), editable=False)
  started = models.DateTimeField(_('started'), blank=True, null=True, editable=False)
  finished = models.DateTimeField(_('submitted'), blank=True, null=True, editable=False)
  arguments = models.TextField(_('arguments'), max_length=200, null=True, editable=False)
  status = models.CharField(_('status'), max_length=20, editable=False)
  message = models.TextField(_('message'), max_length=200, null=True, editable=False)
  logfile = models.TextField(_('log file'), max_length=200, null=True, editable=False)
  #. Translators: Translation included with Django
  user = models.ForeignKey(
    User, verbose_name=_('user'), blank=True, null=True,
    editable=False, on_delete=models.CASCADE
    )

  def __str__(self):
    return "%s - %s - %s" % (self.id, self.name, self.status)

  class Meta:
    db_table = "execute_log"
    verbose_name_plural = _('tasks')
    verbose_name = _('task')

  @staticmethod
  def submitTask():
    # Add record to the database
    # Check if a worker is present. If not launch one.
    return 1


class DataStagingLog(AuditModel):
  id = models.AutoField(_('identifier'), primary_key=True, editable=False)
  nr = models.CharField(_('nr'), max_length=300, editable=False, db_index=True)
  create_user_nr = models.CharField(_('create_user_nr'), max_length=100,editable=False,db_index=True,blank= True, null=True)
  input_data = models.TextField(_('input_data'),blank= True, null=True)
  output_data = models.TextField(_('output_data'),blank= True, null=True)
  result = models.BooleanField(_('result'), default=False)
  message = models.TextField(_('message'),blank= True, null=True)
  start_at = models.DateTimeField(_('start_at'),blank= True, null=True)
  end_at = models.DateTimeField(_('end_at'),blank= True, null=True)


  class Manager(MultiDBManager):
    pass

  objects = Manager()

  class Meta(AuditModel.Meta):
        db_table = 'data_staging_log'
        verbose_name = _('data_staging_log')
        verbose_name_plural = _('data_staging_logs')


