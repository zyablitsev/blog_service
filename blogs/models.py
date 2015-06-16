# coding: utf-8
from django import forms

from django.db import models
from django.db.models.signals import post_save

from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)

from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser,
                     **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        now = timezone.now()
        email = self.normalize_email(email)

        user = self.model(email=email,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user=self._create_user(email, password, True, True,
                               **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), max_length=255, unique=True,
                              db_index=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log'
                    ' into this admin site.'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __unicode__(self):
        return self.email

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def subscribe_me(self, subscription_user_id):
        subscription_user = User.objects.get(pk=subscription_user_id)
        subscription = Subscription(subscriber=self,
                                    subscription=subscription_user)
        subscription.save()

    def unsubscribe_me(self, subscription_user_id):
        subscription_user = User.objects.get(pk=subscription_user_id)
        subscription = Subscription.objects.filter(
            subscriber=self, subscription=subscription_user).delete()

    def feed(self):
        return Post.objects.filter(
            user__in=[x.subscription for x
                      in self.subscriber.all()]).order_by('-created_at')


class Post(models.Model):
    title = models.CharField(_('Label'), max_length=255)
    text = models.TextField(_('Text'))
    created_at = models.DateTimeField(_('Created'), default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    REQUIRED_FIELDS = ['title', 'text']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return 'post', (), {'pk': str(self.id)}


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, related_name='subscriber',
                                   on_delete=models.CASCADE)
    subscription = models.ForeignKey(User, related_name='subscription',
                                     on_delete=models.CASCADE)
    synced_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = (("subscriber", "subscription"), )


class PostRead(models.Model):
    blog_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)


def notify_subscribers(sender, instance, **kwargs):
    subscribes = instance.user.subscription.filter(
        synced_at__lte=instance.created_at)

    for subscribe in subscribes:
        subscribe.subscriber.email_user(
            subject="New post",
            message="Link %s" % instance.get_absolute_url(),
            from_email='simple@blog.com')

post_save.connect(notify_subscribers, sender=Post,
                  dispatch_uid="do_notify_subscribers")
