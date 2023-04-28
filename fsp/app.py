import os
import json

from flask import Flask, request, session, abort
from flask_cors import CORS

from .db.utils import init_connection
from .utils import hash_password, retrieve_fields
from sqlalchemy import Row
from .service import (
    ServiceManager,
    UserService,
    AthleteService,
    EventService,
    ProfileService,
    RequestService,
    TeamService,
    AthleteTeamsService,
)
from .settings import config
from .db.models import (
    Event,
    Athlete,
    AthleteTeams,
    Role,
    Team as TeamDB,
    User as UserDB,
)
from .entity import User, Claim, EventRequest, Team
from .middleware import CheckFields, auth_required
from .token import JWT
from sqlalchemy import Row
from typing import List
import bcrypt
import sqlalchemy as sa

app = Flask(__name__)
# app.wsgi_app = CheckFields(app.wsgi_app)  # проверка на пустоту JSON-объектов
CORS(app, supports_credentials=True)

app.secret_key = config.secret

engine, sess = init_connection(
    f"{config.database_dialect}+{config.database_driver}://"
    + f"{config.database_admin_username}:{config.database_admin_password}@"
    + f"{config.database_url}/{config.database_name}"
)

services = ServiceManager(sess)


@app.post("/auth/login")
def login():
    user_service = services.get(UserService)

    body = dict(request.json)
    password = body["password"]
    email = body["email"]

    user: User = user_service.get_by_login(email)

    if user is None or not bcrypt.checkpw(password.encode("utf-8"), user.password):
        abort(400, "Пользователь не существует или не найден")

    claims = list(map(lambda x: x.value, user.claims))

    token = JWT.create({"email": user.email, "claims": claims})

    return {"token": token}, 200


@app.post("/auth/register")
def register():
    user_service = services.get(UserService)
    profile_service: ProfileService = services.get(ProfileService)

    body = dict(request.json)
    auth_data = body["auth"]
    email = auth_data["email"]
    user: User = user_service.get_by_login(email)

    if user is not None:
        abort(400, "Этот пользователь уже существует")

    auth_data["password"] = hash_password(auth_data["password"])
    try:
        user = User(**auth_data)
        print(user)
        user_service.add(user)
        ok = True
    except NameError as e:
        print(f"Что-то пошло не так: {e}")
        abort(400, f"Неверный набор аргументов: {e}")
    except Exception as e:
        print(f"Что-то пошло не так: {auth_data}")
        abort(500, f"Что-то пошло не так: {e}")

    try:
        profile_service.update(email, body["profile"])
    except Exception as e:
        print(f"Что-то пошло не так: {e}")
        abort(500, f"Что-то пошло не так: {e}")

    return ("", 201)


@auth_required([Claim.ADMINISTRATOR, Claim.REPRESENTATIVE, Claim.PARTNER])
@app.post("/events")
def add_event():
    event_service: EventService = services.get(EventService)
    body = dict(request.json)

    try:
        event_service.add(Event(**body))
    except Exception as e:
        abort(400, e)

    return ("", 201)


@auth_required(
    [Claim.ADMINISTRATOR, Claim.PARTNER, Claim.ATHLETE, Claim.REPRESENTATIVE]
)
@app.get("/events")
def get_event():
    event_service: EventService = services.get(EventService)
    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))

    try:
        result: List[Row] = event_service.get(page, per_page)

        events = []
        for row in result:
            event = row[0]
            new_event = Event(
                name=event.name,
                date_started=str(event.date_started),
                date_ended=str(event.date_ended),
                location=event.location,
                about=event.about,
            )
            events.append(retrieve_fields(new_event))
        return json.dumps(events), 200
    except Exception as e:
        print(e)
        abort(400, e)


@auth_required([Claim.ADMINISTRATOR])
@app.get("/profile/<email>")
def get_profile():
    profile_service: ProfileService = services.get(ProfileService)

    try:
        result: List[Row] = profile_service.get(request.args["email"])
        return json.dumps(retrieve_fields(result)), 200
    except Exception as e:
        abort(400, e)


@auth_required([Claim.ADMINISTRATOR])
@app.post("/profile")
def update_profile(email: str):
    profile_service: ProfileService = services.get(ProfileService)
    body = dict(request.json)

    try:
        profile_service.update(email, **body["profile"])
    except Exception as e:
        abort(400, e)

    return ("", 201)


@auth_required([Claim.ADMINISTRATOR])
@app.get("/request")
def add_request(email):
    request_service: RequestService = services.get(RequestService)
    body = dict(request.json)

    try:
        request_service.add(email, EventRequest(**body))
    except Exception as e:
        abort(400, e)

    return ("", 201)


@auth_required([Claim.ADMINISTRATOR])
@app.post("/request")
def get_requests(email):
    request_service: RequestService = services.get(RequestService)

    try:
        requests = request_service.get_requests(email)
        return json.dumps(requests), "201"
    except Exception as e:
        abort(400, e)


@auth_required(
    [Claim.ATHLETE, Claim.ADMINISTRATOR, Claim.PARTNER, Claim.REPRESENTATIVE]
)
@app.get("/leaderboard/users")
def get_users_leaderboard():
    athlete_service: AthleteService = services.get(AthleteService)

    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))

    order = request.args.get("order")
    if order == "asc":
        order = True
    elif order == "desc":
        order = False

    try:
        result: List[Row] = athlete_service.get(page, per_page, order)
        athletes = []
        for row in result:
            athlete = row[0]
            new_athlete = Athlete(
                team_FK=athlete.team_FK, rating=athlete.rating, role=athlete.role
            )
            athletes.append(retrieve_fields(new_athlete))

        return json.dumps(athletes), 200

    except Exception as e:
        print(e)
        abort(400, e)


@auth_required([Claim.ATHLETE, Claim.ADMINISTRATOR, Claim.PARTNER, Claim.REPRESENTATIVE])
@app.get("/leaderboard/teams")
def get_teams_leaderboard():
    team_service: TeamService = services.get(TeamService)

    page = int(request.args.get("page"))
    per_page = int(request.args.get("per_page"))

    order = request.args.get("order")
    if order == "asc":
        order = True
    elif order == "desc":
        order = False

    try:
        result: List[Row] = team_service.get(page, per_page, order)

        teams = []
        for row in result:
            team = row[0]
            new_team = TeamDB(
                name=team.name,
                rating=team.rating,
                datetime_create=str(team.datetime_create),
            )
            teams.append(retrieve_fields(new_team))

        return json.dumps(teams), 200

    except Exception as e:
        print(e)
        abort(400, e)


@auth_required([Claim.ATHLETE])
@app.get("/teams/<name>")
def get_team_info():
    team_service: TeamService = ServiceManager(TeamService)
    athlete_service: AthleteService = ServiceManager(AthleteService)
    athlete_teams_service: AthleteTeamsService = ServiceManager(AthleteTeamsService)

    name = request.args["name"]

    try:
        team: TeamDB | None = team_service.get_by_name(name)
        if team is None:
            abort(404, "Команда с таким именем не найдена")

        athlete_teams = athlete_teams_service.get_all_by_team_id(team.id)

        athletes = []
        for t in athlete_teams:
            a: Athlete = athlete_service.get_by_id(t.athlete_id_FK)
            athletes.append(a)

        return {"name": team.name, "rating": team.rating, "athletes": athletes}, 200

    except Exception as e:
        print(e)
        abort(400, e)


@auth_required([Claim.ATHLETE])
@app.post("/teams")
def create_team():
    body = dict(request.json)
    email: str = JWT.extract(body["token"])["email"]
    if email is None:
        return (401, "Неверный или истекший JSON веб токен")

    team_service: TeamService = ServiceManager(TeamService)
    athlete_teams_service: AthleteTeamsService = ServiceManager(AthleteTeamsService)

    try:
        team = TeamDB(name=body["name"], rating=100)

        ok = team_service.add(team)
        if not ok:
            return ({"error": "Команда с таким называнием уже существует"}, 200)

        with sess() as _session:
            db_user: UserDB = _session.execute(
                sa.select(UserDB).where(UserDB.email == email)
            ).fetchone()

        if db_user.athlete_FK is None:
            return (500, "Что-то пошло не так")

        athlete_teams = AthleteTeams(
            athlete_id_FK=db_user.athlete_FK, team_id_FK=team.id, role=Role.LEAD
        )

        athlete_teams_service.add(athlete_teams)
        return ("", 201)

    except Exception as e:
        print(e)
        abort(400, e)

@auth_required([Claim.ATHLETE])
@app.post('/teams/<name>/<email>')
def add_athlete_to_the_team():

    body = dict(request.json)
    email: str = JWT.extract(body["token"])["email"]
    if email is None:
        return (401, "Неверный или истекший JSON веб токен")

    team_service: TeamService = ServiceManager(TeamService)
    athlete_teams_service: AthleteTeamsService = ServiceManager(AthleteTeamsService)

    try:
        team_name = request.args['name']
        email = request.args['email']
        team = TeamDB(name=body["name"], rating=100)
        

        ok = team_service.add(team)
        if not ok:
            return ({"error": "Команда с таким называнием уже существует"}, 200)

        with sess() as _session:
            db_user: UserDB = _session.execute(
                sa.select(UserDB).where(UserDB.email == email)
            ).fetchone()

        if db_user.athlete_FK is None:
            return (500, "Что-то пошло не так")

        athlete_teams = AthleteTeams(
            athlete_id_FK=db_user.athlete_FK, team_id_FK=team.id, role=Role.LEAD
        )

        athlete_teams_service.add(athlete_teams)
        return ("", 201)

    except Exception as e:
        print(e)
        abort(400, e)
