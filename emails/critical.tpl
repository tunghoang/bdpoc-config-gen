Dear Sir,

This is an automated email to inform you of alerts received from the PDM system. Please review the details below:

Alert Type: [Alert.Danger.Critical]
Alert Description: 
    - Check: Instrument Range Validation
    - Tags: 
{%- for event in events %}
        {{ event.Field }} : {{ "HHH" if event["Max"] >= event["HHH"] else "LLL"}}
{% endfor %}
Date and Time of Alert: 
    - From: {{start}}
    - To: {{end}}

Best regards,

BDPOC PDM Platform
