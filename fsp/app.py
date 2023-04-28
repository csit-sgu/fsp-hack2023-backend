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
    Profile,
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

from uuid import uuid4

app = Flask(__name__)
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
    session_id = uuid4()
    user_service = services.get(UserService)

    body = dict(request.json)
    password = body["password"]
    email = body["email"]

    user: User = user_service.get_by_login(email)

    if user is None or not bcrypt.checkpw(password.encode("utf-8"), user.password):
        error = {"error": f"Пользователь не существует или не найден ({session_id})"}
        app.logger.error(error)
        abort(400, error)

    claims = list(map(lambda x: x.value, user.claims))

    token = JWT.create({"email": user.email, "claims": claims, "uuid": session_id})

    app.logger.info(f"Аутентификация прошла успешно ({session_id})")
    return {"token": token}, 200


@app.post("/auth/register")
def register():
    session_id = uuid4()
    user_service = services.get(UserService)
    profile_service: ProfileService = services.get(ProfileService)

    body = dict(request.json)
    auth_data = body["auth"]
    email = auth_data["email"]
    user: User = user_service.get_by_login(email)

    if user is not None:
        error = {"error": "Пользователь с таким адресом уже существует"}
        app.logger.error(f"Пользователь с таким адресом уже существует ({session_id})")
        abort(400, {"error": error, "session_id": session_id})

    auth_data["password"] = hash_password(auth_data["password"])
    try:
        user = User(**auth_data)
        user_service.add(user)
        app.logger.info(f"Пользователь успешно зарегистрирован ({session_id})")
    except NameError as e:
        abort(
            400,
            {
                "error": f"Некорректный набор параметров ({session_id})",
                "session_id": session_id,
            },
        )
    except Exception as e:
        abort(
            500,
            {"error": f"Что-то пошло не так ({session_id})", "session_id": session_id},
        )

    try:
        profile_service.update(email, body["profile"])
    except Exception as e:
        app.logger.info(f"Что-то пошло не так при создании профиля: {e} ({session_id})")
        abort(500, {"error": f"Что-то пошло не так", "session_id": session_id})

    return ("", 201)


@auth_required([Claim.ADMINISTRATOR, Claim.REPRESENTATIVE, Claim.PARTNER])
@app.post("/events")
def add_event():
    session_id = uuid4()
    event_service: EventService = services.get(EventService)
    body = dict(request.json)

    try:
        event_service.add(Event(**body))
        app.logger.info(f"Событие успешно добавлено ({session_id})")
    except Exception as e:
        app.logger.error(f"Что-то пошло не так: {e}")
        abort(500, {"error": "Что-то пошло не так", "session_id": session_id})

    return ("", 201)


@auth_required(
    [Claim.ADMINISTRATOR, Claim.PARTNER, Claim.ATHLETE, Claim.REPRESENTATIVE]
)
@app.get("/events")
def get_event():
    session_id = uuid4()
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
            app.logger.info(f"События успешно получены ({session_id})")
        return json.dumps(events), 200
    except Exception as e:
        error = f"Что-то пошло не так: "
        app.logger.error(f"Что-то пошло не так: {e} ({session_id})")
        abort(400, {"error": "Что-то пошло не так", "session_id": session_id})


@auth_required([Claim.ADMINISTRATOR])
@app.get("/profile/<email>")
def get_profile():
    session_id = uuid4()
    profile_service: ProfileService = services.get(ProfileService)

    try:
        result: List[Row] = profile_service.get(request.args["email"])
        app.logger.info(f"Профиль успешно получен ({session_id})")
        return json.dumps(retrieve_fields(result)), 200
    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e})")
        abort(400, {"error": error, "session_id": session_id})


@auth_required([Claim.ADMINISTRATOR])
@app.post("/profile")
def update_profile(email: str):
    session_id = uuid4()
    profile_service: ProfileService = services.get(ProfileService)
    body = dict(request.json)

    try:
        profile_service.update(email, **body["profile"])
        app.logger.info(f"Профиль успешно обновлен ({session_id})")
        return ("", 201)
    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"Что-то пошло не так: {e} ({session_id})")
        abort(400, {"error": error, "session_id": session_id})


@auth_required([Claim.ADMINISTRATOR])
@app.get("/request")
def add_request(email):
    session_id = uuid4()
    request_service: RequestService = services.get(RequestService)
    body = dict(request.json)

    try:
        request_service.add(email, EventRequest(**body))
        app.logger.info(f"Запрос успешно создан ({session_id})")
        return ("", 201)
    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e}")
        abort(500, {"error": error, "session_id": session_id})


@auth_required([Claim.ADMINISTRATOR])
@app.post("/request")
def get_requests(email):
    session_id = uuid4()
    request_service: RequestService = services.get(RequestService)

    try:
        requests = request_service.get_requests(email)
        app.logger.info(f"Запросы успешно получены {session_id}")
        return json.dumps(requests), "201"
    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e}")
        abort(500, {"error": error, "session_id": session_id})


@auth_required(
    [Claim.ATHLETE, Claim.ADMINISTRATOR, Claim.PARTNER, Claim.REPRESENTATIVE]
)
@app.get("/leaderboard/users")
def get_users_leaderboard():
    session_id = uuid4()
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
        app.logger.log(f"Рейтинг спортсменов получен успешно ({session_id})")
        return json.dumps(athletes), 200

    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e}")
        abort(500, {"error": error, "session_id": session_id})


@auth_required(
    [Claim.ATHLETE, Claim.ADMINISTRATOR, Claim.PARTNER, Claim.REPRESENTATIVE]
)
@app.get("/leaderboard/teams")
def get_teams_leaderboard():
    session_id = uuid4()
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
        app.logger.info(f"Рейтинг команд получен успешно ({session_id})")
        return json.dumps(teams), 200

    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e}")
        abort(500, {"error": error, "session_id": session_id})


@auth_required([Claim.ATHLETE])
@app.get("/teams/<name>")
def get_team_info():
    session_id = uuid4()
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
        app.logger.info(f"Информация о команде получена успешно ({session_id})")
        return {"name": team.name, "rating": team.rating, "athletes": athletes}, 200

    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e}")
        abort(500, {"error": error, "session_id": session_id})


@auth_required([Claim.ATHLETE])
@app.post("/teams")
def create_team():
    session_id = uuid4()
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
        app.logger.log(f"Команда создана успешно({session_id})")
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

@auth_required([Claim.ADMINISTRATOR, Claim.ATHLETE, Claim.PARTNER, Claim.REPRESENTATIVE])
@app.get('/me/profile')
def get_my_profile():
    session_id = uuid4()

    body = dict(request.json)
    email: str = JWT.extract(body["token"])["email"]
    if email is None:
        return (401, "Неверный или истекший JSON веб токен")

    user_service: UserService = ServiceManager(UserService)
    user: User = user_service.get_by_login(email)

    with sess() as _session:
        db_user: UserDB = _session.execute(
            sa.select(UserDB)
            .where(UserDB.email == user.email)
        ).fetchone()[0]

        if db_user.personal_FK is None:
            return (500, 'Что-то пошло не так')

        profile: Profile = _session.execute(
            sa.select(Profile)
            .where(Profile.id == db_user.personal_FK)
        ).fetchone()
        
        return {
            'phone': profile.phone,
            'address': profile.address,
            'passport': profile.passport,
            'birthday': profile.birthday,
            'gender': profile.gender.value,
            'organization': profile.organization,
            'skills': profile.skills,
            'name': profile.name,
            'surname': profile.surname,
            'patronymic': profile.patronymic,
            'insurance': profile.insurance
        }, 200

    try:
        team: TeamDB | None = team_service.get_by_name(name)
        if team is None:
            abort(404, "Команда с таким именем не найдена")

        athlete_teams = athlete_teams_service.get_all_by_team_id(team.id)

        athletes = []
        for t in athlete_teams:
            a: Athlete = athlete_service.get_by_id(t.athlete_id_FK)
            athletes.append(a)
        app.logger.info(f"Информация о команде получена успешно ({session_id})")
        return {"name": team.name, "rating": team.rating, "athletes": athletes}, 200

    except Exception as e:
        error = f"Что-то пошло не так ({session_id})"
        app.logger.error(f"{error}: {e}")
        abort(500, {"error": error, "session_id": session_id})