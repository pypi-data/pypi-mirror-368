"""Combined team model."""

# pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-arguments
import functools
import re
import unicodedata
from typing import Any

from ..coach_model import CoachModel
from ..news_model import NewsModel
from ..odds_model import OddsModel
from ..player_model import PlayerModel
from ..social_model import SocialModel
from ..team_model import VERSION, TeamModel
from .combined_coach_model import create_combined_coach_model
from .combined_player_model import create_combined_player_model
from .ffill import ffill
from .most_interesting import more_interesting

REGEX = re.compile("[^a-zA-Z]")


def _normalise_name(name: str) -> str:
    # Handle "Surname, Firstname"
    if "," in name:
        name = " ".join(reversed([x.strip() for x in name.split(",")]))
    return REGEX.sub("", unicodedata.normalize("NFC", name).lower().strip())


def _compare_player_models(left: PlayerModel, right: PlayerModel) -> int:
    if left.jersey is not None and right.jersey is not None:
        if left.jersey < right.jersey:
            return -1
        if left.jersey > right.jersey:
            return 1
    if left.name < right.name:
        return -1
    if left.name < right.name:
        return 1
    return 0


def create_combined_team_model(
    team_models: list[TeamModel],
    identifier: str,
    player_identity_map: dict[str, str],
    names: dict[str, str],
    coach_names: dict[str, str],
    player_ffill: dict[str, dict[str, Any]],
    team_ffill: dict[str, dict[str, Any]],
    coach_ffill: dict[str, dict[str, Any]],
) -> TeamModel:
    """Create a team model by combining many team models."""
    location = None
    players: dict[str, list[PlayerModel]] = {}
    odds: dict[str, list[OddsModel]] = {}
    news: dict[str, NewsModel] = {}
    social: dict[str, SocialModel] = {}
    coaches: dict[str, list[CoachModel]] = {}
    points = None
    ladder_rank = None
    field_goals = None
    lbw = None
    end_dt = None
    for team_model in team_models:
        location = more_interesting(location, team_model.location)
        for player_model in team_model.players:
            player_id = player_model.identifier
            player_name_key = _normalise_name(player_model.name)
            if player_model.identifier in player_identity_map:
                player_id = player_identity_map[player_id]
            elif player_name_key in names:
                player_id = names[player_name_key]
            else:
                names[player_name_key] = player_id
            players[player_id] = players.get(player_id, []) + [player_model]
        for odds_model in team_model.odds:
            key = f"{odds_model.bookie.identifier}-{odds_model.odds}"
            odds[key] = odds.get(key, []) + [odds_model]
        points = more_interesting(points, team_model.points)
        ladder_rank = more_interesting(ladder_rank, team_model.ladder_rank)
        for news_model in team_model.news:
            news_key = "-".join(
                [
                    news_model.title,
                    str(news_model.published),
                    news_model.summary,
                    news_model.source,
                ]
            )
            news[news_key] = news_model
        for social_model in team_model.social:
            social_key = "-".join(
                [social_model.network, social_model.post, str(social_model.published)]
            )
            social[social_key] = social_model
        field_goals = more_interesting(field_goals, team_model.field_goals)
        for coach_model in team_model.coaches:
            coach_id = coach_model.identifier
            coach_name_key = _normalise_name(coach_model.name)
            if coach_name_key in coach_names:
                coach_id = coach_names[coach_name_key]
            else:
                coach_names[coach_name_key] = coach_id
            coaches[coach_id] = coaches.get(coach_id, []) + [coach_model]
        lbw = more_interesting(lbw, team_model.lbw)
        end_dt = more_interesting(end_dt, team_model.end_dt)

    player_list = [
        create_combined_player_model(v, k, player_ffill) for k, v in players.items()
    ]
    player_list.sort(key=functools.cmp_to_key(_compare_player_models))

    team_model = TeamModel(
        identifier=identifier,
        name=team_models[0].name,
        location=location,
        players=player_list,
        odds=[x[0] for x in odds.values()],
        points=points,
        ladder_rank=ladder_rank,
        news=sorted(news.values(), key=lambda x: x.published),
        social=sorted(social.values(), key=lambda x: x.published),
        field_goals=field_goals,
        coaches=[
            create_combined_coach_model(v, k, coach_ffill) for k, v in coaches.items()
        ],
        lbw=lbw,
        end_dt=end_dt,
        version=VERSION,
    )

    ffill(team_ffill, identifier, team_model)

    return team_model
