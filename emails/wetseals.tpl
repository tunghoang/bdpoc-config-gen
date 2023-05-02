Dear Sir,

This is an automated email to inform you of alerts received from the PDM system. Please review the details below:

Alert Type: [Alert.Danger]
Alert Description: 
    - Check: Wet gas seal check
    - Tags: 
{%- for seal in seals %}
        {{ seals.Field }} : flush count per 24h is {{seal.flush_count}}, and tank level decreased by {{seal.dropLevel}}
{% endfor %}
Date and Time of Alert: 
    - From: {{start}}
    - To: {{end}}

Best regards,

BDPOC PDM Platform
