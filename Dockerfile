FROM python:3.9 AS build

ADD . /app
WORKDIR /app
RUN pip install poetry && \
    poetry build

FROM python:3.9-alpine
COPY --from=build /app/dist /app/dist
RUN pip install gitlab-actions -f file:///app/dist
CMD [ "gljob" ]
