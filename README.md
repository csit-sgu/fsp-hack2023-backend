# API

## `POST /auth/register`
```json
{
  "email": "b", 
  "password": "c"
}
```


## `POST /auth/login`
```json
{
  "email": "b", 
  "password": "c"
}
```

## `GET /events&page=3&per_page=15`

## `POST /events`
```json
{
  "name" : "Some interesting name",
  "date_started" : "%y/%m/%d %H:%M:%S",
  "date_ended" : "%y/%m/%d %H:%M:%S",
  "location" : "Some location",
  "about" : "Some description"
}
```