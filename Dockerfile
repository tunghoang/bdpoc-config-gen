FROM python:3.8.16
USER root
COPY ./ /datahub/
WORKDIR /datahub
#RUN apt update
RUN pip install -r /datahub/requirements.txt
RUN pip install python-dotenv 
RUN pip install assets/components/dist/*.whl
CMD streamlit run visualize/app.py
