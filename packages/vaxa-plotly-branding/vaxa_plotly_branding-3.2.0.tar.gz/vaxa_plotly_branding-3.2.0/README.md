Automatically brands Plotly charts with Vaxa Analytics branding.

## Installation
    
    ```bash
    pip install vaxa_plotly_branding
    ```

## Usage

    ```python
    import plotly.express as px
    import vaxa_plotly_branding

    # use templates manually
    px.line().update_layout(template='vaxa_analytics')
    px.line().update_layout(template='vaxa_analytics_no_logo')

    # or register by default
    from vaxa_plotly_branding import default_to_vaxa_analytics_template
    default_to_vaxa_analytics_template()
    px.line() # will use vaxa_analytics template by default

    from vaxa_plotly_branding import default_to_vaxa_analytics_no_logo_template
    default_to_vaxa_analytics_no_logo_template()
    px.line() # will use vaxa_analytics_no_logo template by default    
    ```

