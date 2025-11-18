from website.database_management import cleanup_expired_unverified as db_cleanup

def cleanup_expired_unverified():
    # Cleans up unverified records older than 30 minutes
    # Called before registration to prevent excessive data volume
    return db_cleanup(expiryMinutes=30)