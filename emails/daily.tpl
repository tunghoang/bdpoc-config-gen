<div style="font-size: 15px;">
<p>Dear Sir,</p>

<p>This is an automated email to summarize alerts generate by IHM platform in the pass 24h from {{start.strftime("%d/%m/%Y %H:%M:%S")}} to {{end.strftime("%d/%m/%Y %H:%M:%S")}}.
Please check details belows:
</p>
<code>
------ BEGIN REPORT -------<br/>
**{{DEVICE_INFO.get(device, device.upper())}}**<br/>
Alert Type: [Alert.IRV (Alarm/PreAlarm]<br/>
Alert Description: <br/>
    - Check: Intrument Range Validation<br/>
    - Tags:
{%- if irv | length == 0 -%}
<b> No Alarms</b><br/>
{%- else -%}
<ul>
{%- for e in irv %}
        <li>{{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}</li>
{% endfor %}
</ul>
{%- endif %}
<br/>
Alert Type: [Alert.ROC]<br/>
Alert Description: <br/>
    - Check: Rate Of Change or Frozen<br/>
    - Tags:
{%- if roc | length == 0 -%}
<b> No Alarms</b><br/>
{%- else -%}
<ul>
{%- for e in irv %}
        <li>{{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}</li>
{% endfor %}
</ul>
{%- endif %}
<br/>
Alert Type: [Alert.NaN]<br/>
Alert Description: <br/>
    - Check: NaN Check<br/>
    - Tags: 
{%- if nan | length == 0 -%}
<b> No Alarms</b><br/>
{%- else -%}
<ul>
{%- for e in irv %}
        <li>{{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}</li>
{% endfor %}
</ul>
{%- endif %}
<br/>
Alert Type: [Alert.Overange]<br/>
Alert Description: <br/>
    - Check: Overange Check<br/>
    - Tags:
{%- if overange | length == 0 -%}
<b> No Alarms</b><br/>
{%- else -%}
<ul>
{%- for e in irv %}
        <li>{{ e -}}: {{ tagDict.get(e, {}).get('description', "N/A") -}}</li>
{% endfor %}
</ul>
{%- endif %}
<p>
For a more detail information, we recommend accessing the IHM platform as link http://10.17.4.61:8501/
If you have any questions or require further assistance regarding this report or any related matters, please do not hesitate to contact our team (pdm@biendongpoc.vn). We are here to provide support and address any concerns you may have.
</p>
------ END REPORT -------<br/>
</code>
<p>
Best regards,
</p>
<p>
BDPOC PdM Platform
</p>
</div>
