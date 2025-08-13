from django.conf import settings

class ConfigurableFormTemplateResponseMixin():
    """ Overrides get_template_names to default to django_Accounts_api form template
    and provide an override capability through setttings
    """

    #: The default template for any form
    default_template_name = "django_accounts_api/form.html"
    #: The setting thaat provides the default template for all these views
    default_template_name_setting = "ACCOUNT_API_FORM_TEMPLATE_DEFAULT"
    #: The setting thaat provides the template name for this view
    template_name_setting = None

    def get_template_names(self) -> list[str]:
        """ Return the configured setting, or the default
        """
        return [
            getattr(
                settings,
                self.template_name_setting,
                None
            ) if self.template_name_setting else getattr(
                settings,
                self.default_template_name_setting,
                self.default_template_name
            )
        ]
