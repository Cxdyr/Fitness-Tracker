from sqlalchemy import extract
from backend.models import LiftPerformance, db  

def get_tracked_dates(user_id, year, month):
    tracked_dates = db.session.query(LiftPerformance.date_tracked).filter(
        LiftPerformance.user_id == user_id,
        extract('year', LiftPerformance.date_tracked) == year,
        extract('month', LiftPerformance.date_tracked) == month
    ).all()
    return [tracked_date[0] for tracked_date in tracked_dates]