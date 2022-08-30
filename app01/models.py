# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Adminuser(models.Model):
    admin_id = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    disable = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adminuser'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
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


class AuthTable(models.Model):
    accountid = models.CharField(max_length=255, blank=True, null=True)
    openid = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_table'


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Comments(models.Model):
    videoid = models.CharField(max_length=255)
    userid = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
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


class FileStorage(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'file_storage'


class Healthinfo(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    birthyear = models.CharField(max_length=255, blank=True, null=True)
    illtime = models.CharField(max_length=255, blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    surgerytime = models.CharField(db_column='surgeryTime', max_length=255, blank=True, null=True)  # Field name made lowercase.
    degree = models.CharField(max_length=255, blank=True, null=True)
    illtype = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'healthinfo'


class LookVideo(models.Model):
    url = models.CharField(max_length=255)
    videotype = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    appurl = models.CharField(max_length=255, blank=True, null=True)
    logourl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'look_video'


class Pose(models.Model):
    after_url = models.CharField(max_length=255, blank=True, null=True)
    before_url = models.CharField(max_length=255)
    user_openid = models.CharField(max_length=255)
    pose_report = models.TextField(blank=True, null=True)
    doctor_url = models.CharField(max_length=255, blank=True, null=True)
    assessstatus = models.IntegerField(db_column='assessStatus')  # Field name made lowercase.
    doctor_app_url = models.CharField(max_length=255, blank=True, null=True)
    csv_url = models.CharField(max_length=255, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pose'


class RecordData(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    sequenceid = models.CharField(db_column='sequenceId', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'record_data'


class RecoveryRank(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recovery_rank'


class Test(models.Model):
    name = models.CharField(max_length=10, db_collation='utf8_general_ci')

    class Meta:
        managed = False
        db_table = 'test'


class TotalData(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    data = models.CharField(max_length=255, blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'total_data'


class TrainResult(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    trainscore = models.FloatField(blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'train_result'


class TranData(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    time = models.CharField(max_length=255, blank=True, null=True)
    sequenceid = models.CharField(db_column='sequenceId', max_length=255, db_collation='armscii8_general_ci', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tran_data'


class Userinfo(models.Model):
    openid = models.CharField(max_length=255, blank=True, null=True)
    ipname = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    disable = models.IntegerField(blank=True, null=True)
    avatar = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'userinfo'
