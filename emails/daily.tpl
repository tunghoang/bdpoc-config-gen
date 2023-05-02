Dear Sir,

This is an automated email to summarize alert from {{start}} to {{end}}. 
Please check details belows:

------ BEGIN REPORT -------
Alert Type: [Alert.IRV PreAlarm]
Alert Description: 
    - Check: Intrument Range Validation
    - Tags: 
{%- for e in irv %}
        {{ e -}}
{% endfor %}

Alert Type: [Alert.ROC]
Alert Description: 
    - Check: Rate Of Change or Frozen
    - Tags: 
{%- for e in roc %}
        {{ e -}}
{% endfor %}

Alert Type: [Alert.NaN]
Alert Description: 
    - Check: NaN Check
    - Tags: 
{%- for e in nan %}
        {{ e -}}
{% endfor %}

Alert Type: [Alert.Overange]
Alert Description: 
    - Check: Overange Check
    - Tags: 
{%- for e in overange %}
        {{ e -}}
{% endfor %}
------ END REPORT -------

Best regards,

BDPOC PdM Platform

