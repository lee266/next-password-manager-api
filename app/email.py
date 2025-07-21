
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from djoser import utils
from templated_mail.mail import BaseEmailMessage

class EmailManager(BaseEmailMessage):
    def send(self, to, *args, **kwags):
        self.render()
        self.to = to
        self.cc = kwags.pop('cc', [])
        self.bcc = kwags.pop('bcc', [])
        self.replay_to = kwags.pop('reply_to', [])
        self.from_email = kwags.pop(
          'from_email',
          'settings.EMAIL_HOST_USER'
        )
        super(BaseEmailMessage, self).send(*args **kwags)

class ActivationEmail(EmailManager):
    template_name = 'accounts/activation.html'

    def get_context_data(self):
      context = super().get_context_data()
      user = context.get("user")
      context["name"] = user.name
      context["uid"] = utils.encode_uid(user.pk)
      context["token"] = default_token_generator.make_token(user)
      context["url"] = settings.DJOSER["ACTIVATION_URL"].format(**context)
      return context


class PasswordResetEmail(BaseEmailMessage):
    template_name = 'accounts/password_reset.html'

    def get_context_data(self):
      context = super().get_context_data()
      user = context.get("user")
      context["uid"] = utils.encode_uid(user.pk)
      context["token"] = default_token_generator.make_token(user)
      context["url"] = settings.DJOSER["PASSWORD_RESET_CONFIRM_URL"].format(**context)
      print("context",context)
      return context


class PasswordChangedConfirmationEmail(BaseEmailMessage):
    template_name = 'accounts/password_changed_confirmation.html'

    def get_context_data(self):
      context = super().get_context_data()
      return context
