Dear Sir,

The following data collectors have failed
  - Check time: {{start}}
  - Failed collectors:
{%- for e in sources %}
        {{ e -}}
{% endfor %}

Regards,

BDPOC PdM Platform
