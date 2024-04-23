FROM public.ecr.aws/lambda/python:3.10
# Copy function code
# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY ./api/requirements.txt .
RUN pip3 install -r requirements.txt
COPY ./api ${LAMBDA_TASK_ROOT}
# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]