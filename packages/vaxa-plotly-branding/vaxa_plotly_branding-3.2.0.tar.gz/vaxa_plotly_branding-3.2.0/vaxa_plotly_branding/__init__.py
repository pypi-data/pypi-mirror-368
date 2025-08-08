import plotly.io as pio

from .vaxa_plotly_template import (  # noqa: F401
    VaxaBrandingTemplate,
    VaxaBrandingTemplateNoLogo,
    vaxa_colorway,
)


def default_to_vaxa_analytics_template():
    """
    Sets the default Plotly template to the VaxaBrandingTemplate, which is a custom template
    defined in the vaxa_plotly_branding package. This function modifies the `pio.templates`
    dictionary and sets the default template to "vaxa_analytics".
    """
    pio.templates.default = "vaxa_analytics"


def default_to_vaxa_analytics_no_logo_template():
    """
    Sets the default Plotly template to the VaxaBrandingTemplateNoLogo, which is a custom template
    defined in the vaxa_plotly_branding package. This function modifies the `pio.templates`
    dictionary and sets the default template to "vaxa_analytics_no_logo".
    """
    pio.templates.default = "vaxa_analytics_no_logo"


# Default template is no longer applied automatically on import to avoid side effects.
# Users should explicitly call one of the default_to_* functions when desired.
# default_to_vaxa_analytics_template()
