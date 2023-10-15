Dear Sir,

This is an automated email to summarize alert from {{start}} to {{end}}. 
Please check details belows:

------ BEGIN REPORT -------
{%- for d in devices %}
**{{DEVICE_INFO.get(d, d.upper())}}**
Alert Type: [Alert.IRV (Alarm/PreAlarm]
Alert Description: 
    - Check: Intrument Range Validation
    - Tags: 
{%- if irv[d] | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in irv[d] %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

Alert Type: [Alert.ROC]
Alert Description: 
    - Check: Rate Of Change or Frozen
    - Tags:
{%- if roc[d] | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in roc[d] %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

Alert Type: [Alert.NaN]
Alert Description: 
    - Check: NaN Check
    - Tags: 
{%- if nan[d] | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in nan[d] %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

Alert Type: [Alert.Overange]
Alert Description: 
    - Check: Overange Check
    - Tags: 
{%- if overange[d] | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in overange[d] %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}
{% endfor %}
------ END REPORT -------

Best regards,

BDPOC PdM Platform

