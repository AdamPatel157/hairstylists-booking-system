from datetime import datetime, timedelta

def cleanup_expired_unverified(db, tblUnverified):
    # Deletes tblUnverified records older than 24 hours from the database
    expiryTime = datetime.now() - timedelta(hours=24)
    expiredRecords = tblUnverified.query.filter(tblUnverified.CodeCreatedAt < expiryTime).all()
    for record in expiredRecords:
        db.session.delete(record)
    db.session.commit()