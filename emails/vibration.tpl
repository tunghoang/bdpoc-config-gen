Dear Sir,

This is an automated email to inform you of alerts received from the PDM system. Please review the details below:

Alert Type: [{{events[0][alertType]}}]
Alert Description: 
    - Check: VIBRATION
    - Tags: 
{%- for event in events %}
        {{ event["_field"] }} ({{ tagDict.get(event["_field"], {}).get("description", "N/A") }}) : {{ event["alarmType"]}} at {{event["_time"]}}
{% endfor %}
Date and Time of Alert: 
    - From: {{start}}
    - To: {{end}}

For more detail information, we recommend accessing the IHM platform at http://10.17.4.61:8501/
If you have any questions or require further assistance regarding this anomaly or any related matters, please do not hesitate to contact our team (pdm@biendongpoc.vn). We are here to provide support and address any concerns you may have.

Best regards,

BDPOC PDM Platform
