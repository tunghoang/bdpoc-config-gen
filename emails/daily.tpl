Dear Sir,

This is an automated email to summarize alerts generate by IHM platform in the pass 24h from {{start.strftime("%d/%m/%Y %H:%M:%S")}} to {{end.strftime("%d/%m/%Y %H:%M:%S")}}.
Please check details belows:

------ BEGIN REPORT -------
**{{DEVICE_INFO.get(device, device.upper())}}**
Alert Type: [Alert.IRV (Alarm/PreAlarm]
Alert Description: 
    - Check: Intrument Range Validation
    - Tags: 
{%- if irv | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in irv %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

Alert Type: [Alert.ROC]
Alert Description: 
    - Check: Rate Of Change or Frozen
    - Tags:
{%- if roc | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in roc %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

Alert Type: [Alert.NaN]
Alert Description: 
    - Check: NaN Check
    - Tags: 
{%- if nan | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in nan %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

Alert Type: [Alert.Overange]
Alert Description: 
    - Check: Overange Check
    - Tags: 
{%- if overange | length == 0 -%}
No Alarms
{%- endif %}
{%- for e in overange %}
        {{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}
{% endfor %}

For a more detail information, we recommend accessing the IHM platform as link http://10.17.4.61:8501/
If you have any questions or require further assistance regarding this report or any related matters, please do not hesitate to contact our team (pdm@biendongpoc.vn). We are here to provide support and address any concerns you may have.

------ END REPORT -------

Best regards,

BDPOC PdM Platform

