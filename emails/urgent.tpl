Dear Sir,

This is an automated email to inform you of alerts received from the PDM system. Please review the details below:

Alert Type: [Alert.Danger]
Alert Description: 
    - Check: Instrument Range Validation
    - Tags: 
{%- for event in events %}
        {{ event.Field }} : {{ "HH" if event["Max"] >= event["HH"] else "LL"}}
{% endfor %}
Date and Time of Alert: 
    - From: {{start}}
    - To: {{end}}

Best regards,

BDPOC PDM Platform
