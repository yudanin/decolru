from django.db import models
from django.core.validators import ValidationError
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

import os


@deconstructible
class ProhibitedFileExtensionValidator:
    def __init__(self, prohibited_extensions, message=None):
        self.prohibited_extensions = prohibited_extensions
        self.message = message

    def __call__(self, value):
        if value.name.split('.')[-1] in self.prohibited_extensions:
            if self.message is None:
                raise ValidationError('Prohibited file extension detected.')
            else:
                raise ValidationError(self.message)


@deconstructible
class FileSizeValidator(object):
    error_messages = {
         'max_size': _("Ensure this file size is not greater than %(max_size)s."),
    }

    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(self.error_messages['max_size'],
                                  code='max_size',
                                  params={'max_size': filesizeformat(self.max_size)})


class Msgs(models.Model):
    lang_code = models.IntegerField(null=False)
    page_id = models.IntegerField(blank=True, null=True)
    msg_id = models.IntegerField(null=False)
    msg_name = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'msg_translation'
        verbose_name_plural = "Messages"


class Resources(models.Model):
    id = models.AutoField(primary_key=True)
    resource_status = models.ForeignKey('ResourceStatuses', on_delete=models.SET_NULL, null=True,
                                        related_name="resource_status")
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    # type = models.ForeignKey('ResourceTypes', on_delete=models.SET_NULL, null=True, related_name="type")
    type_id = models.IntegerField()
    journal = models.CharField(max_length=255, blank=True, null=True)
    group_link = models.CharField(max_length=1000, blank=True, null=True)
    journal_issue = models.CharField(max_length=100, blank=True, null=True)
    book = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    resource_link = models.CharField(max_length=1000, blank=True, null=True)
    lang = models.ForeignKey('Langs', on_delete=models.SET_NULL, null=True, related_name="lang")
    img = models.ImageField(upload_to='images', max_length=255)
    img_file = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    date_added_to_lib = models.DateTimeField(blank=True, null=True)
    slug = models.CharField(max_length=255)
    suggested_authors = models.CharField(max_length=255, blank=True, null=True)
    suggested_editors = models.CharField(max_length=255, blank=True, null=True)
    submitter_name = models.CharField(max_length=100, blank=True, null=True)
    submitter_email = models.EmailField(max_length=255, blank=True, null=True)
    submitter_comments = models.CharField(max_length=1000, blank=True, null=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    resource_file = models.FileField(upload_to='resource_files',
                                     validators=[
                                         ProhibitedFileExtensionValidator(prohibited_extensions=['exe', 'bat']),
                                         FileSizeValidator(max_size=50 * 1024 * 1024)  # 50MB in bytes
                                     ],
                                     max_length=255)

    authored_resources = models.ManyToManyField('Authors', through='AuthorsXResources',
                                                related_name='authored_resources', blank=True)

    tags_in_resources = models.ManyToManyField('Tags', through='TagsXResources', related_name='tags_in_resources',
                                               blank=True)

    @property
    def authors_full_name(self):
        return self.get_authors_editors_full_name_lat(1, False)

    @property
    def editors_full_name(self):
        return self.get_authors_editors_full_name_lat(2, False)

    @property
    def authors_full_name_lat(self):
        return self.get_authors_editors_full_name_lat(1, True)

    @property
    def editors_full_name_lat(self):
        return self.get_authors_editors_full_name_lat(2, True)

    def get_authors_editors_full_name_lat(self, type_of, if_lat):
        # authors_x_resources = AuthorsXResources.objects.filter(resource=self, type_of=type_of)
        authors_x_resources = AuthorsXResources.objects.filter(resource=self, type_of=type_of).exclude(
            author_id=-1)  # exclude no-author records
        authors = [author_x_resource.author for author_x_resource in authors_x_resources]
        if if_lat:
            return ', '.join([author.get_full_name_lat() for author in authors])
        else:
            return ', '.join([author.get_full_name() for author in authors])

    def __str__(self):
        return f"{self.title}, {self.subtitle}, {self.date_created}"

    class Meta:
        managed = False
        db_table = 'resources'
        verbose_name_plural = "Resources"


class Authors(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=False)
    affiliation = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    first_name_lat = models.CharField(max_length=255, blank=True, null=True)
    last_name_lat = models.CharField(max_length=255, blank=True, null=True)

    authored_by = models.ManyToManyField(Resources, through='AuthorsXResources', related_name='authored_by')

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name_lat(self):
        return f"{self.first_name} {self.last_name} ({self.first_name_lat} {self.last_name_lat})"

    def __str__(self):
        return self.get_full_name()

    class Meta:
        managed = False
        db_table = 'authors'
        verbose_name_plural = "Authors"


class AuthorsXResources(models.Model):
    # author_id = models.IntegerField(blank=True, null=True)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE, null=True, db_column='author_id')
    # resource_id = models.IntegerField(blank=True, null=True)
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE, null=True, db_column='resource_id')
    type_of = models.IntegerField(blank=True, null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        db_table = 'authors_x_resources'
        unique_together = ('author', 'resource')


class Langs(models.Model):
    lang_code_2 = models.CharField(max_length=2, blank=True, null=True)
    lang_code_3 = models.CharField(max_length=3, blank=True, null=True)
    lang_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.lang_name}"

    class Meta:
        managed = False
        db_table = 'langs'
        verbose_name_plural = "Languages"


class ResourceStatuses(models.Model):
    description = models.CharField(max_length=25, blank=True, null=True)

    def __str__(self):
        return f"{self.description}"

    class Meta:
        managed = False
        db_table = 'resource_statuses'
        verbose_name_plural = "Resource Statuses"


class ResourceTypes(models.Model):
    resource_type_id = models.IntegerField(blank=True, null=True)
    lang_id = models.IntegerField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resource_types'
        verbose_name_plural = "Resource Types"

    def __str__(self):
        return self.description


class Tags(models.Model):
    description = models.CharField(unique=True, max_length=50, blank=True, null=True)
    tags_for = models.ManyToManyField(Resources, through='TagsXResources', related_name='tags_for')

    def __str__(self):
        return f"{self.description}"

    class Meta:
        managed = False
        db_table = 'tags'
        verbose_name_plural = "Tags"


class TagsXResources(models.Model):
    # tag_id = models.IntegerField(blank=True, null=True)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, null=True, db_column='tag_id')
    # resource_id = models.IntegerField(blank=True, null=True)
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE, null=True, db_column='resource_id')

    class Meta:
        managed = False
        db_table = 'tags_x_resources'
        unique_together = ('tag', 'resource')





class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
