from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template import loader

User = get_user_model()


class ResetPasswordMixin():
    subject_template_name="registration/password_reset_subject.txt"
    email_template_name="django_accounts_api/set_password_email.html"
    html_email_template_name="django_accounts_api/set_password_email_html.html"
    from_email=None
    extra_email_context=None

    def set_reset_link(self, user):
        # Generate a one-use only link for resetting password and send it to the user.
        use_https = self.request.is_secure()
        token_generator=default_token_generator
        current_site = get_current_site(self.request)
        domain = current_site.domain
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        reset_path = reverse('django_accounts_api:password_reset_confirm', kwargs=dict(
            uidb64=uid,
            token=token
        ))
        protocol = "https" if use_https else "http"
        self.reset_link = f"{protocol}://{domain}{reset_path}"

        site_name = current_site.name
        email_field_name = User.get_email_field_name()
        user_email = getattr(user, email_field_name)
        if user_email:
            context = {
                "email": user_email,
                "site_name": site_name,
                "uid": uid,
                "user": user,
                "reset_link": self.reset_link,
                **(self.extra_email_context or {}),
            }
            self.sent_email = self.send_mail(
                self.subject_template_name,
                self.email_template_name,
                context,
                self.from_email,
                user_email,
                html_email_template_name=self.html_email_template_name,
            )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        return email_message.send()
