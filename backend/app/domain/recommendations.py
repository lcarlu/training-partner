from statistics import mean

from app.domain.entities import Phase, PhaseInfo, Recommendation, Severity, WellnessDay

_LOW_HRV_STATUSES = {"LOW", "UNBALANCED"}
_RISKY_TRAINING_STATUSES = {"OVERREACHING", "UNPRODUCTIVE", "DETRAINING"}
_LOW_SLEEP_SCORE = 60
_LOW_READINESS = 40
_MIN_DAYS_FOR_TREND = 3


def generate_recommendations(
    phase_info: PhaseInfo,
    recent_wellness: list[WellnessDay],
    weekly_volume_km: list[float],
) -> list[Recommendation]:
    """Pure rule-based suggestions from race phase + recent Garmin wellness/load trends.

    `recent_wellness` should be ordered oldest -> newest, ideally the last 7-14 days.
    `weekly_volume_km` should be ordered oldest -> newest (one entry per week).
    """
    recommendations: list[Recommendation] = []

    recommendations.append(_phase_banner(phase_info))

    if len(recent_wellness) >= _MIN_DAYS_FOR_TREND:
        recommendations.extend(_wellness_recommendations(recent_wellness))

    if len(weekly_volume_km) >= 2:
        recommendations.extend(_volume_recommendations(phase_info, weekly_volume_km))

    return recommendations


def _phase_banner(phase_info: PhaseInfo) -> Recommendation:
    labels = {
        Phase.BASE: "Phase Base",
        Phase.BUILD: "Phase Développement",
        Phase.PEAK: "Phase Spécifique",
        Phase.TAPER: "Affûtage",
        Phase.RACE_WEEK: "Semaine de course",
        Phase.POST: "Post-course",
    }
    weeks = phase_info.weeks_to_race
    if phase_info.phase == Phase.POST:
        detail = "La date de course est passée."
    else:
        detail = f"Encore {weeks:g} semaines avant le {phase_info.race_date.isoformat()}."
    return Recommendation(severity=Severity.INFO, title=labels[phase_info.phase], detail=detail)


def _wellness_recommendations(days: list[WellnessDay]) -> list[Recommendation]:
    out: list[Recommendation] = []

    statuses = [d.training_status for d in days if d.training_status]
    if statuses and statuses[-1] in _RISKY_TRAINING_STATUSES:
        out.append(
            Recommendation(
                severity=Severity.WARNING,
                title=f"Training status Garmin : {statuses[-1].title()}",
                detail="Envisage une séance allégée ou un jour de repos supplémentaire.",
            )
        )

    hrv_statuses = [d.hrv_status for d in days if d.hrv_status]
    if hrv_statuses and hrv_statuses[-1] in _LOW_HRV_STATUSES:
        out.append(
            Recommendation(
                severity=Severity.WARNING,
                title=f"HRV {hrv_statuses[-1].title()}",
                detail=(
                    "Ta variabilité de fréquence cardiaque est basse : privilégie la récupération."
                ),
            )
        )

    sleep_scores = [d.sleep_score for d in days if d.sleep_score is not None]
    if sleep_scores and mean(sleep_scores) < _LOW_SLEEP_SCORE:
        out.append(
            Recommendation(
                severity=Severity.WARNING,
                title="Sommeil en dessous de la cible",
                detail=(
                    f"Score de sommeil moyen de {mean(sleep_scores):.0f}/100 sur "
                    f"{len(sleep_scores)} jours : ça vaut le coup de soigner le coucher."
                ),
            )
        )

    readiness_scores = [
        d.training_readiness_score for d in days if d.training_readiness_score is not None
    ]
    if readiness_scores and readiness_scores[-1] < _LOW_READINESS:
        out.append(
            Recommendation(
                severity=Severity.ALERT,
                title="Training readiness bas",
                detail=(
                    f"Readiness à {readiness_scores[-1]}/100 aujourd'hui : "
                    "repos ou séance très facile recommandés."
                ),
            )
        )

    return out


def _volume_recommendations(
    phase_info: PhaseInfo, weekly_volume_km: list[float]
) -> list[Recommendation]:
    out: list[Recommendation] = []
    last, previous = weekly_volume_km[-1], weekly_volume_km[-2]

    if previous > 0:
        change_pct = (last - previous) / previous * 100
        if change_pct > 30:
            out.append(
                Recommendation(
                    severity=Severity.WARNING,
                    title="Hausse de volume rapide",
                    detail=(
                        f"Volume en hausse de {change_pct:.0f}% par rapport à la semaine "
                        "précédente : au-delà de +10%/semaine, le risque de blessure augmente."
                    ),
                )
            )

    if phase_info.phase == Phase.BASE and last <= previous:
        out.append(
            Recommendation(
                severity=Severity.INFO,
                title="Phase Base : construire le volume",
                detail=(
                    "Encore beaucoup de semaines avant la course, profites-en pour augmenter "
                    "progressivement le volume."
                ),
            )
        )

    return out
