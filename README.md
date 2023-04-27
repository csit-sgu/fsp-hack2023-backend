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

## `GET /events`
```json
{
  "page" : 3,
  "per_page": 15
}
```

## `POST /events`
```json
{
  "date_started": "yyyy-mm-dd",
  "date_ended": "yyyy-mm-dd",
  "location": "Some location",
  "about": "Some description"
}
```