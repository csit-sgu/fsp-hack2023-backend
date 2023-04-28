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

## `POST /profile`
```json
{
  "phone": "string",
  "address": "string",
  "passport": "string",
  "birthday": "yyyy-mm-dd",
  "gender": "string",
  "organization": "string",
  "name": "string",
  "surname": "string",
  "patronymic": "string",
  "insurance": "string"
}
```

## `GET /profile/<url parameter>`

## `GET /request`

```json
{
  ""
}
```

