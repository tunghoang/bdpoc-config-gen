Dear Sir,

This is an automated email to inform you of alerts received from the PDM system. Please review the details below:

Alert Type: [Alert.Danger.Critical]
Alert Description: 
    - Check: Instrument Range Validation
    - Tags: 
{%- for event in events %}
        {{ event.Field }} ({{ tagDict.get(event.Field, {}).get("description", "N/A") }}) : {{ "HHH" if event["Max"] >= event["HHH"] else "LLL"}}
{% endfor %}
Date and Time of Alert: 
    - From: {{start}}
    - To: {{end}}

For more detail information, we recommend accessing the IHM platform at http://10.17.4.61:8501/
If you have any questions or require further assistance regarding this anomaly or any related matters, please do not hesitate to contact our team (pdm@biendongpoc.vn). We are here to provide support and address any concerns you may have.

Best regards,

BDPOC PDM Platform
